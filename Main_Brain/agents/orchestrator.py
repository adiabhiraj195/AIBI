"""
Orchestrator Agent for Multi-Agent Chatbot Copilot
Central routing and coordination hub for all user queries
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from agents.base import BaseAgent, AgentResponse, QueryContext
from agents.memory import ConversationMemory, conversation_memory
from agents.insights import insights_agent
from agents.visualization import visualization_agent
from rag.system import rag_system
from rag.statistical_queries import StatisticalQueryHandler
from rag.nl2sql_agent import NL2SQLAgent

logger = logging.getLogger(__name__)



class OrchestratorAgent(BaseAgent):
    """
    Central orchestrator agent that routes queries to appropriate specialized agents
    Handles query classification, agent coordination, and response aggregation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("orchestrator", config)
        self.statistical_handler = StatisticalQueryHandler()
        self.nl2sql_agent = NL2SQLAgent()
        self.conversation_memory = conversation_memory
        self.insights_agent = insights_agent
        self.visualization_agent = visualization_agent
        

    
    async def _initialize_impl(self) -> None:
        """Initialize orchestrator dependencies"""
        try:
            # Initialize RAG system
            if not rag_system._model_loaded:
                await rag_system.initialize()
            
            # Initialize conversation memory
            if not self.conversation_memory._initialized:
                await self.conversation_memory.initialize()
            
            # Initialize insights agent
            if not self.insights_agent._initialized:
                await self.insights_agent.initialize()
            
            # Initialize visualization agent
            if not self.visualization_agent._initialized:
                await self.visualization_agent.initialize()
            
            # NL2SQL agent doesn't require async initialization
            
            logger.info("✅ Orchestrator agent initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator agent: {str(e)}")
            raise
    
    async def _process_impl(self, context: QueryContext) -> AgentResponse:
        """
        Main orchestrator processing logic with proper handler prioritization:
        1. Try NL2SQL Agent (highest priority)
        2. Try Statistical Query Handler (high priority)
        3. Fall back to RAG Semantic Search (lowest priority)
        4. Apply confidence threshold (< 0.7 = ask for more context)
        """
        try:
            # Get conversation context for better routing and clarification
            conv_context = await self.conversation_memory.get_context(context.session_id)
            
            # Try handlers in priority order
            response = await self._try_primary_handlers(context, conv_context)
            
            # If no high-confidence response, ask for more context
            if not response or response.confidence < 0.7:
                response = await self._request_more_context(context, conv_context, response)
            
            # Store interaction in conversation memory
            await self.conversation_memory.store_interaction(
                context.query, 
                response, 
                context.session_id,
                context.user_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Orchestrator processing failed: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                content=f"I encountered an error processing your query: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    

    
    def _is_statistical_query(self, query: str) -> bool:
        """Check if query requires statistical analysis"""
        statistical_indicators = [
            'total', 'sum', 'count', 'average', 'mean', 'max', 'min',
            'top', 'bottom', 'highest', 'lowest', 'breakdown', 'by',
            'compare', 'vs', 'difference', 'analysis'
        ]
        
        return any(indicator in query for indicator in statistical_indicators)
    

    

    

    
    async def _try_primary_handlers(self, context: QueryContext, conv_context) -> Optional[AgentResponse]:
        """
        Try primary handlers in priority order:
        1. NL2SQL Agent (for complex semantic queries)
        2. Statistical Query Handler (for aggregation queries)
        3. RAG Semantic Search (fallback only)
        """
        
        # Priority 1: Try NL2SQL Agent
        try:
            logger.info("Trying NL2SQL Agent...")
            nl2sql_result = await self.nl2sql_agent.process_natural_query(context.query)
            if nl2sql_result and nl2sql_result.get('success'):
                confidence = nl2sql_result.get('confidence', 0.95)
                if confidence >= 0.7:
                    # Use Insights Agent to generate CFO-grade response
                    insights_context = QueryContext(
                        query=context.query,
                        session_id=context.session_id,
                        user_id=context.user_id,
                        metadata={
                            "processed_data": nl2sql_result.get('data_full', []),
                            "handler": "nl2sql_agent",
                            "sql_query": nl2sql_result.get('sql_query', ''),
                            "raw_response": nl2sql_result.get('answer', ''),
                            "row_count": nl2sql_result.get('row_count', 0)
                        }
                    )
                    
                    insights_response = await self.insights_agent.process(insights_context)
                    
                    # Generate visualizations
                    viz_context = QueryContext(
                        query=context.query,
                        session_id=context.session_id,
                        user_id=context.user_id,
                        metadata={
                            "processed_data": nl2sql_result.get('data_full', []),
                            "handler": "nl2sql_agent"
                        }
                    )
                    viz_response = await self.visualization_agent.process(viz_context)
                    
                    # Combine insights and visualizations
                    combined_content = insights_response.content
                    if viz_response.visualizations:
                        combined_content += f"\n\n{viz_response.content}"
                    
                    return AgentResponse(
                        agent_name="orchestrator",
                        content=combined_content,
                        visualizations=viz_response.visualizations,
                        confidence=confidence,
                        metadata={
                            "handler": "nl2sql_agent",
                            "sql_query": nl2sql_result.get('sql_query', ''),
                            "data_source": "nl2sql_agent",
                            "insights_generated": True,
                            "visualizations_generated": len(viz_response.visualizations) > 0,
                            "cfo_response": insights_response.metadata.get("cfo_response")
                        }
                    )
        except Exception as e:
            logger.warning(f"NL2SQL Agent failed: {str(e)}")
        
        # Priority 2: Try Statistical Query Handler
        try:
            logger.info("Trying Statistical Query Handler...")
            if self._is_statistical_query(context.query.lower()):
                stat_result = await self.statistical_handler.handle_statistical_query(context.query)
                if stat_result and stat_result.get('success'):
                    confidence = stat_result.get('confidence', 0.9)
                    if confidence >= 0.7:
                        # Use Insights Agent to generate CFO-grade response
                        insights_context = QueryContext(
                            query=context.query,
                            session_id=context.session_id,
                            user_id=context.user_id,
                            metadata={
                                "processed_data": stat_result,
                                "handler": "statistical_handler",
                                "query_type": stat_result.get('query_type'),
                                "raw_answer": stat_result.get('answer', '')
                            }
                        )
                        
                        insights_response = await self.insights_agent.process(insights_context)
                        
                        # Generate visualizations
                        viz_context = QueryContext(
                            query=context.query,
                            session_id=context.session_id,
                            user_id=context.user_id,
                            metadata={
                                "processed_data": stat_result,
                                "handler": "statistical_handler"
                            }
                        )
                        viz_response = await self.visualization_agent.process(viz_context)
                        
                        # Combine insights and visualizations
                        combined_content = insights_response.content
                        if viz_response.visualizations:
                            combined_content += f"\n\n{viz_response.content}"
                        
                        return AgentResponse(
                            agent_name="orchestrator",
                            content=combined_content,
                            visualizations=viz_response.visualizations,
                            confidence=confidence,
                            metadata={
                                "handler": "statistical_handler",
                                "query_type": stat_result.get('query_type'),
                                "data_source": "statistical_handler",
                                "insights_generated": True,
                                "visualizations_generated": len(viz_response.visualizations) > 0,
                                "cfo_response": insights_response.metadata.get("cfo_response")
                            }
                        )
        except Exception as e:
            logger.warning(f"Statistical Query Handler failed: {str(e)}")
        
        # Priority 3: Try RAG Semantic Search (fallback only)
        try:
            logger.info("Trying RAG Semantic Search as fallback...")
            documents = await rag_system.semantic_search(context.query, limit=10)
            
            if documents and len(documents) >= 5:  # Only if we have sufficient relevant documents
                # Use Insights Agent to generate CFO-grade response
                insights_context = QueryContext(
                    query=context.query,
                    session_id=context.session_id,
                    user_id=context.user_id,
                    metadata={
                        "processed_data": documents,
                        "handler": "rag_semantic_search",
                        "document_count": len(documents)
                    }
                )
                
                insights_response = await self.insights_agent.process(insights_context)
                
                # Lower confidence for semantic search fallback
                return AgentResponse(
                    agent_name="orchestrator",
                    content=insights_response.content,
                    confidence=0.6,  # Intentionally below 0.7 threshold
                    metadata={
                        "handler": "rag_semantic_search",
                        "document_count": len(documents),
                        "data_source": "rag_system",
                        "insights_generated": True,
                        "cfo_response": insights_response.metadata.get("cfo_response")
                    }
                )
        except Exception as e:
            logger.warning(f"RAG Semantic Search failed: {str(e)}")
        
        # No handler succeeded
        return None
    
    async def _request_more_context(
        self, 
        context: QueryContext, 
        conv_context, 
        low_confidence_response: Optional[AgentResponse]
    ) -> AgentResponse:
        """
        Request more context from user when confidence is below threshold
        Uses conversation history to provide intelligent clarification requests
        """
        
        # Analyze conversation history for context
        recent_topics = []
        if conv_context and conv_context.turns:
            recent_queries = [turn.user_query for turn in conv_context.turns[-3:]]
            recent_topics = self._extract_topics_from_history(recent_queries)
        
        # Generate contextual clarification request
        clarification_msg = "I don't have enough context to provide a confident answer. "
        
        # Add specific suggestions based on query content and history
        suggestions = []
        
        query_lower = context.query.lower()
        
        # Suggest specific details based on query type
        if any(word in query_lower for word in ['customer', 'customers']):
            suggestions.append("specify which customer or customer segment you're interested in")
        
        if any(word in query_lower for word in ['state', 'states', 'region']):
            suggestions.append("mention specific states or regions")
        
        if any(word in query_lower for word in ['capacity', 'mwg', 'project']):
            suggestions.append("specify the time period (fiscal year) or project phase")
        
        if any(word in query_lower for word in ['analysis', 'compare', 'breakdown']):
            suggestions.append("clarify what specific metrics or dimensions you want to analyze")
        
        # Add suggestions based on recent conversation topics
        if recent_topics:
            if 'capacity' in recent_topics:
                suggestions.append("specify if you want capacity by customer, state, or business module")
            if 'financial' in recent_topics:
                suggestions.append("mention specific financial metrics like revenue, cost, or margin")
        
        # Default suggestions if none specific
        if not suggestions:
            suggestions = [
                "provide more specific details about what you're looking for",
                "mention specific time periods, customers, or regions",
                "clarify what type of analysis or breakdown you need"
            ]
        
        # Format the clarification request
        if len(suggestions) == 1:
            clarification_msg += f"Could you please {suggestions[0]}?"
        elif len(suggestions) == 2:
            clarification_msg += f"Could you please {suggestions[0]} or {suggestions[1]}?"
        else:
            clarification_msg += f"Could you please {', '.join(suggestions[:-1])}, or {suggestions[-1]}?"
        
        # Add conversation context hint
        if recent_topics:
            clarification_msg += f"\n\nBased on our recent discussion about {', '.join(recent_topics[:2])}, "
            clarification_msg += "I can provide more targeted insights with additional details."
        
        return AgentResponse(
            agent_name="orchestrator",
            content=clarification_msg,
            confidence=0.5,
            metadata={
                "handler": "clarification_request",
                "low_confidence_response": low_confidence_response.content if low_confidence_response else None,
                "suggested_details": suggestions,
                "recent_topics": recent_topics
            }
        )
    
    def _extract_topics_from_history(self, recent_queries: List[str]) -> List[str]:
        """Extract topics from recent conversation history"""
        topics = set()
        
        for query in recent_queries:
            query_lower = query.lower()
            
            # Business topics
            if any(word in query_lower for word in ['capacity', 'mwg', 'turbine', 'wtg']):
                topics.add('capacity')
            if any(word in query_lower for word in ['revenue', 'cost', 'margin', 'profit', 'financial']):
                topics.add('financial')
            if any(word in query_lower for word in ['customer', 'client']):
                topics.add('customer')
            if any(word in query_lower for word in ['state', 'region', 'geographic']):
                topics.add('geographic')
            if any(word in query_lower for word in ['project', 'phase']):
                topics.add('project')
            if any(word in query_lower for word in ['forecast', 'predict', 'future']):
                topics.add('forecasting')
        
        return list(topics)
    
    def _calculate_confidence(self, query: str, context: QueryContext = None) -> float:
        """Calculate confidence score for handling this query"""
        # Orchestrator can handle any query, but with varying confidence
        if not query or len(query.strip()) < 3:
            return 0.1
        
        # Higher confidence for business/financial queries
        business_keywords = ['capacity', 'revenue', 'customer', 'project', 'analysis', 'forecast']
        keyword_matches = sum(1 for keyword in business_keywords if keyword in query.lower())
        
        base_confidence = 0.7
        keyword_boost = min(keyword_matches * 0.1, 0.3)
        
        return min(base_confidence + keyword_boost, 1.0)

# Global orchestrator instance
orchestrator_agent = OrchestratorAgent()