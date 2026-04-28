"""
LLM Integration for Multi-Agent Chatbot Copilot
Handles language model interactions and prompt management
"""

from .client import LLMClient
from .prompts import PromptManager

__all__ = [
    "LLMClient",
    "PromptManager"
]