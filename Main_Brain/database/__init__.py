"""
Database layer for Multi-Agent Chatbot Copilot
Handles PostgreSQL connections, pgvector operations, and data management
"""

from .connection import DatabaseManager, db_manager
from .models import (
    ConversationHistory, 
    PredictionCache, 
    RAGDocument, 
    DatabaseStatus, 
    DatabaseStats,
    QueryIntent
)
from .status import get_database_status, get_database_stats, get_system_health

__all__ = [
    "DatabaseManager",
    "db_manager",
    "ConversationHistory", 
    "PredictionCache",
    "RAGDocument",
    "DatabaseStatus",
    "DatabaseStats",
    "QueryIntent",
    "get_database_status",
    "get_database_stats", 
    "get_system_health"
]