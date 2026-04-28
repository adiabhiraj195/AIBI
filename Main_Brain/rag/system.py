"""
RAG (Retrieval Augmented Generation) System
Interfaces with existing pgvector embeddings for contextual data retrieval
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from database.connection import db_manager
from database.models import RAGDocument
from config import settings

logger = logging.getLogger(__name__)

class RAGSystem:
    """Main RAG system for document retrieval and search"""
    
    def __init__(self):
        self.embedding_model: Optional[SentenceTransformer] = None
        self._model_loaded = False
    
    async def initialize(self) -> None:
        """Initialize the RAG system and load embedding model"""
        try:
            # Load embedding model
            logger.info(f"Loading embedding model: {settings.rag.embedding_model}")
            self.embedding_model = SentenceTransformer(settings.rag.embedding_model)
            self._model_loaded = True
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise
    
    def _ensure_model_loaded(self) -> None:
        """Ensure embedding model is loaded"""
        if not self._model_loaded or self.embedding_model is None:
            raise RuntimeError("RAG system not initialized. Call initialize() first.")
    
    async def semantic_search(
        self, 
        query: str, 
        limit: int = None,
        similarity_threshold: float = None
    ) -> List[RAGDocument]:
        """
        Perform semantic search using vector similarity
        
        Args:
            query: Search query text
            limit: Maximum number of results (default from settings)
            similarity_threshold: Minimum similarity score (default from settings)
            
        Returns:
            List of RAGDocument objects with similarity scores
        """
        self._ensure_model_loaded()
        
        if limit is None:
            limit = settings.rag.max_retrieval_docs
        if similarity_threshold is None:
            similarity_threshold = settings.rag.similarity_threshold
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
            # Convert to string format for asyncpg
            query_vector = "[" + ",".join(map(str, query_embedding.tolist())) + "]"
            
            # Perform vector search
            async with db_manager.get_connection() as conn:
                results = await conn.fetch("""
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
                """, query_vector, similarity_threshold, limit)
            
            # Convert to RAGDocument objects
            documents = []
            for row in results:
                doc = RAGDocument(**dict(row))
                documents.append(doc)
            
            logger.info(f"Semantic search returned {len(documents)} documents for query: {query[:100]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            raise
    
    async def metadata_filter(
        self,
        fiscal_year: Optional[str] = None,
        state: Optional[str] = None,
        business_module: Optional[str] = None,
        customer_name: Optional[str] = None,
        project_phase: Optional[str] = None,
        limit: int = None
    ) -> List[RAGDocument]:
        """
        Filter documents by metadata criteria
        
        Args:
            fiscal_year: Filter by fiscal year
            state: Filter by state
            business_module: Filter by business module
            customer_name: Filter by customer name
            project_phase: Filter by project phase
            limit: Maximum number of results
            
        Returns:
            List of RAGDocument objects
        """
        if limit is None:
            limit = settings.rag.max_retrieval_docs
        
        try:
            # Build dynamic query
            conditions = []
            params = []
            param_count = 0
            
            if fiscal_year:
                param_count += 1
                conditions.append(f"fiscalyear = ${param_count}")
                params.append(fiscal_year)
            
            if state:
                param_count += 1
                conditions.append(f"state = ${param_count}")
                params.append(state)
            
            if business_module:
                param_count += 1
                conditions.append(f"business_module = ${param_count}")
                params.append(business_module)
            
            if customer_name:
                param_count += 1
                conditions.append(f"customer_name ILIKE ${param_count}")
                params.append(f"%{customer_name}%")
            
            if project_phase:
                param_count += 1
                conditions.append(f"project_phase = ${param_count}")
                params.append(project_phase)
            
            # Add limit parameter
            param_count += 1
            params.append(limit)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            query = f"""
                SELECT 
                    doc_id, source_file, data_type, business_context,
                    customer_name, state, formatted_period, project_phase,
                    fiscalyear, ryear, business_module, wtg_model, wtg_type,
                    capacity, model_bucket, wtg_count, mwg,
                    wtg_count_deviation, mwg_deviation, content,
                    NULL as similarity_score
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
                doc = RAGDocument(**dict(row))
                documents.append(doc)
            
            logger.info(f"Metadata filter returned {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Metadata filtering failed: {e}")
            raise
    
    async def hybrid_search(
        self,
        query: str,
        keywords: List[str],
        fiscal_year: Optional[str] = None,
        state: Optional[str] = None,
        business_module: Optional[str] = None,
        limit: int = None,
        similarity_threshold: float = None
    ) -> List[RAGDocument]:
        """
        Combine semantic search with keyword matching and metadata filtering
        
        Args:
            query: Semantic search query
            keywords: Keywords for text matching
            fiscal_year: Filter by fiscal year
            state: Filter by state
            business_module: Filter by business module
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of RAGDocument objects with combined scoring
        """
        self._ensure_model_loaded()
        
        if limit is None:
            limit = settings.rag.max_retrieval_docs
        if similarity_threshold is None:
            similarity_threshold = settings.rag.similarity_threshold
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
            # Convert to string format for asyncpg
            query_vector = "[" + ",".join(map(str, query_embedding.tolist())) + "]"
            
            # Build keyword search conditions
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(f"content ILIKE '%{keyword}%'")
            
            keyword_clause = " OR ".join(keyword_conditions) if keyword_conditions else "TRUE"
            
            # Build metadata conditions
            metadata_conditions = []
            params = [query_vector, similarity_threshold]
            param_count = 2
            
            if fiscal_year:
                param_count += 1
                metadata_conditions.append(f"fiscalyear = ${param_count}")
                params.append(fiscal_year)
            
            if state:
                param_count += 1
                metadata_conditions.append(f"state = ${param_count}")
                params.append(state)
            
            if business_module:
                param_count += 1
                metadata_conditions.append(f"business_module = ${param_count}")
                params.append(business_module)
            
            # Add limit parameter
            param_count += 1
            params.append(limit)
            
            metadata_clause = " AND ".join(metadata_conditions) if metadata_conditions else "TRUE"
            
            query_sql = f"""
                SELECT 
                    doc_id, source_file, data_type, business_context,
                    customer_name, state, formatted_period, project_phase,
                    fiscalyear, ryear, business_module, wtg_model, wtg_type,
                    capacity, model_bucket, wtg_count, mwg,
                    wtg_count_deviation, mwg_deviation, content,
                    (1 - (embedding <=> $1::vector)) as similarity_score
                FROM rag_embeddings
                WHERE 
                    (1 - (embedding <=> $1::vector)) >= $2
                    AND ({keyword_clause})
                    AND ({metadata_clause})
                ORDER BY 
                    (1 - (embedding <=> $1::vector)) DESC,
                    doc_id
                LIMIT ${param_count}
            """
            
            async with db_manager.get_connection() as conn:
                results = await conn.fetch(query_sql, *params)
            
            # Convert to RAGDocument objects
            documents = []
            for row in results:
                doc = RAGDocument(**dict(row))
                documents.append(doc)
            
            logger.info(f"Hybrid search returned {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise
    
    async def get_document_by_id(self, doc_id: int) -> Optional[RAGDocument]:
        """
        Retrieve a specific document by ID
        
        Args:
            doc_id: Document identifier
            
        Returns:
            RAGDocument object or None if not found
        """
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.fetchrow("""
                    SELECT 
                        doc_id, source_file, data_type, business_context,
                        customer_name, state, formatted_period, project_phase,
                        fiscalyear, ryear, business_module, wtg_model, wtg_type,
                        capacity, model_bucket, wtg_count, mwg,
                        wtg_count_deviation, mwg_deviation, content,
                        NULL as similarity_score
                    FROM rag_embeddings
                    WHERE doc_id = $1
                """, doc_id)
            
            if result:
                return RAGDocument(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document by ID {doc_id}: {e}")
            raise
    
    async def get_similar_documents(
        self, 
        doc_id: int, 
        limit: int = 5,
        similarity_threshold: float = None
    ) -> List[RAGDocument]:
        """
        Find documents similar to a given document
        
        Args:
            doc_id: Reference document ID
            limit: Maximum number of similar documents
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar RAGDocument objects
        """
        if similarity_threshold is None:
            similarity_threshold = settings.rag.similarity_threshold
        
        try:
            async with db_manager.get_connection() as conn:
                # Get the reference document's embedding
                ref_embedding = await conn.fetchval(
                    "SELECT embedding FROM rag_embeddings WHERE doc_id = $1", 
                    doc_id
                )
                
                if not ref_embedding:
                    return []
                
                # Find similar documents
                results = await conn.fetch("""
                    SELECT 
                        doc_id, source_file, data_type, business_context,
                        customer_name, state, formatted_period, project_phase,
                        fiscalyear, ryear, business_module, wtg_model, wtg_type,
                        capacity, model_bucket, wtg_count, mwg,
                        wtg_count_deviation, mwg_deviation, content,
                        1 - (embedding <=> $1::vector) as similarity_score
                    FROM rag_embeddings
                    WHERE 
                        doc_id != $2
                        AND 1 - (embedding <=> $1::vector) >= $3
                    ORDER BY embedding <=> $1::vector
                    LIMIT $4
                """, ref_embedding, doc_id, similarity_threshold, limit)
            
            # Convert to RAGDocument objects
            documents = []
            for row in results:
                doc = RAGDocument(**dict(row))
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to find similar documents for {doc_id}: {e}")
            raise
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial query
        
        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        try:
            async with db_manager.get_connection() as conn:
                # Get unique terms from content that match partial query
                results = await conn.fetch("""
                    SELECT DISTINCT 
                        CASE 
                            WHEN customer_name ILIKE $1 THEN customer_name
                            WHEN state ILIKE $1 THEN state
                            WHEN business_module ILIKE $1 THEN business_module
                            WHEN wtg_model ILIKE $1 THEN wtg_model
                            WHEN project_phase ILIKE $1 THEN project_phase
                        END as suggestion
                    FROM rag_embeddings
                    WHERE 
                        customer_name ILIKE $1 
                        OR state ILIKE $1
                        OR business_module ILIKE $1
                        OR wtg_model ILIKE $1
                        OR project_phase ILIKE $1
                    LIMIT $2
                """, f"%{partial_query}%", limit)
            
            suggestions = [row['suggestion'] for row in results if row['suggestion']]
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get search suggestions: {e}")
            return []

# Global RAG system instance
rag_system = RAGSystem()