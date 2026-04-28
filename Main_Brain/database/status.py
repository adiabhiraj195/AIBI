"""
Database status utilities for Multi-Agent Chatbot Copilot
Provides health checks and system information endpoints
"""

import logging
from typing import Dict, Any
from database.connection import db_manager
from database.models import DatabaseStatus, DatabaseStats
from config import settings

logger = logging.getLogger(__name__)

async def get_database_status() -> DatabaseStatus:
    """
    Get comprehensive database connection status and information
    
    Returns:
        DatabaseStatus object with connection info and statistics
    """
    try:
        status_info = await db_manager.test_connection()
        return DatabaseStatus(**status_info)
        
    except Exception as e:
        logger.error(f"Failed to get database status: {e}")
        return DatabaseStatus(
            status="error",
            host=settings.database.host,
            port=settings.database.port,
            database=settings.database.name,
            error=str(e)
        )

async def get_database_stats() -> DatabaseStats:
    """
    Get detailed database statistics including embedding counts and distributions
    
    Returns:
        DatabaseStats object with comprehensive statistics
    """
    try:
        stats_info = await db_manager.get_embedding_stats()
        return DatabaseStats(**stats_info)
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return DatabaseStats(
            total_embeddings=0,
            business_modules=[],
            top_states=[],
            capacity_stats={"error": str(e)}
        )

async def get_system_health() -> Dict[str, Any]:
    """
    Get overall system health including database and configuration status
    
    Returns:
        Dictionary with system health information
    """
    try:
        # Get database status
        db_status = await get_database_status()
        
        # Get database stats if connection is healthy
        db_stats = None
        if db_status.status == "connected":
            db_stats = await get_database_stats()
        
        # Check configuration
        config_status = {
            "database_configured": bool(settings.database.user and settings.database.password),
            "redis_configured": bool(settings.redis.host),
            "llm_configured": bool(settings.llm.api_key),
            "embedding_model": settings.rag.embedding_model,
            "max_retrieval_docs": settings.rag.max_retrieval_docs,
            "similarity_threshold": settings.rag.similarity_threshold
        }
        
        return {
            "status": "healthy" if db_status.status == "connected" else "degraded",
            "database": db_status.dict(),
            "statistics": db_stats.dict() if db_stats else None,
            "configuration": config_status,
            "version": "1.0.0",
            "environment": {
                "host": settings.host,
                "port": settings.port,
                "debug": settings.debug
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        return {
            "status": "error",
            "error": str(e),
            "database": None,
            "statistics": None,
            "configuration": None
        }