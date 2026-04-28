"""
Pydantic models for Multi-Agent Chatbot Copilot
Defines request/response schemas and data structures
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class QueryIntentType(str, Enum):
    """Query intent classification types"""
    VISUALIZATION = "visualization"
    INSIGHTS = "insights" 
    FORECASTING = "forecasting"
    GENERAL = "general"

class AgentStageStatus(str, Enum):
    """Agent processing stage status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class QuestionCategory(str, Enum):
    """Follow-up question categories"""
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    TECHNICAL = "technical"

class ChartType(str, Enum):
    """Supported chart types for visualization"""
    BAR = "bar"
    STACKED_BAR = "stacked_bar"
    LINE = "line"
    HEATMAP = "heatmap"
    CHOROPLETH = "choropleth"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    PIE = "pie"
    DONUT = "donut"
    WATERFALL = "waterfall"
    TREEMAP = "treemap"
    BOX = "box"
    FUNNEL = "funnel"
    SANKEY = "sankey"

# Request Models
class QueryRequest(BaseModel):
    """Request model for query processing"""
    query: str = Field(..., description="User query text")
    session_id: str = Field(..., description="Session identifier for conversation context")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional request metadata")

# Response Models
class KeyMetric(BaseModel):
    """Key financial metric structure"""
    name: str = Field(..., description="Metric name")
    value: Union[float, str] = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    trend: str = Field(..., description="Trend direction: increasing, decreasing, stable")
    significance: str = Field(..., description="Significance level: high, medium, low")

class CFOResponse(BaseModel):
    """CFO-grade response structure"""
    summary: str = Field(..., description="4-5 line executive summary")
    key_metrics: List[KeyMetric] = Field(default_factory=list, description="Key financial metrics")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    risk_flags: List[str] = Field(default_factory=list, description="Risk indicators and warnings")

class PlotlyChart(BaseModel):
    """Plotly chart structure"""
    type: str = Field(..., description="Type of chart (bar, line, pie, scatter, etc.)")
    data: Dict[str, Any] = Field(..., description="Plotly chart data with traces")
    layout: Dict[str, Any] = Field(..., description="Plotly chart layout")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Plotly chart configuration")

class FollowUpQuestion(BaseModel):
    """Follow-up question structure"""
    question: str = Field(..., description="Follow-up question text")
    category: QuestionCategory = Field(..., description="Question category")
    priority: int = Field(..., ge=1, le=4, description="Question priority (1-4)")

class AgentStage(BaseModel):
    """Agent processing stage information"""
    agent_name: str = Field(..., description="Name of the agent")
    status: AgentStageStatus = Field(..., description="Current processing status")
    message: Optional[str] = Field(None, description="Status message or description")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    error: Optional[str] = Field(None, description="Error message if status is error")

class QueryResponse(BaseModel):
    """Complete query response structure"""
    query: str = Field(..., description="Original user query")
    intent: QueryIntentType = Field(..., description="Classified query intent")
    session_id: str = Field(..., description="Session identifier")
    
    # Agent processing information
    agent_stages: List[AgentStage] = Field(default_factory=list, description="Agent processing stages")
    primary_agent: str = Field(..., description="Primary agent that handled the query")
    
    # Response content
    content: str = Field(..., description="Main response content")
    cfo_response: Optional[CFOResponse] = Field(None, description="CFO-grade structured response")
    visualizations: List[PlotlyChart] = Field(default_factory=list, description="Generated charts and visualizations")
    follow_up_questions: List[FollowUpQuestion] = Field(default_factory=list, description="Contextual follow-up questions")
    
    # Metadata
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence score")
    total_execution_time: float = Field(..., description="Total processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional response metadata")

# Conversation Models
class ConversationMessage(BaseModel):
    """Individual conversation message"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Message metadata")

class ConversationHistory(BaseModel):
    """Conversation history structure"""
    session_id: str = Field(..., description="Session identifier")
    messages: List[ConversationMessage] = Field(default_factory=list, description="Conversation messages")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Conversation start time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")

class ConversationTurnResponse(BaseModel):
    """Response for a single conversation turn"""
    turn_id: str = Field(..., description="Unique turn identifier")
    timestamp: datetime = Field(..., description="Turn timestamp")
    user_query: str = Field(..., description="User query")
    agent_response: str = Field(..., description="Agent response content")
    visualizations: List[PlotlyChart] = Field(default_factory=list, description="Visualizations from this turn")
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")

class ConversationContextResponse(BaseModel):
    """Conversation context response"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    turns: List[ConversationTurnResponse] = Field(default_factory=list, description="Conversation turns")
    current_topic: Optional[str] = Field(None, description="Current conversation topic")
    turn_count: int = Field(..., description="Total number of turns")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")

