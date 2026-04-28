"""
Multi-Agent System for Chatbot Copilot
Provides specialized agents for different query types and orchestration
"""

from .base import BaseAgent
from .orchestrator import OrchestratorAgent
from .insights import InsightsAgent
from .visualization import VisualizationAgent
from .memory import ConversationMemory

# Future agent implementations
# from .forecasting import ForecastingAgent
# from .follow_up import FollowUpAgent

__all__ = [
    "BaseAgent",
    "OrchestratorAgent", 
    "InsightsAgent",
    "VisualizationAgent",
    "ConversationMemory",
    # "ForecastingAgent",
    # "FollowUpAgent"
]