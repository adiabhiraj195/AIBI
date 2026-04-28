"""
Base Agent class for Multi-Agent Chatbot Copilot
Provides common interfaces and functionality for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Standard response format for all agents"""
    agent_name: str
    content: str
    visualizations: List[Dict[str, Any]] = None
    confidence: float = 1.0
    execution_time: float = 0.0
    follow_up_questions: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.visualizations is None:
            self.visualizations = []
        if self.follow_up_questions is None:
            self.follow_up_questions = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class QueryContext:
    """Context information for query processing"""
    query: str
    session_id: str
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.metadata is None:
            self.metadata = {}

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system
    Provides common functionality and enforces interface contracts
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agents.{name}")
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize agent resources and dependencies"""
        if self._initialized:
            return
        
        self.logger.info(f"Initializing {self.name} agent...")
        await self._initialize_impl()
        self._initialized = True
        self.logger.info(f"{self.name} agent initialized successfully")
    
    @abstractmethod
    async def _initialize_impl(self) -> None:
        """Agent-specific initialization logic"""
        pass
    
    async def process(self, context: QueryContext) -> AgentResponse:
        """
        Main processing method for handling queries
        Includes timing, error handling, and logging
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing query with {self.name} agent")
            response = await self._process_impl(context)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            response.execution_time = execution_time
            
            self.logger.info(f"{self.name} agent completed in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"{self.name} agent failed after {execution_time:.2f}s: {str(e)}")
            
            # Return error response
            return AgentResponse(
                agent_name=self.name,
                content=f"Error processing query: {str(e)}",
                confidence=0.0,
                execution_time=execution_time,
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
    
    @abstractmethod
    async def _process_impl(self, context: QueryContext) -> AgentResponse:
        """Agent-specific processing logic"""
        pass
    
    def can_handle(self, query: str, context: QueryContext = None) -> float:
        """
        Determine if this agent can handle the given query
        Returns confidence score between 0.0 and 1.0
        """
        return self._calculate_confidence(query, context)
    
    @abstractmethod
    def _calculate_confidence(self, query: str, context: QueryContext = None) -> float:
        """Agent-specific confidence calculation"""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        if not self._initialized:
            return
        
        self.logger.info(f"Cleaning up {self.name} agent...")
        await self._cleanup_impl()
        self._initialized = False
        self.logger.info(f"{self.name} agent cleanup completed")
    
    async def _cleanup_impl(self) -> None:
        """Agent-specific cleanup logic"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "initialized": self._initialized,
            "config": self.config,
            "status": "ready" if self._initialized else "not_initialized"
        }