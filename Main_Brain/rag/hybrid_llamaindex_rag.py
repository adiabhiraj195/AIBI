"""
Hybrid LlamaIndex RAG System for Multi-Agent Chatbot Copilot
Uses existing RAG system for retrieval + LlamaIndex for response generation
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from llama_index.core import Document, VectorStoreIndex, ServiceContext, Settings
from llama_index.core.schema import TextNode, NodeWithScore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.prompts import PromptTemplate
import httpx
from database.models import RAGDocument
from rag.system import rag_system
from rag.statistical_queries import statistical_handler
from rag.nl2sql_agent import nl2sql_agent
from config import settings

logger = logging.getLogger(__name__)

class OpenRouterLLM(CustomLLM):
    """Custom LLM wrapper for OpenRouter API compatibility with LlamaIndex"""
    
    model_name: str
    api_key: str
    base_url: str
    temperature: float = 0.1
    max_tokens: int = 2000
    
    class Config:
        protected_namespaces = ()
    
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=4096,
            num_output=self.max_tokens,
            model_name=self.model_name,
        )
    
    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Complete a prompt using OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    return CompletionResponse(text=content)
                else:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return CompletionResponse(text="I don't have sufficient data to answer this question based on the available wind turbine project information.")
                    
        except Exception as e:
            logger.error(f"OpenRouter LLM completion failed: {e}")
            return CompletionResponse(text="I don't have sufficient data to answer this question based on the available wind turbine project information.")
    
    @llm_completion_callback()
    async def acomplete(self, prompt: str, **kwargs) -> CompletionResponse:
        """Async complete"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    return CompletionResponse(text=content)
                else:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return CompletionResponse(text="I don't have sufficient data to answer this question based on the available wind turbine project information.")
                    
        except Exception as e:
            logger.error(f"OpenRouter LLM async completion failed: {e}")
            return CompletionResponse(text="I don't have sufficient data to answer this question based on the available wind turbine project information.")
    
    def stream_complete(self, prompt: str, **kwargs):
        """Stream complete - not implemented for OpenRouter"""
        response = self.complete(prompt, **kwargs)
        yield response
    
    async def astream_complete(self, prompt: str, **kwargs):
        """Async stream complete - not implemented for OpenRouter"""
        response = await self.acomplete(prompt, **kwargs)
        yield response