class SessionSummaryResponse(BaseModel):
    """Session summary response"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    start_time: datetime = Field(..., description="Session start time")
    last_activity: datetime = Field(..., description="Last activity time")
    turn_count: int = Field(..., description="Number of conversation turns")
    topics: List[str] = Field(default_factory=list, description="Topics discussed")
    key_metrics_discussed: List[str] = Field(default_factory=list, description="Key metrics mentioned")

class MemoryStatsResponse(BaseModel):
    """Memory system statistics response"""
    redis_connected: bool = Field(..., description="Redis connection status")
    active_sessions: int = Field(..., description="Number of active sessions")
    total_turns: int = Field(..., description="Total conversation turns stored")
    total_users: int = Field(..., description="Total number of users")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    session_timeout: int = Field(..., description="Session timeout in seconds")
    memory_limit_per_session: int = Field(..., description="Memory limit per session")

# System Status Models
class DatabaseStatus(BaseModel):
    """Database connection status"""
    status: str = Field(..., description="Connection status")
    host: str = Field(..., description="Database host")
    database: str = Field(..., description="Database name")
    embedding_count: int = Field(..., description="Number of embeddings in rag_embeddings table")
    tables: List[str] = Field(default_factory=list, description="Available tables")

class AgentStatus(BaseModel):
    """Individual agent status"""
    name: str = Field(..., description="Agent name")
    status: str = Field(..., description="Agent status")
    initialized: bool = Field(..., description="Initialization status")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")

class SystemStatus(BaseModel):
    """Overall system status"""
    status: str = Field(..., description="Overall system status")
    agents: Dict[str, str] = Field(default_factory=dict, description="Agent status summary")
    database: str = Field(..., description="Database status")
    rag_system: str = Field(..., description="RAG system status")
    uptime: Optional[float] = Field(None, description="System uptime in seconds")

# Error Models
class ErrorResponse(BaseModel):
    """Error response structure"""
    error_type: str = Field(..., description="Error type classification")
    message: str = Field(..., description="Human-readable error message")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested user actions")
    fallback_response: Optional[str] = Field(None, description="Fallback response if available")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

# Forecasting Models
class ForecastRequest(BaseModel):
    """Forecasting request parameters"""
    target_variable: str = Field(..., description="Variable to forecast")
    horizon: int = Field(..., ge=1, description="Forecast horizon in periods")
    scenario_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="What-if scenario parameters")

class ForecastResult(BaseModel):
    """Forecasting result structure"""
    predictions: List[float] = Field(..., description="Forecast predictions")
    confidence_intervals: List[Dict[str, float]] = Field(default_factory=list, description="Confidence intervals")
    forecasting_model: str = Field(..., description="Model used for forecasting")
    accuracy_metrics: Optional[Dict[str, float]] = Field(default_factory=dict, description="Model accuracy metrics")

# Feedback Models
class FeedbackRequest(BaseModel):
    """User feedback request"""
    query: str = Field(..., description="Original user query")
    response: str = Field(..., description="Agent response that was rated")
    feedback: str = Field(..., description="Feedback type: thumbs_up or thumbs_down")
    session_id: Optional[str] = Field(None, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")

class FeedbackResponse(BaseModel):
    """Feedback submission response"""
    success: bool = Field(..., description="Whether feedback was saved successfully")
    message: str = Field(..., description="Response message")
    feedback_id: Optional[int] = Field(None, description="ID of saved feedback record")

# Dashboard Models
class DashboardItemCreate(BaseModel):
    """Request to create a dashboard item"""
    title: str = Field(..., description="Title of the visualization")
    description: Optional[str] = Field(None, description="Description")
    visualization_data: Dict[str, Any] = Field(..., description="Plotly chart data/layout")
    layout: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Grid layout information")
    user_id: Optional[str] = Field(None, description="User identifier")
    category: Optional[str] = Field("General", description="Category for grouping items")

class DashboardItem(BaseModel):
    """Dashboard item response"""
    id: int = Field(..., description="Item ID")
    user_id: Optional[str] = Field(None, description="User identifier")
    title: str = Field(..., description="Title")
    description: Optional[str] = Field(None, description="Description")
    visualization_data: Dict[str, Any] = Field(..., description="Visualization data")
    layout: Optional[Dict[str, Any]] = Field(None, description="Layout")
    created_at: datetime = Field(..., description="Creation time")
    category: Optional[str] = Field("General", description="Category for grouping items")