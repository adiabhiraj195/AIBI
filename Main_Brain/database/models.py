"""
Database models for Multi-Agent Chatbot Copilot
Pydantic models for database operations and data validation
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class QueryIntent(str, Enum):
    """Query intent classification"""
    VISUALIZATION = "visualization"
    INSIGHTS = "insights"
    FORECASTING = "forecasting"
    GENERAL = "general"

class ConversationHistory(BaseModel):
    """Model for conversation history records"""
    id: Optional[int] = None
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    user_query: str = Field(..., description="Original user query")
    agent_response: Dict[str, Any] = Field(..., description="Complete agent response")
    query_intent: Optional[QueryIntent] = Field(None, description="Classified query intent")
    execution_time: Optional[float] = Field(None, description="Response time in seconds")
    created_at: Optional[datetime] = Field(None, description="Timestamp of interaction")
    
    class Config:
        from_attributes = True

class PredictionCache(BaseModel):
    """Model for cached ML predictions"""
    id: Optional[int] = None
    query_hash: str = Field(..., description="Hash of query parameters")
    model_type: str = Field(..., description="Type of ML model used")
    prediction: Dict[str, Any] = Field(..., description="Prediction results")
    confidence: Optional[float] = Field(None, description="Prediction confidence score")
    created_at: Optional[datetime] = Field(None, description="Cache creation time")
    expires_at: Optional[datetime] = Field(None, description="Cache expiration time")
    
    class Config:
        from_attributes = True
        protected_namespaces = ()

class RAGDocument(BaseModel):
    """Model for RAG embedding documents"""
    doc_id: int = Field(..., description="Unique document identifier")
    source_file: Optional[str] = Field(None, description="Source file name")
    data_type: Optional[str] = Field(None, description="Type of data")
    business_context: Optional[str] = Field(None, description="Business context")
    customer_name: Optional[str] = Field(None, description="Customer name")
    state: Optional[str] = Field(None, description="State/region")
    formatted_period: Optional[str] = Field(None, description="Time period")
    project_phase: Optional[str] = Field(None, description="Project phase")
    fiscalyear: Optional[str] = Field(None, description="Fiscal year")
    ryear: Optional[str] = Field(None, description="Report year")
    business_module: Optional[str] = Field(None, description="Business module")
    wtg_model: Optional[str] = Field(None, description="Wind turbine model")
    wtg_type: Optional[str] = Field(None, description="Wind turbine type")
    capacity: Optional[float] = Field(None, description="Capacity in MW")
    model_bucket: Optional[str] = Field(None, description="Model bucket category")
    wtg_count: Optional[float] = Field(None, description="Wind turbine count")
    mwg: Optional[float] = Field(None, description="Megawatt generation")
    wtg_count_deviation: Optional[float] = Field(None, description="WTG deviation")
    mwg_deviation: Optional[float] = Field(None, description="MWG deviation")
    content: str = Field(..., description="Document content for embedding")
    similarity_score: Optional[float] = Field(None, description="Similarity score from search")
    
    class Config:
        from_attributes = True
        protected_namespaces = ()

class DatabaseStats(BaseModel):
    """Model for database statistics"""
    total_embeddings: int = Field(..., description="Total number of embeddings")
    business_modules: List[Dict[str, Any]] = Field(default_factory=list, description="Business module counts")
    top_states: List[Dict[str, Any]] = Field(default_factory=list, description="Top states by count")
    capacity_stats: Dict[str, Any] = Field(default_factory=dict, description="Capacity statistics")

class DatabaseStatus(BaseModel):
    """Model for database connection status"""
    status: str = Field(..., description="Connection status")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database name")
    version: Optional[str] = Field(None, description="PostgreSQL version")
    pgvector_installed: Optional[bool] = Field(None, description="pgvector extension status")
    rag_table_exists: Optional[bool] = Field(None, description="RAG table existence")
    embedding_count: Optional[int] = Field(None, description="Number of embeddings")
    error: Optional[str] = Field(None, description="Error message if failed")