class HybridLlamaIndexRAG:
    """Hybrid RAG system using existing retrieval + LlamaIndex response generation"""
    
    def __init__(self):
        self.llm = None
        self.response_synthesizer = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the hybrid RAG system"""
        try:
            logger.info("Initializing Hybrid LlamaIndex RAG system...")
            
            # Initialize existing RAG system for retrieval
            await rag_system.initialize()
            
            # Initialize LLM with OpenRouter compatibility
            self.llm = OpenRouterLLM(
                model_name=settings.llm.model,
                api_key=settings.llm.api_key,
                base_url=settings.llm.base_url,
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens
            )
            
            # Configure global settings
            Settings.llm = self.llm
            
            # Create custom prompt template for wind turbine domain
            qa_prompt_template = PromptTemplate(
                """You are a specialized AI assistant for AIBI's wind turbine project data analysis. 
                You have access to comprehensive project data including capacity, customer information, 
                business modules, states, project phases, and financial metrics.

                Context information is below:
                ---------------------
                {context_str}
                ---------------------

                Instructions:
                1. Answer ONLY based on the provided context data
                2. If the information is not in the context, clearly state "I don't have sufficient data to answer this question"
                3. Provide specific numbers, metrics, and details when available
                4. Translate technical terms to business language:
                   - MWG = Megawatt Generation Capacity
                   - WTG = Wind Turbine Generator
                   - Capacity deviations = Budget variance analysis
                5. Include relevant context like customer names, states, business modules when applicable
                6. For financial questions, focus on capacity, deviations, and business impact
                7. Be concise but comprehensive in your analysis
                8. Always provide actionable insights when possible

                Question: {query_str}
                
                Answer: """
            )
            
            # Initialize response synthesizer with custom prompt
            self.response_synthesizer = get_response_synthesizer(
                llm=self.llm,
                text_qa_template=qa_prompt_template,
                response_mode="simple_summarize"  # More efficient, single API call
            )
            
            self._initialized = True
            logger.info("Hybrid LlamaIndex RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hybrid LlamaIndex RAG system: {e}")
            raise
    
    def _ensure_initialized(self) -> None:
        """Ensure the system is initialized"""
        if not self._initialized:
            raise RuntimeError("Hybrid LlamaIndex RAG system not initialized. Call initialize() first.")
    
    async def query(
        self, 
        question: str,
        filters: Optional[Dict[str, Any]] = None,
        max_docs: int = None
    ) -> Dict[str, Any]:
        """
        Query the hybrid RAG system with natural language
        
        Args:
            question: Natural language question
            filters: Optional metadata filters
            max_docs: Number of documents to retrieve
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        self._ensure_initialized()
        
        try:
            # First, check if this is a statistical query
            statistical_result = await statistical_handler.handle_statistical_query(question)
            
            if statistical_result and statistical_result.get('success'):
                # Return statistical result with proper formatting
                return {
                    'answer': statistical_result['answer'],
                    'source_count': statistical_result.get('total_customers', 0) or statistical_result.get('project_count', 0),
                    'confidence': statistical_result['confidence'],
                    'query': question,
                    'has_sufficient_data': True,
                    'query_type': 'statistical',
                    'statistical_data': statistical_result
                }
            
            # Second, try NL2SQL for complex semantic queries
            nl2sql_result = await nl2sql_agent.process_natural_query(question)
            
            if nl2sql_result and nl2sql_result.get('success'):
                # Return NL2SQL result with proper formatting
                return {
                    'answer': nl2sql_result['answer'],
                    'source_count': nl2sql_result.get('row_count', 0),
                    'confidence': nl2sql_result['confidence'],
                    'query': question,
                    'has_sufficient_data': True,
                    'query_type': 'nl2sql',
                    'sql_query': nl2sql_result.get('sql_query'),
                    'data_sample': nl2sql_result.get('data_sample', [])
                }
            
            # Use existing RAG system for retrieval
            if max_docs is None:
                max_docs = min(50, settings.rag.max_retrieval_docs)  # Limit to 50 for LLM processing
            
            # Perform semantic search using existing system
            documents = await rag_system.semantic_search(
                query=question,
                limit=max_docs,
                similarity_threshold=0.3  # Lower threshold for better recall
            )
            
            if not documents:
                return {
                    'answer': "I don't have sufficient data to answer this question based on the available wind turbine project information.",
                    'sources': [],
                    'source_count': 0,
                    'query': question,
                    'has_sufficient_data': False,
                    'confidence': 0.0
                }
            
            # Convert RAGDocuments to LlamaIndex TextNodes
            nodes = []
            source_documents = []
            
            for doc in documents:
                # Create metadata dict
                metadata = {
                    'doc_id': doc.doc_id,
                    'customer_name': doc.customer_name,
                    'state': doc.state,
                    'business_module': doc.business_module,
                    'capacity': doc.capacity,
                    'wtg_model': doc.wtg_model,
                    'project_phase': doc.project_phase,
                    'fiscalyear': doc.fiscalyear,
                    'similarity_score': doc.similarity_score
                }
                
                # Create TextNode for LlamaIndex
                node = TextNode(
                    text=doc.content,
                    metadata=metadata
                )
                
                # Create NodeWithScore
                node_with_score = NodeWithScore(
                    node=node,
                    score=doc.similarity_score if doc.similarity_score else 0.5
                )
                nodes.append(node_with_score)
                
                # Prepare source info
                source_documents.append({
                    'doc_id': doc.doc_id,
                    'customer_name': doc.customer_name,
                    'state': doc.state,
                    'business_module': doc.business_module,
                    'capacity': doc.capacity,
                    'similarity_score': doc.similarity_score,
                    'content_preview': doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                })
            
            # Generate response using LlamaIndex synthesizer
            response = await self.response_synthesizer.asynthesize(
                query=question,
                nodes=nodes
            )
            
            # Calculate confidence based on sources and response quality
            confidence = self._calculate_confidence(str(response), source_documents)
            has_sufficient_data = self._check_data_sufficiency(str(response))
            
            return {
                'answer': str(response),
                'sources': source_documents,
                'source_count': len(source_documents),
                'query': question,
                'has_sufficient_data': has_sufficient_data,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                'answer': "I encountered an error while processing your question. Please try again.",
                'sources': [],
                'source_count': 0,
                'query': question,
                'has_sufficient_data': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _check_data_sufficiency(self, response: str) -> bool:
        """Check if the response indicates sufficient data was found"""
        insufficient_indicators = [
            "don't have sufficient data",
            "not enough information",
            "cannot find",
            "no data available",
            "insufficient context",
            "unable to answer",
            "not provided in the context"
        ]
        return not any(indicator in response.lower() for indicator in insufficient_indicators)
    
    def _calculate_confidence(self, response: str, source_documents: List[Dict]) -> float:
        """Calculate confidence score based on response and sources"""
        if not source_documents:
            return 0.0
        
        # Base confidence on number and quality of sources
        num_sources = len(source_documents)
        avg_similarity = sum(doc.get('similarity_score', 0) for doc in source_documents) / num_sources
        
        # Check if response indicates insufficient data
        if not self._check_data_sufficiency(response):
            return 0.1
        
        # Confidence factors
        source_factor = min(num_sources / 5.0, 1.0)  # Normalize to max 5 sources
        similarity_factor = avg_similarity if avg_similarity else 0.5
        
        # Response quality factor (longer, more detailed responses get higher confidence)
        response_length_factor = min(len(response) / 500.0, 1.0)
        
        return (source_factor * 0.3 + similarity_factor * 0.5 + response_length_factor * 0.2)
    
    async def ask_question(
        self,
        question: str,
        context_filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Simple question-answering interface
        
        Args:
            question: Natural language question
            context_filters: Optional filters for context
            
        Returns:
            String response
        """
        result = await self.query(question, filters=context_filters)
        return result['answer']
    
    async def get_business_insights(
        self,
        query: str,
        focus_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get business-focused insights with CFO-grade analysis
        
        Args:
            query: Business question
            focus_area: Optional focus (financial, operational, strategic)
            
        Returns:
            Structured business insights
        """
        # Enhance query for business context
        business_query = f"""
        Provide a comprehensive business analysis for: {query}
        
        Focus on:
        - Key financial metrics and capacity data
        - Business impact and implications  
        - Risk factors and deviations
        - Actionable recommendations
        - State and customer distribution insights
        - Trends and patterns in the data
        
        Format the response as a detailed executive summary with specific numbers and insights.
        """
        
        result = await self.query(business_query, max_docs=15)  # Get more context for business insights
        
        # Parse response for structured insights
        insights = {
            'executive_summary': result['answer'],
            'key_metrics': self._extract_metrics(result['sources']),
            'risk_factors': self._identify_risks(result['sources']),
            'recommendations': self._generate_recommendations(result['answer']),
            'data_confidence': result['confidence'],
            'source_count': len(result['sources']),
            'has_sufficient_data': result['has_sufficient_data']
        }
        
        return insights
    
    def _extract_metrics(self, sources: List[Dict]) -> List[Dict[str, Any]]:
        """Extract key metrics from source documents"""
        metrics = []
        total_capacity = 0
        customer_count = set()
        state_count = set()
        business_modules = set()
        
        for source in sources:
            if source.get('capacity'):
                total_capacity += source['capacity']
            if source.get('customer_name'):
                customer_count.add(source['customer_name'])
            if source.get('state'):
                state_count.add(source['state'])
            if source.get('business_module'):
                business_modules.add(source['business_module'])
        
        if sources:
            metrics = [
                {'name': 'Total Capacity', 'value': f"{total_capacity:.2f} MW", 'type': 'capacity'},
                {'name': 'Customers Involved', 'value': len(customer_count), 'type': 'count'},
                {'name': 'States Covered', 'value': len(state_count), 'type': 'count'},
                {'name': 'Business Modules', 'value': len(business_modules), 'type': 'count'},
                {'name': 'Data Points', 'value': len(sources), 'type': 'count'}
            ]
        
        return metrics
    
    def _identify_risks(self, sources: List[Dict]) -> List[str]:
        """Identify risk factors from source data"""
        risks = []
        
        # Analyze capacity concentration
        if sources:
            capacities = [s.get('capacity', 0) for s in sources if s.get('capacity')]
            if capacities:
                max_capacity = max(capacities)
                total_capacity = sum(capacities)
                if max_capacity > total_capacity * 0.3:
                    risks.append("High capacity concentration in single project")
        
        # Check customer concentration
        customers = set(s.get('customer_name') for s in sources if s.get('customer_name'))
        if len(customers) < 3 and len(sources) > 5:
            risks.append("Limited customer diversification")
        
        return risks
    
    def _generate_recommendations(self, response: str) -> List[str]:
        """Generate actionable recommendations from response"""
        recommendations = []
        
        # Extract recommendation-like sentences from response
        sentences = response.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(word in sentence.lower() for word in ['should', 'recommend', 'suggest', 'consider', 'need to', 'must']):
                if len(sentence) > 20:  # Filter out very short sentences
                    recommendations.append(sentence)
        
        return recommendations[:4]  # Limit to top 4

# Global hybrid RAG system instance
hybrid_rag = HybridLlamaIndexRAG()