"""
Multi-Agent Chatbot Copilot - FastAPI Application
Provides CFO-grade financial insights with multi-agent orchestration
"""

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration and logging
from config import settings
from logging_config import setup_logging, get_logger
from models import (
    SystemStatus, DatabaseStatus, ErrorResponse,
    ConversationContextResponse, SessionSummaryResponse, MemoryStatsResponse,
    ConversationTurnResponse, QueryRequest, QueryResponse, AgentStage, 
    AgentStageStatus, QueryIntentType, CFOResponse, KeyMetric,
    FeedbackRequest, FeedbackResponse, DashboardItem, DashboardItemCreate
)

# Setup logging
setup_logging()
logger = get_logger("main")

# Import application modules
from agents.memory import conversation_memory
from agents.orchestrator import orchestrator_agent
from database.connection import db_manager
from rag.system import rag_system
from rag.embedding import EmbeddingManager
from services.data_sync_manager import data_sync_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Multi-Agent Chatbot Copilot...")
    
    try:
        # Initialize conversation memory
        await conversation_memory.initialize()
        
        # Initialize database connections
        await db_manager.initialize()
        
        # Create necessary tables
        await db_manager.create_tables()
        
        # Initialize RAG system
        await rag_system.initialize()
        
        # Ensure RAG embeddings table exists
        embedding_manager = EmbeddingManager()
        embedding_manager.create_embeddings_table()
        
        # Initialize data sync manager (monitors new CSV uploads)
        await data_sync_manager.initialize()
        
        # Initialize orchestrator agent
        await orchestrator_agent.initialize()
        
        logger.info("✅ Application startup complete")
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down application...")
    try:
        # Cleanup resources here
        await data_sync_manager.cleanup()
        await conversation_memory.cleanup()
        await orchestrator_agent.cleanup()
        await db_manager.cleanup()
        
        logger.info("✅ Application shutdown complete")
    except Exception as e:
        logger.error(f"❌ Application shutdown failed: {str(e)}")

# Create FastAPI application
app = FastAPI(
    title="Multi-Agent Chatbot Copilot",
    description="CFO-grade financial insights with multi-agent orchestration for AIBI wind turbine data",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Open to all origins for MVP deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for MVP
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "multi-agent-chatbot-copilot",
        "version": "1.0.0"
    }

# System status endpoint
@app.get("/api/system/status", response_model=SystemStatus)
async def system_status():
    """System status endpoint showing service information"""
    return SystemStatus(
        status="operational",
        agents={
            "orchestrator": "ready",
            "insights": "ready", 
            "visualization": "ready",
            "forecasting": "ready",
            "follow_up": "ready"
        },
        database="connected",
        rag_system="initialized"
    )

# Database status endpoint
@app.get("/api/system/database", response_model=DatabaseStatus)
async def database_status():
    """Database status endpoint showing connection info and embedding count"""
    try:
        # Get database status from db_manager
        db_status = await db_manager.get_status()
        
        return DatabaseStatus(
            status=db_status.get("status", "unknown"),
            host=db_status.get("host", "unknown"),
            database=db_status.get("database", "unknown"),
            embedding_count=db_status.get("embedding_count", 0),
            tables=db_status.get("tables", [])
        )
        
    except Exception as e:
        logger.error(f"Failed to get database status: {str(e)}")
        return DatabaseStatus(
            status="error",
            host="unknown",
            database="unknown", 
            embedding_count=0,
            tables=[]
        )

