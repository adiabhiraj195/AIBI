from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
import asyncio
import uvicorn
from contextlib import asynccontextmanager

# Import application components
from app.config import settings
from app.controllers.csv_controller import router as csv_router
from app.controllers.metadata_controller import router as metadata_router
from app.controllers.auth_controller import router as auth_router
from app.middleware.cors import add_cors_middleware
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.database.connection import DatabaseConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting CSV Upload and Preview API")
    
    # Initialize SQLAlchemy database with connection pooling and auto-create tables
    try:
        DatabaseConnection.init_db()
        logger.info("✅ SQLAlchemy database initialized with connection pooling")
        
        # Test database connection (with retry logic)
        max_retries = 3
        for attempt in range(max_retries):
            if DatabaseConnection.test_connection():
                logger.info("✅ Database connection successful")
                break
            else:
                if attempt < max_retries - 1:
                    logger.warning(f"Database connection attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(2)
                else:
                    logger.error("❌ Database connection failed after retries - app may not function properly")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}", exc_info=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down CSV Upload and Preview API")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-grade API for CSV file upload, preview, and management with Supabase integration",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
add_cors_middleware(app)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth_router)
app.include_router(csv_router)
app.include_router(metadata_router)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    db_status = DatabaseConnection.test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": settings.app_version
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level="info"
    )