# Backend Integration Guide

## ⚠️ Important Update: Session Management Now Implemented

**This document has been updated to reflect the new session management features.**

For detailed session integration instructions, see:
- **`SESSION_INTEGRATION.md`** - Complete integration overview
- **`BACKEND_SESSION_INTEGRATION.md`** - Step-by-step backend guide  
- **`SESSION_MANAGEMENT_SUMMARY.md`** - Quick summary

## Overview

This document provides complete integration guidelines for connecting the frontend CFO Multi-Agent Chatbot to the Python FastAPI backend powered by LangGraph.

## Architecture Alignment

### Frontend Architecture
- **Framework**: React + TypeScript + Tailwind CSS
- **State Management**: React Hooks (useState, useEffect) + localStorage
- **API Layer**: `/services/api.ts` with streaming support
- **Type System**: `/types/index.ts` matching backend data models
- **Session Management**: Full session persistence and switching ✨ NEW

### Backend Architecture (Expected)
- **Framework**: FastAPI (Python)
- **Orchestration**: LangGraph multi-agent system
- **Database**: PostgreSQL with pgvector extension
- **ML Models**: Prophet (time-series) + XGBoost (scenarios)
- **Memory**: Redis for session management and conversation history ✨ UPDATED

## API Endpoints

### 1. Query Processing (Primary Endpoint)

**Endpoint**: `POST /api/query`

**Request Format**:
```typescript
{
  query: string;              // User's natural language query
  session_id: string;         // Unique session identifier
  user_id?: string;          // Optional user identifier
  context?: {                // Optional conversation context
    previous_queries: string[];
    previous_responses: AgentResponse[];
    current_topic?: string;
  }
}
```

**Response Format** (Server-Sent Events Stream):
```typescript
{
  query_intent: {
    intent_type: 'visualization' | 'insights' | 'forecasting' | 'general';
    confidence: number;
    entities: string[];
    temporal_scope?: string;
  };
  agent_responses: [{
    agent_name: 'Orchestrator' | 'Visualization' | 'Insights' | 'Forecasting' | 'Follow-Up';
    content: string;
    visualizations: PlotlyChart[];  // For Visualization Agent
    confidence: number;
    execution_time: number;
    follow_up_questions: string[];  // Exactly 4 questions
    cfo_response?: {               // For Insights Agent
      summary: string;             // 4-5 lines
      key_metrics: KeyMetric[];
      recommendations: string[];
      risk_flags: string[];
    };
    forecast_data?: {              // For Forecasting Agent
      model_type: 'prophet' | 'xgboost';
      predictions: any[];
      confidence_intervals?: {
        lower: number[];
        upper: number[];
      };
      scenario_params?: Record<string, any>;
    };
  }];
  conversation_context: {
    session_id: string;
    user_id: string;
    previous_queries: string[];
    previous_responses: AgentResponse[];
    current_topic?: string;
  };
  processing_stages: [{
    agent_name: 'Orchestrator' | 'Visualization' | 'Insights' | 'Forecasting' | 'Follow-Up';
    status: 'pending' | 'processing' | 'completed' | 'error';
    duration?: number;           // Milliseconds
    output?: string;             // Agent-specific output message
  }];
  total_execution_time: number;  // Total milliseconds
  timestamp: string;             // ISO 8601 format
}
```

### 2. System Health

**Endpoint**: `GET /health`

**Response**:
```typescript
{
  status: 'healthy' | 'degraded' | 'error';
  timestamp: string;
}
```

### 3. Database Status

**Endpoint**: `GET /api/system/database`

**Response**:
```typescript
{
  connected: boolean;
  host: string;
  database: string;
  embedding_count: number;      // Total RAG embeddings (should be 105,984)
  latency: number;              // Connection latency in ms
}
```

### 4. System Status

**Endpoint**: `GET /api/system/status`

**Response**:
```typescript
{
  apiHealth: boolean;
  dbConnected: boolean;
  ragSystemActive: boolean;
  modelsLoaded: boolean;        // Prophet + XGBoost loaded
  activeAgents: AgentType[];    // All 5 agents
}
```

### 5. Conversation History

**Endpoint**: `GET /api/conversation/:sessionId`

**Response**:
```typescript
{
  session_id: string;
  total_queries: number;
  messages: Message[];
  topics_covered: string[];
  start_time: string;
  last_activity: string;
}
```

### 6. Clear Conversation

**Endpoint**: `DELETE /api/conversation/:sessionId`

**Response**: `204 No Content`

## Data Type Definitions

All TypeScript interfaces are defined in `/types/index.ts`. Key types include:

### Core Types
```typescript
export enum AgentType {
  ORCHESTRATOR = 'Orchestrator',
  VISUALIZATION = 'Visualization',
  INSIGHTS = 'Insights',
  FORECASTING = 'Forecasting',
  FOLLOWUP = 'Follow-Up'
}

export enum QueryIntentType {
  VISUALIZATION = 'visualization',
  INSIGHTS = 'insights',
  FORECASTING = 'forecasting',
  GENERAL = 'general'
}

export enum ChartType {
  BAR = 'bar',
  STACKED_BAR = 'stacked_bar',
  LINE = 'line',
  HEATMAP = 'heatmap',
  CHOROPLETH = 'choropleth',
  SCATTER = 'scatter',
  BUBBLE = 'bubble',
  PIE = 'pie',
  DONUT = 'donut',
  WATERFALL = 'waterfall',
  TREEMAP = 'treemap',
  BOX = 'box',
  FUNNEL = 'funnel',
  SANKEY = 'sankey'
}
```

### Agent Response Structure
```typescript
export interface CFOResponse {
  summary: string;              // Exactly 4-5 lines of executive summary
  key_metrics: KeyMetric[];     // Up to 4 key financial metrics
  recommendations: string[];     // 3-4 strategic recommendations
  risk_flags: string[];         // 1-3 risk indicators
}

export interface KeyMetric {
  name: string;
  value: number | string;
  unit: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  significance: 'high' | 'medium' | 'low';
}
```

## Frontend Implementation

### API Service Layer (`/services/api.ts`)

The API service implements streaming query processing:

```typescript
export async function* processQuery(
  request: QueryRequest,
  onStageUpdate?: (stage: AgentStage) => void
): AsyncGenerator<QueryResponse, void, unknown> {
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const data = JSON.parse(chunk);
    
    // Update agent stages if callback provided
    if (data.processing_stages && onStageUpdate) {
      data.processing_stages.forEach((stage: AgentStage) => onStageUpdate(stage));
    }
    
    yield data as QueryResponse;
  }
}
```

### Component Integration

#### App.tsx
- Manages global state and routing
- Handles query submission and response streaming
- Updates UI in real-time as agents complete processing

#### ChatMessage.tsx
- Displays CFO response summary (4-5 lines)
- Shows key metrics in grid layout
- Renders Plotly visualizations
- Displays strategic recommendations
- Shows risk flags
- Presents exactly 4 follow-up questions

#### AgentPipeline.tsx
- Displays real-time processing status for all 5 agents
- Shows agent execution times
- Indicates current processing stage

## Multi-Agent Workflow

### Expected Agent Execution Order

1. **Orchestrator Agent** (400ms avg)
   - Classifies query intent
   - Routes to appropriate specialized agents
   - Determines agent collaboration strategy

2. **Visualization Agent** (800ms avg)
   - Generates appropriate Plotly charts (13 types supported)
   - Auto-selects chart type based on data dimensions
   - Formats with business-relevant labels

3. **Insights Agent** (900ms avg)
   - Produces CFO-grade 4-5 line summary
   - Identifies key metrics with trends
   - Provides actionable recommendations
   - Flags risk indicators

