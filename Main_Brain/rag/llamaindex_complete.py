"""
Complete LlamaIndex RAG System for Multi-Agent Chatbot Copilot
Combines LlamaIndex retrieval with custom LLM for superior question answering
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import httpx
from llama_index.core import Settings
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.prompts import PromptTemplate
from llama_index.core.schema import QueryBundle
from llama_index.core.base.response.schema import Response
from rag.llamaindex_retriever import LlamaIndexRetriever, llamaindex_retriever
from database.models import RAGDocument
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
                    return CompletionResponse(text="I don't have sufficient data to answer this question based on the available information.")
                    
        except Exception as e:
            logger.error(f"OpenRouter LLM completion failed: {e}")
            return CompletionResponse(text="I don't have sufficient data to answer this question based on the available information.")
    
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
                    return CompletionResponse(text="I don't have sufficient data to answer this question based on the available information.")
                    
        except Exception as e:
            logger.error(f"OpenRouter LLM async completion failed: {e}")
            return CompletionResponse(text="I don't have sufficient data to answer this question based on the available information.")
    
    def stream_complete(self, prompt: str, **kwargs):
        """Stream complete - not implemented for OpenRouter"""
        response = self.complete(prompt, **kwargs)
        yield response
    
    async def astream_complete(self, prompt: str, **kwargs):
        """Async stream complete - not implemented for OpenRouter"""
        response = await self.acomplete(prompt, **kwargs)
        yield response

class WindTurbineQueryEngine(CustomQueryEngine):
    """Custom query engine for wind turbine project data"""
    
    retriever: LlamaIndexRetriever
    llm: OpenRouterLLM
    qa_prompt: PromptTemplate
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, retriever: LlamaIndexRetriever, llm: OpenRouterLLM):
        # Wind turbine domain-specific prompt
        qa_prompt = PromptTemplate(
            """You are a specialized AI assistant for Suzlon's wind turbine project data analysis. 
            You have access to comprehensive project data including capacity, customer information, 
            business modules, states, project phases, and financial metrics.

            STRICT INSTRUCTIONS:
            1. Answer ONLY based on the provided context data below
            2. If the information is not in the context, respond with: "I don't have sufficient data to answer this question based on the available information."
            3. Never make up or hallucinate information
            4. Provide specific numbers, metrics, and details when available
            5. Translate technical terms to business language:
               - MWG = Megawatt Generation Capacity
               - WTG = Wind Turbine Generator  
               - Capacity deviations = Budget variance analysis
               - Project phases = Pipeline progression metrics
            6. Include relevant context like customer names, states, business modules when applicable
            7. For financial questions, focus on capacity, deviations, and business impact
            8. Be concise but comprehensive in your analysis
            9. Always cite specific data points from the context when making claims

            Context Information:
            ---------------------
            {context_str}
            ---------------------

            Question: {query_str}
            
            Answer: """
        )
        
        super().__init__(retriever=retriever, llm=llm, qa_prompt=qa_prompt)
    
    def custom_query(self, query_str: str) -> Response:
        """Execute custom query"""
        return asyncio.run(self.acustom_query(query_str))
    
    async def acustom_query(self, query_str: str) -> Response:
        """Execute async custom query"""
        try:
            # Retrieve relevant documents
            documents = await self.retriever.retrieve_documents(query_str)
            
            if not documents:
                return Response(
                    response="I don't have sufficient data to answer this question based on the available information.",
                    source_nodes=[],
                    metadata={"has_sufficient_data": False, "confidence": 0.0}
                )
            
            # Format context
            context_parts = []
            for i, doc in enumerate(documents[:10]):  # Limit to top 10 for context
                context_part = f"""
