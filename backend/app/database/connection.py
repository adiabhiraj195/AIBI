"""
SQLAlchemy database connection manager for CSV backend.

Uses SQLAlchemy 2.0 with PostgreSQL for all database operations.
"""

import logging
from typing import Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """SQLAlchemy database connection manager"""
    
    _engine: Optional[object] = None
    _session_factory: Optional[object] = None
    
    @classmethod
    def init_db(cls) -> None:
        """Initialize SQLAlchemy engine and session factory"""
        if cls._engine is None:
            try:
                database_url = settings.get_database_url()
                
                # Create engine with connection pool
                cls._engine = create_engine(
                    database_url,
                    poolclass=QueuePool,
                    pool_size=max(settings.db_pool_size, 5),
                    max_overflow=10,
                    echo=settings.debug,  # Log SQL statements in debug mode
                    future=True,  # Use SQLAlchemy 2.0 behavior
                )
                
                # Create session factory
                cls._session_factory = sessionmaker(
                    bind=cls._engine,
                    class_=Session,
                    expire_on_commit=False,
                )
                
                logger.info("✅ SQLAlchemy database initialized successfully")
                
                # Create all tables if they don't exist
                cls.create_tables()
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize SQLAlchemy database: {e}")
                cls._engine = None
                cls._session_factory = None
                raise
    
    @classmethod
    def create_tables(cls) -> None:
        """Create all tables defined in models"""
        try:
            # Import models here to avoid circular imports
            from app.models.database_models import Base
            Base.metadata.create_all(bind=cls._engine)
            logger.info("✅ All database tables created/verified")
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
            raise
    
    @classmethod
    def get_session(cls) -> Session:
        """Get a new database session"""
        if cls._session_factory is None:
            cls.init_db()
        return cls._session_factory()
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """Context manager for database connections (for backward compatibility)"""
        session = cls.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @classmethod
    def test_connection(cls) -> bool:
        """Test database connection"""
        try:
            if cls._engine is None:
                cls.init_db()
            
            with cls._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    @classmethod
    def close(cls) -> None:
        """Close all connections in the pool"""
        if cls._engine:
            cls._engine.dispose()
            logger.info("Database connections closed")


# Create module-level reference to engine that will be populated on init_db
engine = None


def _init_engine():
    """Initialize and return the engine (for module-level access)"""
    if DatabaseConnection._engine is None:
        DatabaseConnection.init_db()
    return DatabaseConnection._engine


# Monkey patch to make DatabaseConnection.engine work
def _get_engine_property():
    if DatabaseConnection._engine is None:
        DatabaseConnection.init_db()
    return DatabaseConnection._engine


# Add a property-like method to get the engine
class_init = DatabaseConnection.init_db


def init_and_get_engine():
    """Convenient function to initialize DB and get engine"""
    DatabaseConnection.init_db()
    return DatabaseConnection._engine