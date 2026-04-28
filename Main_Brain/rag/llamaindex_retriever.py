"""
LlamaIndex-based Retrieval System for Multi-Agent Chatbot Copilot
Creates LlamaIndex documents from existing pgvector embeddings for superior retrieval
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import numpy as np
from llama_index.core import VectorStoreIndex, ServiceContext, Settings, Document
from llama_index.core.schema import TextNode, NodeWithScore
from llama_index.core.vector_stores import VectorStoreQuery, VectorStoreQueryResult
from llama_index.core.vector_stores.types import VectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import ResponseMode, get_response_synthesizer
from llama_index.core.prompts import PromptTemplate
from llama_index.core.postprocessor import SimilarityPostprocessor
from database.connection import db_manager
from database.models import RAGDocument
from config import settings

logger = logging.getLogger(__name__)

class CustomPGVectorStore(VectorStore):
    """Custom vector store that works with existing rag_embeddings table"""
    
    def __init__(self):
        self.stores_text = True
        self.is_embedding_query = True
    
    async def aquery(self, query: VectorStoreQuery, **kwargs) -> VectorStoreQueryResult:
        """Async query method for vector similarity search"""
        try:
            # Convert query embedding to string format for PostgreSQL
            query_vector = "[" + ",".join(map(str, query.query_embedding)) + "]"
            
            # Build the SQL query
            sql_query = """
                SELECT 
                    doc_id, source_file, data_type, business_context,
                    customer_name, state, formatted_period, project_phase,
                    fiscalyear, ryear, business_module, wtg_model, wtg_type,
                    capacity, model_bucket, wtg_count, mwg,
                    wtg_count_deviation, mwg_deviation, content,
                    1 - (embedding <=> $1::vector) as similarity_score
                FROM rag_embeddings
                WHERE 1 - (embedding <=> $1::vector) >= $2
                ORDER BY embedding <=> $1::vector
                LIMIT $3
            """
            
            # Execute query
            async with db_manager.get_connection() as conn:
                similarity_threshold = 0.1  # Lower threshold for testing
                limit = query.similarity_top_k or 10
                
                results = await conn.fetch(
                    sql_query, 
                    query_vector, 
                    similarity_threshold,
                    limit
                )
            
            # Convert results to LlamaIndex format
            nodes = []
            similarities = []
            ids = []
            
            for row in results:
                # Create metadata dictionary
                metadata = {
                    'doc_id': row['doc_id'],
                    'source_file': row['source_file'],
                    'data_type': row['data_type'],
                    'business_context': row['business_context'],
                    'customer_name': row['customer_name'],
                    'state': row['state'],
                    'formatted_period': row['formatted_period'],
                    'project_phase': row['project_phase'],
                    'fiscalyear': row['fiscalyear'],
                    'ryear': row['ryear'],
                    'business_module': row['business_module'],
                    'wtg_model': row['wtg_model'],
                    'wtg_type': row['wtg_type'],
                    'capacity': row['capacity'],
                    'model_bucket': row['model_bucket'],
                    'wtg_count': row['wtg_count'],
                    'mwg': row['mwg'],
                    'wtg_count_deviation': row['wtg_count_deviation'],
                    'mwg_deviation': row['mwg_deviation']
                }
                
                # Create TextNode
                node = TextNode(
                    text=row['content'],
                    metadata=metadata,
                    id_=str(row['doc_id'])
                )
                
                nodes.append(node)
                similarities.append(row['similarity_score'])
                ids.append(str(row['doc_id']))
            
            return VectorStoreQueryResult(
                nodes=nodes,
                similarities=similarities,
                ids=ids
            )
            
        except Exception as e:
            logger.error(f"Vector store query failed: {e}")
            return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])
    
    def query(self, query: VectorStoreQuery, **kwargs) -> VectorStoreQueryResult:
        """Sync query method - calls async version"""
        return asyncio.run(self.aquery(query, **kwargs))
    
    def add(self, nodes: List[TextNode], **kwargs) -> List[str]:
        """Add nodes - not implemented for read-only store"""
        raise NotImplementedError("This vector store is read-only")
    
    def delete(self, ref_doc_id: str, **kwargs) -> None:
        """Delete nodes - not implemented for read-only store"""
        raise NotImplementedError("This vector store is read-only")

class LlamaIndexRetriever:
    """LlamaIndex-based retrieval system using existing pgvector embeddings"""
    
    def __init__(self):
        self.embedding_model: Optional[HuggingFaceEmbedding] = None
        self.vector_store: Optional[CustomPGVectorStore] = None
        self.index: Optional[VectorStoreIndex] = None
        self.retriever: Optional[VectorIndexRetriever] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the LlamaIndex retrieval system"""
        try:
            logger.info("Initializing LlamaIndex retrieval system...")
            
            # Initialize embedding model
            self.embedding_model = HuggingFaceEmbedding(
                model_name=settings.rag.embedding_model,
                max_length=512
            )
            
            # Set global embedding model
            Settings.embed_model = self.embedding_model
            Settings.chunk_size = 1024
            Settings.chunk_overlap = 20
            
            # Initialize custom vector store
            self.vector_store = CustomPGVectorStore()
            
            # Create index from vector store
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store
            )
            
            # Create retriever
            self.retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=settings.rag.max_retrieval_docs
            )
            
            self._initialized = True
            logger.info("LlamaIndex retrieval system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex retrieval system: {e}")
            raise
    
    def _ensure_initialized(self) -> None:
        """Ensure the system is initialized"""
        if not self._initialized:
            raise RuntimeError("LlamaIndex retrieval system not initialized. Call initialize() first.")
    
    async def retrieve_documents(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[RAGDocument]:
        """
        Retrieve relevant documents using LlamaIndex
        
        Args:
            query: Search query text
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of RAGDocument objects
        """
        self._ensure_initialized()
        
        if top_k is None:
            top_k = settings.rag.max_retrieval_docs
        
        try:
            # Update retriever parameters
            self.retriever.similarity_top_k = top_k
            
            # Retrieve nodes
            nodes_with_scores = await self.retriever.aretrieve(query)
            
            # Convert to RAGDocument objects
            documents = []
            for node_with_score in nodes_with_scores:
                if hasattr(node_with_score, 'node') and hasattr(node_with_score.node, 'metadata'):
                    metadata = node_with_score.node.metadata
                    
                    # Apply similarity threshold if specified
                    score = getattr(node_with_score, 'score', 0.0)
                    if similarity_threshold and score < similarity_threshold:
                        continue
                    
                    # Create RAGDocument
                    doc = RAGDocument(
                        doc_id=metadata.get('doc_id', 0),
                        source_file=metadata.get('source_file'),
                        data_type=metadata.get('data_type'),
                        business_context=metadata.get('business_context'),
                        customer_name=metadata.get('customer_name'),
                        state=metadata.get('state'),
                        formatted_period=metadata.get('formatted_period'),
                        project_phase=metadata.get('project_phase'),
                        fiscalyear=metadata.get('fiscalyear'),
                        ryear=metadata.get('ryear'),
                        business_module=metadata.get('business_module'),
                        wtg_model=metadata.get('wtg_model'),
                        wtg_type=metadata.get('wtg_type'),
                        capacity=metadata.get('capacity'),
                        model_bucket=metadata.get('model_bucket'),
                        wtg_count=metadata.get('wtg_count'),
                        mwg=metadata.get('mwg'),
                        wtg_count_deviation=metadata.get('wtg_count_deviation'),
                        mwg_deviation=metadata.get('mwg_deviation'),
                        content=node_with_score.node.text,
                        similarity_score=score
                    )
                    documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents for query: {query[:100]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            return []
    
    async def retrieve_with_filters(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> List[RAGDocument]:
        """
        Retrieve documents with metadata filters
        
        Args:
            query: Search query
            filters: Metadata filters (fiscal_year, state, business_module, etc.)
            top_k: Number of documents to retrieve
            
        Returns:
            List of filtered RAGDocument objects
        """
        # First retrieve documents
        documents = await self.retrieve_documents(query, top_k)
        
        # Apply filters if provided
        if filters:
            filtered_docs = []
            for doc in documents:
                match = True
                
                for key, value in filters.items():
                    doc_value = getattr(doc, key, None)
                    if key == 'customer_name' and value:
                        # Partial match for customer names
                        if not doc_value or value.lower() not in doc_value.lower():
                            match = False
                            break
                    elif doc_value != value:
                        match = False
                        break
                
                if match:
                    filtered_docs.append(doc)
            
            return filtered_docs
        
        return documents
    
    async def get_context_for_query(
        self, 
        query: str, 
        max_context_length: int = 4000
    ) -> Tuple[str, List[RAGDocument]]:
        """
        Get formatted context string for LLM queries
        
        Args:
            query: Search query
            max_context_length: Maximum context length in characters
            
        Returns:
            Tuple of (formatted_context, source_documents)
        """
        documents = await self.retrieve_documents(query)
        
        if not documents:
            return "No relevant information found in the database.", []
        
        # Format context
        context_parts = []
        current_length = 0
        used_docs = []
        
        for doc in documents:
            # Create document summary
            doc_summary = f"""
Document {doc.doc_id}:
Customer: {doc.customer_name}
State: {doc.state}
Business Module: {doc.business_module}
Capacity: {doc.capacity} MW
Content: {doc.content[:300]}...
Similarity: {doc.similarity_score:.3f}
---
"""
            
            if current_length + len(doc_summary) > max_context_length:
                break
            
            context_parts.append(doc_summary)
            current_length += len(doc_summary)
            used_docs.append(doc)
        
        formatted_context = "\n".join(context_parts)
        return formatted_context, used_docs
    
    async def search_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        limit: int = 10
    ) -> List[RAGDocument]:
        """
        Search documents by metadata only (no semantic search)
        
        Args:
            metadata_filters: Dictionary of metadata filters
            limit: Maximum number of results
            
        Returns:
            List of RAGDocument objects
        """
        try:
            # Build dynamic query
            conditions = []
            params = []
            param_count = 0
            
            for key, value in metadata_filters.items():
                if value is not None:
                    param_count += 1
                    if key == 'customer_name':
                        conditions.append(f"customer_name ILIKE ${param_count}")
                        params.append(f"%{value}%")
                    else:
                        conditions.append(f"{key} = ${param_count}")
                        params.append(value)
            
            param_count += 1
            params.append(limit)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            query = f"""
                SELECT 
                    doc_id, source_file, data_type, business_context,
                    customer_name, state, formatted_period, project_phase,
                    fiscalyear, ryear, business_module, wtg_model, wtg_type,
                    capacity, model_bucket, wtg_count, mwg,
                    wtg_count_deviation, mwg_deviation, content
                FROM rag_embeddings
                WHERE {where_clause}
                ORDER BY doc_id
                LIMIT ${param_count}
            """
            
            async with db_manager.get_connection() as conn:
                results = await conn.fetch(query, *params)
            
            # Convert to RAGDocument objects
            documents = []
            for row in results:
                doc = RAGDocument(**dict(row), similarity_score=None)
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Metadata search failed: {e}")
            return []

# Global LlamaIndex retriever instance
llamaindex_retriever = LlamaIndexRetriever()