# Main query endpoint with orchestrator integration
@app.post("/api/query")
async def process_query(request: QueryRequest):
    """Main query processing endpoint with orchestrator routing"""
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        # Create query context
        from agents.base import QueryContext
        context = QueryContext(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        # Process query through orchestrator
        start_time = datetime.utcnow()
        agent_response = await orchestrator_agent.process(context)
        end_time = datetime.utcnow()

        
        
        # Determine intent based on handler used
        handler = agent_response.metadata.get("handler", "general")
        if handler == "nl2sql_agent":
            intent = QueryIntentType.INSIGHTS
        elif handler == "statistical_handler":
            intent = QueryIntentType.INSIGHTS
        elif handler == "rag_semantic_search":
            intent = QueryIntentType.GENERAL
        else:
            intent = QueryIntentType.GENERAL
        
        print(handler, "handler")
        # Create agent stage information
        agent_stages = [
            AgentStage(
                agent_name="orchestrator",
                status=AgentStageStatus.COMPLETED,
                message=f"Query processed using {handler}",
                execution_time=agent_response.execution_time
            )
        ]
        
        # Create CFO response for successful insights
        cfo_response = None
        if agent_response.confidence >= 0.7 and intent == QueryIntentType.INSIGHTS:
            # Extract key metrics from response content
            key_metrics = []
            if "capacity" in agent_response.content.lower():
                key_metrics.append(
                    KeyMetric(
                        name="Portfolio Capacity",
                        value="Analysis provided",
                        unit="MW",
                        trend="stable",
                        significance="high"
                    )
                )
            
            # Don't create CFO response with generic data
            cfo_response = None

        
        # Calculate total execution time
        total_execution_time = (end_time - start_time).total_seconds()
        
        # Create response
        response = QueryResponse(
            query=request.query,
            intent=intent,
            session_id=request.session_id,
            agent_stages=agent_stages,
            primary_agent="orchestrator",
            content=agent_response.content,
            cfo_response=cfo_response,
            visualizations=agent_response.visualizations,  # Populated by VisualizationAgent
            follow_up_questions=[],  # Will be populated by FollowUpAgent in future tasks
            confidence=agent_response.confidence,
            total_execution_time=total_execution_time,
            metadata=agent_response.metadata
        )
        
        logger.info(f"Query processed successfully in {total_execution_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Query processing failed: {str(e)}"
        )

# Conversation management endpoints
@app.get("/api/conversation/{session_id}", response_model=ConversationContextResponse)
async def get_conversation(session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    try:
        context = await conversation_memory.get_context(session_id, lookback=limit)
        
        # Convert to response format
        turns = []
        for turn in context.turns:
            # Convert visualization dicts to PlotlyChart objects
            visualizations = []
            if turn.agent_response.visualizations:
                from models import PlotlyChart
                for viz_data in turn.agent_response.visualizations:
                    if isinstance(viz_data, dict):
                        visualizations.append(PlotlyChart(**viz_data))
                    else:
                        visualizations.append(viz_data)
            
            turns.append(ConversationTurnResponse(
                turn_id=turn.turn_id,
                timestamp=turn.timestamp,
                user_query=turn.user_query,
                agent_response=turn.agent_response.content,
                visualizations=visualizations,
                session_id=turn.session_id,
                user_id=turn.user_id
            ))
        
        return ConversationContextResponse(
            session_id=context.session_id,
            user_id=context.user_id,
            turns=turns,
            current_topic=context.current_topic,
            turn_count=len(context.turns),
            last_activity=context.turns[-1].timestamp if context.turns else None
        )
        
    except Exception as e:
        logger.error(f"Failed to get conversation {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")

@app.delete("/api/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    try:
        success = await conversation_memory.clear_session(session_id)
        if success:
            return {"message": f"Conversation {session_id} cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear conversation")
            
    except Exception as e:
        logger.error(f"Failed to clear conversation {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")

@app.get("/api/conversation/{session_id}/summary", response_model=SessionSummaryResponse)
async def get_conversation_summary(session_id: str):
    """Get conversation summary for a session"""
    try:
        summary = await conversation_memory.summarize_session(session_id)
        
        return SessionSummaryResponse(
            session_id=summary.session_id,
            user_id=summary.user_id,
            start_time=summary.start_time,
            last_activity=summary.last_activity,
            turn_count=summary.turn_count,
            topics=summary.topics,
            key_metrics_discussed=summary.key_metrics_discussed
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get conversation summary {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation summary: {str(e)}")

@app.get("/api/memory/stats", response_model=MemoryStatsResponse)
async def get_memory_stats():
    """Get conversation memory system statistics"""
    try:
        stats = await conversation_memory.get_memory_stats()
        
        return MemoryStatsResponse(
            redis_connected=stats.get("redis_connected", False),
            active_sessions=stats.get("active_sessions", 0),
            total_turns=stats.get("total_turns", 0),
            total_users=stats.get("total_users", 0),
            memory_usage_mb=stats.get("memory_usage_mb", 0.0),
            session_timeout=stats.get("session_timeout", 3600),
            memory_limit_per_session=stats.get("memory_limit_per_session", 10)
        )
        
    except Exception as e:
        logger.error(f"Failed to get memory stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get memory stats: {str(e)}")

@app.get("/api/user/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    """Get all session IDs for a user"""
    try:
        sessions = await conversation_memory.get_user_sessions(user_id)
        return {"user_id": user_id, "sessions": sessions}
        
    except Exception as e:
        logger.error(f"Failed to get user sessions for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user sessions: {str(e)}")

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback (thumbs up/down) for a response"""
    try:
        logger.info(f"Received feedback: {request.feedback} for query: {request.query[:50]}...")
        
        # Validate feedback value
        if request.feedback not in ["thumbs_up", "thumbs_down"]:
            raise HTTPException(
                status_code=400, 
                detail="Feedback must be either 'thumbs_up' or 'thumbs_down'"
            )
        
        # Save feedback to database
        async with db_manager.get_connection() as conn:
            feedback_id = await conn.fetchval("""
                INSERT INTO feedback (query, response, feedback, created_at)
                VALUES ($1, $2, $3, NOW())
                RETURNING id
            """, request.query, request.response, request.feedback)
            
            logger.info(f"Feedback saved successfully with ID: {feedback_id}")
            
            return FeedbackResponse(
                success=True,
                message="Feedback submitted successfully",
                feedback_id=feedback_id
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save feedback: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save feedback: {str(e)}"
        )


        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save feedback: {str(e)}"
        )


# ==================== DASHBOARD ENDPOINTS ====================

@app.post("/api/dashboard/save", response_model=DashboardItem)
async def save_dashboard_item(item: DashboardItemCreate):
    """Save a visualization to the dashboard"""
    try:
        logger.info(f"Received dashboard save request: {item.model_dump()}")
        if not item.user_id:
             raise HTTPException(status_code=400, detail="User ID is required")
             
        async with db_manager.get_connection() as conn:
            # Serialize dicts to JSON string for storage as asyncpg requires string for JSONB if not configured
            viz_data_json = json.dumps(item.visualization_data)
            layout_json = json.dumps(item.layout) if item.layout else None

            row = await conn.fetchrow("""
                INSERT INTO dashboard_items 
                (user_id, title, description, visualization_data, layout, category, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                RETURNING id, user_id, title, description, visualization_data, layout, category, created_at
            """, item.user_id, item.title, item.description, 
                 viz_data_json,
                 layout_json, item.category)
            
            if not row:
                raise HTTPException(status_code=500, detail="Failed to save dashboard item")
                
            return DashboardItem(
                id=row['id'],
                user_id=row['user_id'],
                title=row['title'],
                description=row['description'],
                visualization_data=json.loads(row['visualization_data']) if isinstance(row['visualization_data'], str) else row['visualization_data'],
                layout=json.loads(row['layout']) if row['layout'] and isinstance(row['layout'], str) else row['layout'],
                category=row['category'],
                created_at=row['created_at']
            )
            
    except Exception as e:
        import traceback
        error_msg = f"Failed to save dashboard item: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/dashboard/items", response_model=List[DashboardItem])
async def get_dashboard_items(user_id: str):
    """Get all dashboard items for a user"""
    try:
        async with db_manager.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT id, user_id, title, description, visualization_data, layout, category, created_at
                FROM dashboard_items
                WHERE user_id = $1
                ORDER BY created_at DESC
            """, user_id)
            
            items = []
            for row in rows:
                items.append(DashboardItem(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    description=row['description'],
                    visualization_data=json.loads(row['visualization_data']) if isinstance(row['visualization_data'], str) else row['visualization_data'],
                    layout=json.loads(row['layout']) if row['layout'] and isinstance(row['layout'], str) else row['layout'],
                    category=row['category'],
                    created_at=row['created_at']
                ))
            
            return items
            
    except Exception as e:
        logger.error(f"Failed to get dashboard items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard items: {str(e)}")


@app.delete("/api/dashboard/delete/{item_id}")
async def delete_dashboard_item(item_id: int, user_id: str):
    """Delete a dashboard item"""
    try:
        async with db_manager.get_connection() as conn:
            result = await conn.execute("""
                DELETE FROM dashboard_items
                WHERE id = $1 AND user_id = $2
            """, item_id, user_id)
            
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Item not found or access denied")
                
            return {"success": True, "message": "Item deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dashboard item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete dashboard item: {str(e)}")


# ==================== DATA SYNC ENDPOINTS ====================

@app.post("/api/v1/admin/sync/trigger")
async def trigger_manual_sync():
    """Manually trigger data synchronization from backend to RAG system"""
    try:
        logger.info("🔔 Manual sync triggered by admin")
        result = await data_sync_manager.sync_new_documents()
        return {
            "success": True,
            "message": "Manual sync triggered",
            "result": result
        }
    except Exception as e:
        logger.error(f"❌ Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.get("/api/v1/admin/sync/status")
async def get_sync_status():
    """Get current sync status and statistics"""
    try:
        async with db_manager.get_connection() as conn:
            # Get sync state
            sync_state = await conn.fetchrow(
                """
                SELECT * FROM data_sync_state
                WHERE service_name = 'AIBI-copilot-main-brain'
                """
            )

            if not sync_state:
                raise HTTPException(
                    status_code=404, 
                    detail="Sync state not found - service may not be initialized"
                )

            # Get document statistics
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(CASE WHEN is_processed_by_rag THEN 1 END) as processed_documents,
                    COUNT(CASE WHEN NOT is_processed_by_rag THEN 1 END) as pending_documents,
                    MAX(created_at) as latest_upload,
                    MAX(rag_processed_at) as latest_processed
                FROM csv_documents
                """
            )

            return {
                "sync_state": {
                    "service_name": sync_state['service_name'],
                    "status": sync_state['status'],
                    "last_sync_timestamp": sync_state['last_sync_timestamp'].isoformat() if sync_state['last_sync_timestamp'] else None,
                    "error_message": sync_state['error_message'],
                    "updated_at": sync_state['updated_at'].isoformat() if sync_state['updated_at'] else None
                },
                "statistics": {
                    "total_documents": stats['total_documents'],
                    "processed_documents": stats['processed_documents'],
                    "pending_documents": stats['pending_documents'],
                    "latest_upload": stats['latest_upload'].isoformat() if stats['latest_upload'] else None,
                    "latest_processed": stats['latest_processed'].isoformat() if stats['latest_processed'] else None
                },
                "sync_health": "healthy" if stats['pending_documents'] == 0 else f"⏳ {stats['pending_documents']} documents pending"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sync status: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get sync status: {str(e)}"
        )


@app.get("/api/v1/admin/sync/pending")
async def get_pending_documents(limit: int = 20):
    """Get list of documents pending RAG processing"""
    try:
        async with db_manager.get_connection() as conn:
            pending = await conn.fetch(
                """
                SELECT 
                    id, filename, created_at, row_count, column_count,
                    CASE WHEN is_processed_by_rag THEN 'processed' ELSE 'pending' END as status
                FROM csv_documents
                WHERE is_processed_by_rag = FALSE
                ORDER BY created_at DESC
                LIMIT $1
                """,
                limit
            )

            return {
                "count": len(pending),
                "pending_documents": [dict(doc) for doc in pending]
            }
    except Exception as e:
        logger.error(f"Failed to get pending documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pending documents: {str(e)}"
        )


if __name__ == "__main__":
    logger.info(f"🌟 Starting server on {settings.host}:{settings.port}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info(f"🌐 CORS enabled for React frontend at localhost:5173")
    logger.info(f"📊 Database: {settings.database.host}:{settings.database.port}/{settings.database.name}")
    logger.info(f"🤖 LLM Model: {settings.llm.model}")
    logger.info(f"🔄 Data Sync Manager: Auto-syncing new uploads every 5 minutes")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )