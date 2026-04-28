# Backend Development Quickstart

## TL;DR for Backend Developer (Kiro)

The frontend is **100% ready** for your backend. Here's what you need to build:

## Required Endpoint

### POST /api/query

**This is the only critical endpoint for MVP.**

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.post("/api/query")
async def process_query(request: QueryRequest):
    """
    Process user query through 5-agent LangGraph pipeline.
    Stream results back as Server-Sent Events.
    """
    return StreamingResponse(
        query_processor_stream(request),
        media_type="text/event-stream"
    )
```

## Expected Request

```json
{
  "query": "What was the revenue for Q3 2024?",
  "session_id": "session_1698765432000",
  "user_id": "demo_user"
}
```

## Expected Response (Streamed via SSE)

```json
{
  "query_intent": {
    "intent_type": "insights",
    "confidence": 0.92,
    "entities": ["Q3 2024", "revenue"],
    "temporal_scope": "Q3 2024"
  },
  "agent_responses": [
    {
      "agent_name": "Visualization",
      "content": "Generated revenue trend chart",
      "visualizations": [{
        "type": "line",
        "data": [...],
        "layout": {...}
      }],
      "confidence": 0.94,
      "execution_time": 780,
      "follow_up_questions": []
    },
    {
      "agent_name": "Insights",
      "content": "Q3 2024 revenue reached ₹228.6 Cr, marking a 23% increase from Q2...",
      "visualizations": [],
      "confidence": 0.89,
      "execution_time": 870,
      "follow_up_questions": [
        "What is the breakdown of revenue by E3 vs E4 turbine models?",
        "How do profit margins compare across different customer segments?",
        "Show me the geographic distribution of installations by state",
        "What are the top 5 customers by revenue contribution?"
      ],
      "cfo_response": {
        "summary": "Q3 2024 revenue reached ₹228.6 Cr, marking a 23% increase from Q2 and 18.9% YoY growth. E4 turbines drive 72% of total revenue with improving profit margins of 23.7%. Installation numbers increased 24% YoY, indicating strong market demand. The operational pipeline shows 70 active projects totaling 2,100 MW capacity across all phases.",
        "key_metrics": [
          {
            "name": "Q3 2024 Revenue",
            "value": "228.6",
            "unit": "₹ Cr",
            "trend": "increasing",
            "significance": "high"
          }
        ],
        "recommendations": [
          "Scale E4 production capacity to meet Q4 demand projections of 22+ installations"
        ],
        "risk_flags": [
          "Customer concentration: Top 5 customers represent 64% of revenue"
        ]
      }
    }
  ],
  "processing_stages": [
    {
      "agent_name": "Orchestrator",
      "status": "completed",
      "duration": 380,
      "output": "Routed to insights agent"
    },
    {
      "agent_name": "Visualization",
      "status": "completed",
      "duration": 780,
      "output": "Generated 1 chart(s)"
    },
    {
      "agent_name": "Insights",
      "status": "completed",
      "duration": 870,
      "output": "Generated CFO-grade insights"
    },
    {
      "agent_name": "Follow-Up",
      "status": "completed",
      "duration": 480,
      "output": "Generated 4 contextual follow-up questions"
    }
  ],
  "total_execution_time": 2510,
  "timestamp": "2024-10-30T14:32:15.123Z"
}
```

## The 5 Agents You Need to Build

### 1. Orchestrator Agent (~400ms)
- **Purpose**: Route queries to correct specialized agents
- **Output**: `query_intent` with type (visualization/insights/forecasting/general)
- **Key Logic**: Keyword detection for routing

### 2. Visualization Agent (~800ms)
- **Purpose**: Generate Plotly charts
- **Supported Types**: bar, line, heatmap, choropleth, scatter, bubble, pie, waterfall, treemap, box, funnel, sankey
- **Output**: `visualizations` array with Plotly format

### 3. Insights Agent (~900ms)
- **Purpose**: CFO-grade analysis
- **Output**: `cfo_response` with:
  - `summary`: Exactly 4-5 lines
  - `key_metrics`: Up to 4 metrics with trends
  - `recommendations`: 3-4 strategic actions
  - `risk_flags`: 1-3 risk indicators

### 4. Forecasting Agent (~1200ms, conditional)
- **Purpose**: Predictions using Prophet/XGBoost
- **Triggers**: Queries with "forecast", "predict", "what if", "scenario"
- **Output**: `forecast_data` with predictions and confidence intervals

### 5. Follow-Up Agent (~500ms)
- **Purpose**: Generate contextual questions
- **Output**: Exactly 4 questions
- **Categories**: Strategic, Operational, Financial, Technical

## Critical Requirements

### ✅ Must-Have
1. **CFO Summary**: Exactly 4-5 lines (not more, not less)
2. **Follow-Up Questions**: Exactly 4 questions (always)
3. **Key Metrics**: Maximum 4 metrics with trends
4. **Response Time**: < 5 seconds for 95% of queries
5. **Streaming**: Use SSE to stream processing stages in real-time

### ⚠️ Nice-to-Have (Can Come Later)
- Conversation memory (Redis)
- Quality reflection/improvement loop
- Advanced error handling
- Caching layer

## Database Connection

```python
# PostgreSQL with pgvector
host = "34.232.69.47"
port = 5432
database = "Prescience_Dev"