Document {i+1} (ID: {doc.doc_id}, Similarity: {doc.similarity_score:.3f}):
Customer: {doc.customer_name}
State: {doc.state}
Business Module: {doc.business_module}
Capacity: {doc.capacity} MW
WTG Count: {doc.wtg_count}
MWG: {doc.mwg}
Project Phase: {doc.project_phase}
Fiscal Year: {doc.fiscalyear}
Content: {doc.content}
---"""
                context_parts.append(context_part)
            
            context_str = "\n".join(context_parts)
            
            # Generate prompt
            prompt = self.qa_prompt.format(
                context_str=context_str,
                query_str=query_str
            )
            
            # Get LLM response
            llm_response = await self.llm.acomplete(prompt)
            
            # Check for data sufficiency
            response_text = llm_response.text
            has_sufficient_data = not any(
                phrase in response_text.lower() 
                for phrase in ["don't have sufficient data", "not enough information", "cannot find"]
            )
            
            # Calculate confidence based on similarity scores and number of sources
            if documents:
                avg_similarity = sum(doc.similarity_score or 0 for doc in documents) / len(documents)
                source_factor = min(len(documents) / 5.0, 1.0)
                confidence = (avg_similarity * 0.7 + source_factor * 0.3) if has_sufficient_data else 0.0
            else:
                confidence = 0.0
            
            return Response(
                response=response_text,
                source_nodes=[],  # We'll handle sources separately
                metadata={
                    "has_sufficient_data": has_sufficient_data,
                    "confidence": confidence,
                    "source_count": len(documents),
                    "sources": [
                        {
                            "doc_id": doc.doc_id,
                            "customer_name": doc.customer_name,
                            "state": doc.state,
                            "business_module": doc.business_module,
                            "capacity": doc.capacity,
                            "similarity_score": doc.similarity_score,
                            "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                        }
                        for doc in documents[:5]  # Top 5 sources
                    ]
                }
            )
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return Response(
                response="I encountered an error while processing your question. Please try again.",
                source_nodes=[],
                metadata={"has_sufficient_data": False, "confidence": 0.0, "error": str(e)}
            )

class LlamaIndexCompleteRAG:
    """Complete LlamaIndex RAG system with retrieval and generation"""
    
    def __init__(self):
        self.retriever: Optional[LlamaIndexRetriever] = None
        self.llm: Optional[OpenRouterLLM] = None
        self.query_engine: Optional[WindTurbineQueryEngine] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the complete RAG system"""
        try:
            logger.info("Initializing LlamaIndex Complete RAG system...")
            
            # Initialize retriever
            self.retriever = llamaindex_retriever
            await self.retriever.initialize()
            
            # Initialize LLM
            self.llm = OpenRouterLLM(
                model_name=settings.llm.model,
                api_key=settings.llm.api_key,
                base_url=settings.llm.base_url,
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens
            )
            
            # Set global LLM
            Settings.llm = self.llm
            
            # Initialize query engine
            self.query_engine = WindTurbineQueryEngine(self.retriever, self.llm)
            
            self._initialized = True
            logger.info("LlamaIndex Complete RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex Complete RAG system: {e}")
            raise
    
    def _ensure_initialized(self) -> None:
        """Ensure the system is initialized"""
        if not self._initialized:
            raise RuntimeError("LlamaIndex Complete RAG system not initialized. Call initialize() first.")
    
    async def query(
        self, 
        question: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the complete RAG system
        
        Args:
            question: Natural language question
            filters: Optional metadata filters
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        self._ensure_initialized()
        
        try:
            # Execute query
            response = await self.query_engine.acustom_query(question)
            
            return {
                'answer': response.response,
                'sources': response.metadata.get('sources', []),
                'query': question,
                'has_sufficient_data': response.metadata.get('has_sufficient_data', False),
                'confidence': response.metadata.get('confidence', 0.0),
                'source_count': response.metadata.get('source_count', 0)
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                'answer': "I encountered an error while processing your question. Please try again.",
                'sources': [],
                'query': question,
                'has_sufficient_data': False,
                'confidence': 0.0,
                'source_count': 0,
                'error': str(e)
            }
    
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
        
        Please focus on:
        - Key financial metrics and capacity data with specific numbers
        - Business impact and implications for Suzlon
        - Risk factors and capacity deviations with root causes
        - Actionable recommendations for management
        - State and customer distribution insights
        - Project phase analysis and pipeline health
        
        Format the response as a structured executive summary with:
        1. Executive Summary (2-3 sentences)
        2. Key Findings (bullet points with specific data)
        3. Risk Assessment (if applicable)
        4. Recommendations (actionable items)
        """
        
        result = await self.query(business_query)
        
        # Parse response for structured insights
        insights = {
            'executive_summary': result['answer'],
            'key_metrics': self._extract_metrics_from_sources(result['sources']),
            'risk_factors': self._identify_risks_from_sources(result['sources']),
            'recommendations': self._extract_recommendations(result['answer']),
            'data_confidence': result['confidence'],
            'source_count': result['source_count'],
            'has_sufficient_data': result['has_sufficient_data']
        }
        
        return insights
    
    def _extract_metrics_from_sources(self, sources: List[Dict]) -> List[Dict[str, Any]]:
        """Extract key metrics from source documents"""
        if not sources:
            return []
        
        metrics = []
        total_capacity = sum(source.get('capacity', 0) or 0 for source in sources)
        customer_count = len(set(source.get('customer_name') for source in sources if source.get('customer_name')))
        state_count = len(set(source.get('state') for source in sources if source.get('state')))
        
        metrics = [
            {'name': 'Total Capacity (from sources)', 'value': f"{total_capacity:.2f} MW", 'type': 'capacity'},
            {'name': 'Unique Customers', 'value': customer_count, 'type': 'count'},
            {'name': 'States Covered', 'value': state_count, 'type': 'count'},
            {'name': 'Data Points Analyzed', 'value': len(sources), 'type': 'count'}
        ]
        
        return metrics
    
    def _identify_risks_from_sources(self, sources: List[Dict]) -> List[str]:
        """Identify risk factors from source data"""
        risks = []
        
        # This would be enhanced with actual business logic
        # For now, return placeholder
        if len(sources) < 3:
            risks.append("Limited data availability may affect analysis accuracy")
        
        return risks
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract actionable recommendations from response"""
        recommendations = []
        
        # Look for recommendation-like sentences
        sentences = response.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(word in sentence.lower() for word in ['should', 'recommend', 'suggest', 'consider', 'need to', 'must']):
                if len(sentence) > 10:  # Filter out very short sentences
                    recommendations.append(sentence)
        
        return recommendations[:4]  # Limit to top 4 recommendations

# Global LlamaIndex Complete RAG system instance
llamaindex_complete_rag = LlamaIndexCompleteRAG()