4. **Forecasting Agent** (1200ms avg, conditional)
   - Runs only for prediction/what-if queries
   - Uses Prophet for time-series forecasts
   - Uses XGBoost for scenario analysis
   - Provides confidence intervals

5. **Follow-Up Agent** (500ms avg)
   - Generates exactly 4 contextual follow-up questions
   - Categories: Strategic, Operational, Financial, Technical
   - Avoids duplicate questions from conversation history

### Total Expected Response Time
- **Visualization Queries**: ~2.5-3.0 seconds
- **Insights Queries**: ~2.2-2.7 seconds
- **Forecasting Queries**: ~3.8-4.3 seconds

## Environment Configuration

Create a `.env` file in the frontend root:

```env
VITE_API_URL=http://localhost:8000
```

For production:
```env
VITE_API_URL=https://api.yourcompany.com
```

## Error Handling

The frontend implements graceful error handling:

```typescript
try {
  for await (const response of queryStream) {
    // Process response
  }
} catch (error) {
  // Display user-friendly error message
  // Log error details for debugging
  // Fallback to cached responses if available
}
```

### Expected Error Responses

```typescript
{
  error_type: 'agent_timeout' | 'database_error' | 'model_error' | 'validation_error';
  message: string;
  suggested_actions: string[];
  fallback_response?: AgentResponse;
}
```

## Testing Integration

### Local Development
1. Start Python FastAPI backend on `http://localhost:8000`
2. Start frontend dev server with `npm run dev`
3. Backend should implement CORS headers for frontend origin
4. Test with sample queries from dashboard cards

### API Contract Testing
- All TypeScript types in `/types/index.ts` must match Python Pydantic models
- Test streaming responses with progress indicators
- Verify exactly 4 follow-up questions are returned
- Confirm CFO summary is 4-5 lines
- Validate all 5 agents report processing stages

## Database Requirements

Backend must connect to:
- **Host**: 34.232.69.47:5432
- **Database**: Prescience_Dev
- **Extensions**: pgvector
- **Expected Tables**:
  - `rag_embeddings` (105,984 records with 21 columns)
  - `conversation_history`
  - `prediction_cache`

## Security Considerations

### Frontend
- No sensitive data in localStorage
- Session IDs are temporary and regenerated
- All API calls use HTTPS in production
- No API keys or credentials in frontend code

### Backend (Expected)
- SSL/TLS for database connections
- JWT tokens for session authentication
- Rate limiting on query endpoints
- Input sanitization for SQL injection prevention
- CORS properly configured for frontend origin

## Deployment Checklist

- [ ] Backend FastAPI server running and healthy
- [ ] PostgreSQL with pgvector accessible
- [ ] Redis for session management running
- [ ] Prophet and XGBoost models loaded
- [ ] All 5 agents initialized in LangGraph
- [ ] RAG embeddings table populated (105,984 records)
- [ ] Environment variables configured
- [ ] CORS headers set correctly
- [ ] API endpoints responding to health checks
- [ ] Streaming responses working
- [ ] Error responses formatted correctly

## Support

For backend implementation questions, refer to:
- `/BACKEND_INTEGRATION.md` (this file)
- `/types/index.ts` (TypeScript type definitions)
- `/services/api.ts` (API service implementation)
- Design Document and Requirements Document provided

## Example Request/Response

### Request
```json
{
  "query": "What was the revenue for Q3 2024?",
  "session_id": "session_1698765432000",
  "user_id": "cfo_user_001"
}
```

### Response (Streamed)
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
      "content": "Generated quarterly revenue chart",
      "visualizations": [
        {
          "type": "line",
          "data": [...],
          "layout": {...},
          "config": {...}
        }
      ],
      "confidence": 0.94,
      "execution_time": 780,
      "follow_up_questions": []
    },
    {
      "agent_name": "Insights",
      "content": "Q3 2024 revenue reached ₹228.6 Cr...",
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
          },
          ...
        ],
        "recommendations": [
          "Scale E4 production capacity to meet Q4 demand projections of 22+ installations",
          ...
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
