"""
Conversation Memory System for Multi-Agent Chatbot Copilot
Manages conversation context, session storage, and user interaction history
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import redis.asyncio as redis
import logging
from contextlib import asynccontextmanager

from config import settings
from agents.base import AgentResponse, QueryContext

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    turn_id: str
    timestamp: datetime
    user_query: str
    agent_response: AgentResponse
    session_id: str
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        # Convert agent_response to dict, handling Pydantic models in visualizations
        agent_response_dict = asdict(self.agent_response)
        
        # Properly serialize visualizations (they might be Pydantic models)
        if self.agent_response.visualizations:
            serialized_viz = []
            for viz in self.agent_response.visualizations:
                if hasattr(viz, 'model_dump'):  # Pydantic v2
                    serialized_viz.append(viz.model_dump())
                elif hasattr(viz, 'dict'):  # Pydantic v1
                    serialized_viz.append(viz.dict())
                elif isinstance(viz, dict):
                    serialized_viz.append(viz)
                else:
                    # Fallback: try to convert to dict
                    serialized_viz.append(dict(viz) if hasattr(viz, '__dict__') else viz)
            agent_response_dict['visualizations'] = serialized_viz
        
        return {
            "turn_id": self.turn_id,
            "timestamp": self.timestamp.isoformat(),
            "user_query": self.user_query,
            "agent_response": agent_response_dict,
            "session_id": self.session_id,
            "user_id": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """Create from dictionary"""
        # Reconstruct AgentResponse
        response_data = data["agent_response"]
        agent_response = AgentResponse(**response_data)
        
        return cls(
            turn_id=data["turn_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_query=data["user_query"],
            agent_response=agent_response,
            session_id=data["session_id"],
            user_id=data.get("user_id")
        )

@dataclass
class ConversationContext:
    """Complete conversation context for an agent"""
    session_id: str
    user_id: Optional[str]
    turns: List[ConversationTurn]
    current_topic: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def get_recent_queries(self, limit: int = 5) -> List[str]:
        """Get recent user queries"""
        return [turn.user_query for turn in self.turns[-limit:]]
    
    def get_recent_responses(self, limit: int = 5) -> List[AgentResponse]:
        """Get recent agent responses"""
        return [turn.agent_response for turn in self.turns[-limit:]]
    
    def get_conversation_summary(self, max_turns: int = 10) -> str:
        """Generate a summary of recent conversation"""
        recent_turns = self.turns[-max_turns:]
        if not recent_turns:
            return "No previous conversation"
        
        summary_parts = []
        for turn in recent_turns:
            summary_parts.append(f"User: {turn.user_query}")
            summary_parts.append(f"Assistant: {turn.agent_response.content[:200]}...")
        
        return "\n".join(summary_parts)

@dataclass
class SessionSummary:
    """Summary of a conversation session"""
    session_id: str
    user_id: Optional[str]
    start_time: datetime
    last_activity: datetime
    turn_count: int
    topics: List[str]
    key_metrics_discussed: List[str]

class ConversationMemory:
    """
    Manages conversation memory using Redis for session storage
    Provides context retrieval, session management, and conversation summarization
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.session_timeout = settings.security.session_timeout
        self.memory_limit = settings.agents.conversation_memory_limit
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize Redis connection and memory system"""
        if self._initialized:
            return
        
        try:
            # Create Redis connection
            self.redis_client = redis.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db,
                password=settings.redis.password,
                username=settings.redis.user,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis connection established for conversation memory")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize conversation memory: {str(e)}")
            raise
    
    async def cleanup(self) -> None:
        """Cleanup Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self._initialized = False
            logger.info("✅ Conversation memory cleanup completed")
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session data"""
        return f"conversation:session:{session_id}"
    
    def _get_turn_key(self, session_id: str, turn_id: str) -> str:
        """Get Redis key for individual turn data"""
        return f"conversation:turn:{session_id}:{turn_id}"
    
    def _get_user_sessions_key(self, user_id: str) -> str:
        """Get Redis key for user's session list"""
        return f"conversation:user:{user_id}:sessions"
    
    async def store_interaction(
        self, 
        query: str, 
        response: AgentResponse, 
        session_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Store a conversation turn in memory
        Returns the turn_id for the stored interaction
        """
        if not self._initialized:
            await self.initialize()
        
        # Generate unique turn ID
        turn_id = str(uuid.uuid4())
        
        # Create conversation turn
        turn = ConversationTurn(
            turn_id=turn_id,
            timestamp=datetime.utcnow(),
            user_query=query,
            agent_response=response,
            session_id=session_id,
            user_id=user_id
        )
        
        try:
            # Store turn data
            turn_key = self._get_turn_key(session_id, turn_id)
            await self.redis_client.setex(
                turn_key,
                self.session_timeout,
                json.dumps(turn.to_dict(), default=str)
            )
            
            # Add turn to session's turn list
            session_key = self._get_session_key(session_id)
            await self.redis_client.lpush(session_key, turn_id)
            await self.redis_client.expire(session_key, self.session_timeout)
            
            # Trim session to memory limit
            await self.redis_client.ltrim(session_key, 0, self.memory_limit - 1)
            
            # Update user's session list if user_id provided
            if user_id:
                user_sessions_key = self._get_user_sessions_key(user_id)
                await self.redis_client.sadd(user_sessions_key, session_id)
                await self.redis_client.expire(user_sessions_key, self.session_timeout * 24)  # Keep longer
            
            logger.debug(f"Stored conversation turn {turn_id} for session {session_id}")
            return turn_id
            
        except Exception as e:
            logger.error(f"Failed to store conversation turn: {str(e)}")
            raise
    
    async def get_context(
        self, 
        session_id: str, 
        lookback: Optional[int] = None
    ) -> ConversationContext:
        """
        Retrieve conversation context for a session
        """
        if not self._initialized:
            await self.initialize()
        
        if lookback is None:
            lookback = self.memory_limit
        
        try:
            # Get turn IDs from session
            session_key = self._get_session_key(session_id)
            turn_ids = await self.redis_client.lrange(session_key, 0, lookback - 1)
            
            # Retrieve turn data
            turns = []
            user_id = None
            
            for turn_id in turn_ids:
                turn_key = self._get_turn_key(session_id, turn_id)
                turn_data = await self.redis_client.get(turn_key)
                
                if turn_data:
                    turn_dict = json.loads(turn_data)
                    turn = ConversationTurn.from_dict(turn_dict)
                    turns.append(turn)
                    
                    # Get user_id from first turn
                    if user_id is None:
                        user_id = turn.user_id
            
            # Reverse to get chronological order (Redis LRANGE returns newest first)
            turns.reverse()
            
            # Detect current topic from recent queries
            current_topic = self._detect_current_topic(turns)
            
            return ConversationContext(
                session_id=session_id,
                user_id=user_id,
                turns=turns,
                current_topic=current_topic,
                metadata={
                    "turn_count": len(turns),
                    "last_activity": turns[-1].timestamp.isoformat() if turns else None
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation context: {str(e)}")
            # Return empty context on error
            return ConversationContext(
                session_id=session_id,
                user_id=None,
                turns=[],
                current_topic=None
            )
    
    def _detect_current_topic(self, turns: List[ConversationTurn]) -> Optional[str]:
        """Detect current conversation topic from recent turns"""
        if not turns:
            return None
        
        # Simple topic detection based on keywords in recent queries
        recent_queries = [turn.user_query.lower() for turn in turns[-3:]]
        combined_text = " ".join(recent_queries)
        
        # Define topic keywords
        topics = {
            "financial_analysis": ["revenue", "cost", "margin", "profit", "financial", "budget", "cash"],
            "forecasting": ["forecast", "predict", "future", "trend", "projection", "what if"],
            "visualization": ["chart", "graph", "plot", "show", "visualize", "display"],
            "capacity_analysis": ["capacity", "mwg", "wtg", "turbine", "generation"],
            "geographic_analysis": ["state", "region", "location", "geographic", "map"],
            "project_analysis": ["project", "phase", "timeline", "milestone", "delivery"]
        }
        
        # Count topic keywords
        topic_scores = {}
        for topic, keywords in topics.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                topic_scores[topic] = score
        
        # Return topic with highest score
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return None
    
    async def summarize_session(self, session_id: str) -> SessionSummary:
        """Generate a summary of the conversation session"""
        context = await self.get_context(session_id)
        
        if not context.turns:
            raise ValueError(f"No conversation found for session {session_id}")
        
        # Extract topics and metrics discussed
        topics = set()
        metrics = set()
        
        for turn in context.turns:
            # Extract topics from agent responses
            if hasattr(turn.agent_response, 'metadata') and turn.agent_response.metadata:
                if 'topic' in turn.agent_response.metadata:
                    topics.add(turn.agent_response.metadata['topic'])
            
            # Extract metrics from content (simple keyword matching)
            content = turn.agent_response.content.lower()
            metric_keywords = ["revenue", "capacity", "mwg", "wtg", "cost", "margin", "profit"]
            for keyword in metric_keywords:
                if keyword in content:
                    metrics.add(keyword)
        
        return SessionSummary(
            session_id=session_id,
            user_id=context.user_id,
            start_time=context.turns[0].timestamp,
            last_activity=context.turns[-1].timestamp,
            turn_count=len(context.turns),
            topics=list(topics),
            key_metrics_discussed=list(metrics)
        )
    
    async def clear_session(self, session_id: str) -> bool:
        """Clear all conversation data for a session"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get all turn IDs for the session
            session_key = self._get_session_key(session_id)
            turn_ids = await self.redis_client.lrange(session_key, 0, -1)
            
            # Delete all turn data
            for turn_id in turn_ids:
                turn_key = self._get_turn_key(session_id, turn_id)
                await self.redis_client.delete(turn_key)
            
            # Delete session key
            await self.redis_client.delete(session_key)
            
            logger.info(f"Cleared conversation session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear session {session_id}: {str(e)}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user"""
        if not self._initialized:
            await self.initialize()
        
        try:
            user_sessions_key = self._get_user_sessions_key(user_id)
            sessions = await self.redis_client.smembers(user_sessions_key)
            return list(sessions)
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # This is handled automatically by Redis TTL, but we can implement
            # additional cleanup logic here if needed
            logger.info("Session cleanup completed (handled by Redis TTL)")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {str(e)}")
            return 0
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get Redis info
            info = await self.redis_client.info()
            
            # Count conversation keys
            session_keys = await self.redis_client.keys("conversation:session:*")
            turn_keys = await self.redis_client.keys("conversation:turn:*")
            user_keys = await self.redis_client.keys("conversation:user:*")
            
            return {
                "redis_connected": True,
                "active_sessions": len(session_keys),
                "total_turns": len(turn_keys),
                "total_users": len(user_keys),
                "memory_usage_mb": info.get("used_memory", 0) / (1024 * 1024),
                "session_timeout": self.session_timeout,
                "memory_limit_per_session": self.memory_limit
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {str(e)}")
            return {
                "redis_connected": False,
                "error": str(e)
            }

# Global conversation memory instance
conversation_memory = ConversationMemory()

@asynccontextmanager
async def get_conversation_memory():
    """Context manager for conversation memory"""
    if not conversation_memory._initialized:
        await conversation_memory.initialize()
    try:
        yield conversation_memory
    finally:
        # Don't cleanup here as it's a singleton
        pass