"""
Database connection utilities for Multi-Agent Chatbot Copilot
Handles PostgreSQL connections with pgvector extension
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Tuple
from contextlib import asynccontextmanager
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._sync_conn = None
        
    async def initialize(self) -> None:
        """Initialize async connection pool"""
        try:
            # Create async connection pool
            ssl_mode = settings.db_ssl_mode if settings.db_ssl_mode != "prefer" else "prefer"
            self._pool = await asyncpg.create_pool(
                host=settings.database.host,
                port=settings.database.port,
                database=settings.database.name,
                user=settings.database.user,
                password=settings.database.password,
                ssl=ssl_mode,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            logger.info(f"Database pool initialized: {settings.database.host}:{settings.database.port}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self) -> None:
        """Close database connections"""
        if self._pool:
            await self._pool.close()
            logger.info("Database pool closed")
        
        if self._sync_conn:
            self._sync_conn.close()
            logger.info("Sync database connection closed")

    async def cleanup(self) -> None:
        """Alias for close() to support cleanup protocol"""
        await self.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get async database connection from pool"""
        if not self._pool:
            await self.initialize()
        
        async with self._pool.acquire() as conn:
            yield conn
    
    def get_sync_connection(self):
        """Get synchronous database connection for embedding operations"""
        if not self._sync_conn or self._sync_conn.closed:
            self._sync_conn = psycopg2.connect(
                host=settings.database.host,
                port=settings.database.port,
                database=settings.database.name,
                user=settings.database.user,
                password=settings.database.password,
                cursor_factory=RealDictCursor
            )
        return self._sync_conn
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status info"""
        try:
            async with self.get_connection() as conn:
                # Test basic connectivity
                version = await conn.fetchval("SELECT version()")
                
                # Check pgvector extension
                vector_ext = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                )
                
                # Check rag_embeddings table and count
                table_exists = await conn.fetchval("""
                    SELECT EXISTS(
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'rag_embeddings'
                    )
                """)
                
                embedding_count = 0
                if table_exists:
                    embedding_count = await conn.fetchval("SELECT COUNT(*) FROM rag_embeddings")
                
                return {
                    "status": "connected",
                    "host": settings.database.host,
                    "port": settings.database.port,
                    "database": settings.database.name,
                    "version": version,
                    "pgvector_installed": vector_ext,
                    "rag_table_exists": table_exists,
                    "embedding_count": embedding_count
                }
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "host": settings.database.host,
                "port": settings.database.port,
                "database": settings.database.name
            }
    
    async def create_tables(self) -> None:
        """Create required tables for the system"""
        async with self.get_connection() as conn:
            # Create conversation history table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255),
                    user_query TEXT NOT NULL,
                    agent_response JSONB NOT NULL,
                    query_intent VARCHAR(100),
                    execution_time FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes for conversation history
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_session_id 
                ON conversation_history (session_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_user_id 
                ON conversation_history (user_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_created_at 
                ON conversation_history (created_at)
            """)
            
            # Create prediction cache table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS prediction_cache (
                    id SERIAL PRIMARY KEY,
                    query_hash VARCHAR(255) UNIQUE NOT NULL,
                    model_type VARCHAR(50) NOT NULL,
                    prediction JSONB NOT NULL,
                    confidence FLOAT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP
                )
            """)
            
            # Create indexes for prediction cache
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_prediction_query_hash 
                ON prediction_cache (query_hash)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_prediction_model_type 
                ON prediction_cache (model_type)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_prediction_expires_at 
                ON prediction_cache (expires_at)
            """)
            
            # Create dashboard items table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_items (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255),
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    visualization_data JSONB NOT NULL,
                    layout JSONB,
                    category VARCHAR(255) DEFAULT 'General',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes for dashboard items
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dashboard_user_id 
                ON dashboard_items (user_id)
            """)
            
            logger.info("Database tables created successfully")
    
    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about the embeddings table"""
        async with self.get_connection() as conn:
            try:
                # Basic counts
                total_count = await conn.fetchval("SELECT COUNT(*) FROM rag_embeddings")
                
                # Count by business module
                business_modules = await conn.fetch("""
                    SELECT business_module, COUNT(*) as count
                    FROM rag_embeddings 
                    WHERE business_module IS NOT NULL
                    GROUP BY business_module
                    ORDER BY count DESC
                """)
                
                # Count by state
                states = await conn.fetch("""
                    SELECT state, COUNT(*) as count
                    FROM rag_embeddings 
                    WHERE state IS NOT NULL
                    GROUP BY state
                    ORDER BY count DESC
                    LIMIT 10
                """)
                
                # Capacity statistics
                capacity_stats = await conn.fetchrow("""
                    SELECT 
                        MIN(capacity) as min_capacity,
                        MAX(capacity) as max_capacity,
                        AVG(capacity) as avg_capacity,
                        SUM(capacity) as total_capacity
                    FROM rag_embeddings 
                    WHERE capacity IS NOT NULL
                """)
                
                return {
                    "total_embeddings": total_count,
                    "business_modules": [dict(row) for row in business_modules],
                    "top_states": [dict(row) for row in states],
                    "capacity_stats": dict(capacity_stats) if capacity_stats else {}
                }
                
            except Exception as e:
                logger.error(f"Failed to get embedding stats: {e}")
                return {"error": str(e)}
    
    async def get_status(self) -> dict:
        """Get database connection status and basic information"""
        try:
            if not self._pool:
                return {
                    "status": "disconnected",
                    "host": "unknown",
                    "database": "unknown",
                    "embedding_count": 0,
                    "tables": []
                }
            
            async with self._pool.acquire() as conn:
                # Test connection
                await conn.fetchval("SELECT 1")
                
                # Get embedding count
                embedding_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM rag_embeddings"
                )
                
                # Get table list
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                
                return {
                    "status": "connected",
                    "host": settings.database.host,
                    "database": settings.database.name,
                    "embedding_count": embedding_count or 0,
                    "tables": [row['table_name'] for row in tables]
                }
                
        except Exception as e:
            logger.error(f"Database status check failed: {e}")
            return {
                "status": "error",
                "host": settings.database.host,
                "database": settings.database.name,
                "embedding_count": 0,
                "tables": [],
                "error": str(e)
            }

# Global database manager instance
db_manager = DatabaseManager()