# Expected table: rag_embeddings
# Should have 105,984 records with 21 columns
```

## Pydantic Models (Match Frontend Types)

```python
from pydantic import BaseModel
from enum import Enum

class AgentType(str, Enum):
    ORCHESTRATOR = "Orchestrator"
    VISUALIZATION = "Visualization"
    INSIGHTS = "Insights"
    FORECASTING = "Forecasting"
    FOLLOWUP = "Follow-Up"

class QueryIntentType(str, Enum):
    VISUALIZATION = "visualization"
    INSIGHTS = "insights"
    FORECASTING = "forecasting"
    GENERAL = "general"

class KeyMetric(BaseModel):
    name: str
    value: str | float
    unit: str
    trend: str  # "increasing" | "decreasing" | "stable"
    significance: str  # "high" | "medium" | "low"

class CFOResponse(BaseModel):
    summary: str  # 4-5 lines
    key_metrics: list[KeyMetric]
    recommendations: list[str]
    risk_flags: list[str]

class AgentResponse(BaseModel):
    agent_name: AgentType
    content: str
    visualizations: list[dict]
    confidence: float
    execution_time: int
    follow_up_questions: list[str]
    cfo_response: CFOResponse | None = None
    forecast_data: dict | None = None

class AgentStage(BaseModel):
    agent_name: AgentType
    status: str  # "pending" | "processing" | "completed" | "error"
    duration: int | None = None
    output: str | None = None

class QueryRequest(BaseModel):
    query: str
    session_id: str
    user_id: str | None = None

class QueryResponse(BaseModel):
    query_intent: dict
    agent_responses: list[AgentResponse]
    conversation_context: dict
    processing_stages: list[AgentStage]
    total_execution_time: int
    timestamp: str
```

## LangGraph Setup (Minimal)

```python
from langgraph.graph import StateGraph

# Define agent workflow
workflow = StateGraph()

# Add nodes (agents)
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("visualization", visualization_agent)
workflow.add_node("insights", insights_agent)
workflow.add_node("forecasting", forecasting_agent)
workflow.add_node("followup", followup_agent)

# Add edges (routing)
workflow.set_entry_point("orchestrator")
workflow.add_conditional_edges(
    "orchestrator",
    route_to_agents,  # Your routing function
    {
        "visualization": "visualization",
        "insights": "insights",
        "forecasting": "forecasting"
    }
)
workflow.add_edge("visualization", "insights")
workflow.add_edge("insights", "followup")
workflow.add_edge("forecasting", "followup")
workflow.add_edge("followup", END)

# Compile
app = workflow.compile()
```

## Testing the Integration

### 1. Start Your Backend
```bash
uvicorn main:app --reload --port 8000
```

### 2. Update Frontend .env
```bash
VITE_API_URL=http://localhost:8000
```

### 3. Test with Dashboard Queries
Use the 7 pre-configured queries from dashboard cards:
- "Show me revenue realization breakdown by project phase"
- "Analyze current cash flow position and forecast next 90-day runway"
- etc.

### 4. Verify Response Format
- ✅ Summary is 4-5 lines
- ✅ Exactly 4 follow-up questions
- ✅ Key metrics have trend indicators
- ✅ Processing stages stream in real-time
- ✅ Total time < 5 seconds

## Quick Wins for MVP

### Phase 1: Basic Response (1-2 days)
1. Static response matching the format
2. No real AI, just return mock data
3. Verify frontend displays correctly

### Phase 2: RAG Integration (2-3 days)
1. Connect to pgvector database
2. Retrieve relevant embeddings
3. Use in prompt context

### Phase 3: Real Agents (3-5 days)
1. Implement Orchestrator routing
2. Add Visualization agent (generate Plotly JSON)
3. Add Insights agent (LLM-generated CFO summary)
4. Add Follow-Up agent (generate 4 questions)

### Phase 4: ML Models (2-3 days)
1. Load Prophet model
2. Load XGBoost model
3. Integrate Forecasting agent

## Common Pitfalls to Avoid

❌ **DON'T**:
- Return more or less than 4-5 lines for CFO summary
- Generate more or less than 4 follow-up questions
- Include more than 4 key metrics
- Take longer than 5 seconds for most queries
- Forget to stream processing stages

✅ **DO**:
- Match the Pydantic models exactly
- Stream responses via SSE
- Include execution times for each agent
- Set proper CORS headers for frontend
- Test with actual dashboard queries

## Files to Reference

1. **`/BACKEND_INTEGRATION.md`**: Complete API specification
2. **`/types/index.ts`**: Frontend TypeScript types (must match your Pydantic)
3. **`/services/api.ts`**: Frontend API client (shows expected format)

## Support

Frontend is ready. Just build backend matching the types in `/types/index.ts` and you're done!

**Key Success Metric**: Dashboard card click → Query submitted → 5 agents process → CFO response displayed in < 5 seconds

Good luck! 🚀
