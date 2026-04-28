# CFO Multi-Agent Chatbot - Project Overview

## Executive Summary

This is a **conversational AI chatbot interface** for Suzlon Wind Energy's CFO operations. It provides natural language querying of financial and operational data through a **multi-agent AI system** powered by LangGraph, RAG (pgvector embeddings), and ML models (Prophet + XGBoost).

**Current Status:** ✅ Frontend 100% Integration-Ready | ⏳ Backend Development Needed

### Three-Page Application Structure
1. **Welcome Page**: Claude-style onboarding with feature highlights
2. **CFO Dashboard**: 7 critical metric cards with click-to-query functionality  
3. **Chat Interface**: Conversational AI assistant with real-time 5-agent pipeline

---

## What This Application Does

### User Experience
1. **Natural Language Queries**: CFOs ask questions in plain English like "What was Q3 revenue for E4 turbines?"
2. **Multi-Agent Processing**: A 5-agent pipeline processes queries:
   - **Orchestrator** → Routes queries to specialized agents
   - **Visualization** → Generates 13 types of Plotly charts
   - **Insights** → Produces CFO-grade 4-5 line summaries
   - **Forecasting** → Prophet/XGBoost predictions (conditional)
   - **Follow-Up** → Generates exactly 4 contextual questions
3. **Rich Visualizations**: Auto-selected charts optimized for data dimensions
4. **CFO-Grade Responses**: 4-5 line executive summaries with key metrics, recommendations, and risk flags
5. **Smart Follow-ups**: Exactly 4 categorized questions (Strategic, Operational, Financial, Technical)

### Page 1: Welcome Screen
- **Claude-Inspired Design**: Professional welcome experience with feature showcase
- **Dark + Green Theme**: Modern aesthetic with emerald accents (#10b981)
- **Key Features Display**: 6 capability cards highlighting AI features
- **Call-to-Action**: Direct navigation to dashboard or chat
- **Font**: General Sans for modern, professional typography

### Page 2: CFO Dashboard
- **7 Priority Metric Cards** organized by urgency:
  - **Priority 1 (Critical)**: Revenue Realization, Cash Flow, Project Margin Health
  - **Priority 2 (Operational)**: Stage-Wise Financial Exposure, Customer Concentration Risk
  - **Priority 3 (Strategic)**: Quarterly Forecast Confidence, Cost Efficiency Metrics
- **Interactive Cards**: Hover to preview, click to auto-submit query in chat
- **Real Financial Metrics**: ₹485 Cr revenue at risk, ₹1,250 Cr cash position, etc.
- **Visual Indicators**: Progress bars, status badges, trend indicators

### Page 3: Chat Interface
- **Dark Theme**: Matches dashboard with emerald green accents
- **Conversational UI**: Messages appear like modern chat (ChatGPT/Claude style)
- **Real-time Pipeline Visibility**: See 5 agents working (Orchestrator → Visualization → Insights → Forecasting → Follow-Up)
- **CFO Response Format**: 
  - 4-5 line executive summary
  - Grid of 4 key metrics with trend indicators
  - Strategic recommendations
  - Risk flags
  - Exactly 4 follow-up questions
- **Session History**: Sidebar shows previous conversations
- **System Metrics**: Live monitoring showing:
  - 5 active agents status
  - Database connection (105,984 RAG embeddings)
  - Model status (Prophet + XGBoost)
  - LangGraph orchestration status
- **Navigation**: Easy access to Welcome and Dashboard pages

---

## User Navigation Flow

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   WELCOME   │ ──────> │  DASHBOARD   │ ──────> │     CHAT     │
│    PAGE     │  Start  │  (7 Cards)   │  Query  │  INTERFACE   │
└─────────────┘         └──────────────┘         └──────────────┘
      ▲                        ▲                        │
      │                        │                        │
      └────────────────────────┴────────────────────────┘
                    Navigation Buttons (Sidebar)
```

**Flow:**
1. User lands on **Welcome Page** → sees AI capabilities and features
2. Clicks "Get Started" → navigates to **CFO Dashboard**
3. Views critical financial metrics → hovers/clicks card → navigates to **Chat**
4. Query auto-submitted → 5-agent pipeline processes → results displayed
5. User can navigate back to Welcome/Dashboard anytime via sidebar

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 FRONTEND (React/TypeScript)                  │
│               ✅ 100% Integration-Ready                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  WelcomePage │  │ DashboardPage│  │  Chat Page   │     │
│  │              │  │  (7 Cards)   │  │  (Messages)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Components                                          │   │
│  │  • ChatMessage → Displays CFO responses + metrics    │   │
│  │  • AgentPipeline → Shows 5-agent processing stages  │   │
│  │  • SystemMetrics → Backend health monitoring        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API Service Layer (/services/api.ts)               │   │
│  │  • Streaming query processing (SSE)                 │   │
│  │  • Real-time agent stage updates                    │   │
│  │  • System health checks                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Type System (/types/index.ts)                      │   │
│  │  • Matches backend Pydantic models                  │   │
│  │  • AgentType, QueryIntentType, ChartType enums      │   │
│  │  • CFOResponse, QueryResponse interfaces            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/SSE (POST /api/query)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (Python/FastAPI + LangGraph)            │
│                  ⏳ NEEDS TO BE BUILT                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         LangGraph Multi-Agent Pipeline                │  │
│  │                                                        │  │
│  │  1. Orchestrator Agent → Query classification & routing│
│  │     • Intent detection (visualization/insights/forecast)│
│  │     • Agent coordination                              │  │
│  │     • Execution: ~400ms                               │  │
│  │                                                        │  │
│  │  2. Visualization Agent → Chart generation            │  │
│  │     • 13 chart types (bar, line, heatmap, choropleth,│  │
│  │       scatter, bubble, pie, waterfall, treemap, etc.) │  │
│  │     • Plotly format output                            │  │
│  │     • Execution: ~800ms                               │  │
│  │                                                        │  │
│  │  3. Insights Agent → CFO-grade analysis               │  │
│  │     • 4-5 line executive summary                      │  │
│  │     • 4 key metrics with trends                       │  │
│  │     • Strategic recommendations                        │  │
│  │     • Risk flags                                       │  │
│  │     • Execution: ~900ms                               │  │
│  │                                                        │  │
│  │  4. Forecasting Agent → Predictive analytics          │  │
│  │     • Prophet: Time-series forecasting                │  │
│  │     • XGBoost: Scenario analysis                      │  │
│  │     • Confidence intervals                            │  │
│  │     • Execution: ~1200ms (conditional)                │  │
│  │                                                        │  │
│  │  5. Follow-Up Agent → Question generation             │  │
│  │     • Exactly 4 contextual questions                  │  │
│  │     • Categories: Strategic/Operational/Financial/Tech│  │
│  │     • Avoids duplicates from history                  │  │
│  │     • Execution: ~500ms                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              RAG System (pgvector)                    │  │
│  │  • PostgreSQL with pgvector extension                │  │
│  │  • 105,984 embeddings (21 columns)                   │  │
│  │  • Semantic search + metadata filtering              │  │
│  │  • Vector similarity for context retrieval           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         ML Models (Prophet + XGBoost)                 │  │
│  │  • Prophet: Time-series capacity forecasting         │  │
│  │  • XGBoost: What-if scenario modeling                │  │
│  │  • Pre-trained on Suzlon historical data             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Conversation Memory (Redis + PostgreSQL)         │  │
│  │  • Redis: Session-based fast access                  │  │
│  │  • PostgreSQL: Persistent conversation logs          │  │
│  │  • Context window: 10 previous interactions          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
            ┌────────────────────────────────┐
            │  PostgreSQL Database           │
            │  Host: 34.232.69.47:5432      │
            │  DB: Prescience_Dev            │
            │  • rag_embeddings (105,984)   │
            │  • conversation_history        │
            │  • prediction_cache            │
            └────────────────────────────────┘
```

---

## Backend Integration Requirements

### API Endpoints (Expected from Backend)

#### 1. Query Processing (Primary)
**POST /api/query**
- Accepts: `{ query: string, session_id: string, user_id?: string }`
- Returns: Server-Sent Events stream with QueryResponse
- Processing stages streamed in real-time
- Total response time: < 5 seconds (95%ile)

#### 2. System Health
**GET /health**
- Returns: System health status

#### 3. Database Status
**GET /api/system/database**
- Returns: Connection status, embedding count (105,984), latency

#### 4. System Status
**GET /api/system/status**
- Returns: Agent health, RAG status, models loaded

#### 5. Conversation Management
**GET /api/conversation/:sessionId** - Retrieve history
**DELETE /api/conversation/:sessionId** - Clear session

### Data Contract

All TypeScript types defined in `/types/index.ts` match Python Pydantic models:

```typescript
// 5 Agent Types
enum AgentType {
  ORCHESTRATOR, VISUALIZATION, INSIGHTS, FORECASTING, FOLLOWUP
}

// Query Intent Classification
enum QueryIntentType {
  VISUALIZATION, INSIGHTS, FORECASTING, GENERAL
}

// 13 Supported Chart Types
enum ChartType {
  BAR, STACKED_BAR, LINE, HEATMAP, CHOROPLETH, SCATTER,
  BUBBLE, PIE, DONUT, WATERFALL, TREEMAP, BOX, FUNNEL, SANKEY
}

// CFO Response Structure (4-5 lines)
interface CFOResponse {
  summary: string;              // Executive summary
  key_metrics: KeyMetric[];     // 4 key metrics
  recommendations: string[];     // Strategic actions
  risk_flags: string[];         // Risk indicators
}
```

See `/BACKEND_INTEGRATION.md` for complete API specifications.

---

## Key Features

### 1. Multi-Agent Architecture
- **Orchestrator**: Routes queries to appropriate specialized agents
- **Visualization**: Auto-generates charts based on data dimensions
- **Insights**: Produces CFO-grade summaries with business context
- **Forecasting**: Prophet/XGBoost predictions for time-series and scenarios
- **Follow-Up**: Context-aware question generation (exactly 4)

### 2. CFO-Grade Responses
Every response includes:
- **4-5 line summary**: Executive-level insights
- **4 key metrics**: With trends (increasing/decreasing/stable) and significance
- **Recommendations**: Actionable strategic advice
- **Risk flags**: Critical business indicators
- **4 follow-up questions**: Categorized by type

### 3. Real-Time Processing
- **Streaming responses**: See agents work in real-time
- **Stage updates**: Visual pipeline shows current processing step
- **Execution times**: Each agent reports duration
- **Quality indicators**: Confidence scores for each agent

### 4. Smart Visualizations
- **13 chart types**: Auto-selected based on query and data
- **Plotly integration**: Interactive, professional charts
- **Business formatting**: Labeled with ₹ Cr, MW, project counts
- **Dark theme**: Consistent with application design

### 5. Conversation Memory
- **Session persistence**: Redis for fast access
- **Context awareness**: References previous 10 interactions
- **Topic tracking**: Maintains conversation flow
- **History retrieval**: Sidebar shows past sessions

---

## Technology Stack

### Frontend (Implemented)
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS v4.0
- **UI Components**: shadcn/ui (custom dark theme)
- **Charts**: Recharts (for mock data) → Plotly (backend provides)
- **Icons**: Lucide React
- **Font**: General Sans

### Backend (To Be Built)
- **Framework**: Python FastAPI
- **Orchestration**: LangGraph
- **RAG**: LlamaIndex + pgvector
- **ML Models**: Prophet, XGBoost
- **Database**: PostgreSQL 14+ with pgvector
- **Cache**: Redis
- **LLM Providers**: OpenRouter → Cerebras → Groq (fallback chain)

---

## File Structure

```
/
├── App.tsx                          # Main app with routing (Welcome/Dashboard/Chat)
├── BACKEND_INTEGRATION.md           # Complete API integration guide
├── PROJECT_OVERVIEW.md              # This file
├── types/
│   └── index.ts                     # TypeScript types matching backend
├── components/
│   ├── WelcomePage.tsx              # Claude-style landing page
│   ├── DashboardPage.tsx            # 7 CFO metric cards
│   ├── ChatMessage.tsx              # CFO response rendering
│   ├── ChatInput.tsx                # Query input with suggestions
│   ├── AgentPipeline.tsx            # 5-agent processing display
│   ├── SystemMetrics.tsx            # Backend health monitoring
│   └── QueryHistory.tsx             # Session history sidebar
├── services/
│   ├── api.ts                       # API integration layer
│   └── database.ts                  # Database schema types
└── styles/
    └── globals.css                  # Dark theme + General Sans
```

---

## Dashboard Metric Cards (7 Priority Areas)

### Priority 1: Critical Metrics

1. **Revenue Realization**
   - **Value**: ₹485 Cr at risk
   - **Query**: "Show me revenue realization breakdown by project phase and identify stuck payments"

2. **Cash Flow Position**
   - **Value**: ₹1,250 Cr current position
   - **Query**: "Analyze current cash flow position and forecast next 90-day runway"

3. **Project Margin Health**
   - **Value**: 3.2% margin compression
   - **Query**: "Show me project-level margin analysis and highlight erosion factors"

### Priority 2: Operational Metrics

4. **Stage-Wise Financial Exposure**
   - **Value**: ₹2,340 Cr total exposure
   - **Query**: "Break down financial exposure across all project stages and risk levels"

5. **Customer Concentration Risk**
   - **Value**: 68% from top 5 customers
   - **Query**: "Analyze customer concentration risk and revenue dependency patterns"

### Priority 3: Strategic Metrics

6. **Quarterly Forecast Confidence**
   - **Value**: 82% confidence for Q4 2024
   - **Query**: "Show me Q4 2024 forecast confidence intervals and variance analysis"

7. **Cost Efficiency Metrics**
   - **Value**: 15% reduction opportunity
   - **Query**: "Analyze cost efficiency trends and identify optimization opportunities"

---

## Development Workflow

### Frontend Development (Complete)
1. ✅ Welcome page with feature showcase
2. ✅ Dashboard with 7 interactive metric cards
3. ✅ Chat interface with dark theme
4. ✅ Real-time agent pipeline display
5. ✅ CFO response formatting (4-5 lines + metrics)
6. ✅ Follow-up question rendering (exactly 4)
7. ✅ System health monitoring
8. ✅ Session management
9. ✅ Type system matching backend

### Backend Development (Needed)
1. ⏳ FastAPI server setup
2. ⏳ LangGraph multi-agent pipeline
3. ⏳ 5 specialized agents (Orchestrator, Visualization, Insights, Forecasting, Follow-Up)
4. ⏳ RAG system with pgvector (105,984 embeddings)
5. ⏳ Prophet + XGBoost model integration
6. ⏳ Redis conversation memory
7. ⏳ PostgreSQL database connection
8. ⏳ SSE streaming endpoint
9. ⏳ Error handling & fallbacks

### Integration Steps
1. Backend implements `/api/query` endpoint matching TypeScript types
2. Backend streams processing stages via Server-Sent Events
3. Frontend connects to backend URL (env: `VITE_API_URL`)
4. Test with dashboard card queries
5. Verify 5-agent pipeline execution
6. Confirm CFO response format (4-5 lines)
7. Validate exactly 4 follow-up questions
8. Monitor system health metrics

---

## Expected Response Times

| Query Type | Agents Involved | Expected Time |
|-----------|----------------|---------------|
| Visualization | Orchestrator → Visualization → Insights → Follow-Up | 2.5-3.0s |
| Insights | Orchestrator → Insights → Follow-Up | 2.2-2.7s |
| Forecasting | All 5 agents | 3.8-4.3s |

Target: **95% of queries under 5 seconds**

---

## Business Value

### For CFOs
- **Instant insights**: Natural language queries eliminate manual analysis
- **Executive summaries**: 4-5 line responses perfect for decision-making
- **Risk awareness**: Flagged indicators in every response
- **Guided exploration**: 4 follow-up questions drive deeper analysis

### For Analysts
- **Automated visualization**: 13 chart types auto-selected
- **Context preservation**: Conversation memory maintains analysis flow
- **Predictive analytics**: Prophet/XGBoost forecasts
- **Quality assurance**: Agent pipeline visible for debugging

### For Organization
- **Data democratization**: Anyone can query complex financial data
- **Faster decisions**: Real-time insights vs. days of analysis
- **Consistent insights**: AI ensures comprehensive responses
- **Audit trail**: All queries logged in conversation history

---

## Next Steps

### For Backend Developer (Kiro)
1. Review `/BACKEND_INTEGRATION.md` for complete API specifications
2. Review `/types/index.ts` for TypeScript → Pydantic model mapping
3. Implement FastAPI server with LangGraph orchestration
4. Create 5 specialized agents matching AgentType enum
5. Integrate RAG system with 105,984 pgvector embeddings
6. Load Prophet + XGBoost models for forecasting
7. Implement SSE streaming for real-time updates
8. Test with frontend dashboard queries
9. Deploy and connect via VITE_API_URL environment variable

### Testing Checklist
- [ ] `/health` endpoint responds
- [ ] `/api/system/database` shows 105,984 embeddings
- [ ] `/api/system/status` lists all 5 agents as active
- [ ] `/api/query` streams processing stages
- [ ] Orchestrator routes queries correctly
- [ ] Visualization generates Plotly charts
- [ ] Insights produces 4-5 line summaries
- [ ] Forecasting conditionally triggers
- [ ] Follow-Up returns exactly 4 questions
- [ ] Response time < 5 seconds (95%ile)
- [ ] Conversation memory persists across queries

---

## Support Documentation

- **`/BACKEND_INTEGRATION.md`**: Complete API integration guide with request/response examples
- **`/types/index.ts`**: TypeScript type definitions matching backend Pydantic models
- **`/services/api.ts`**: Frontend API service implementation with streaming support
- **Design Document**: Multi-agent architecture specification
- **Requirements Document**: Detailed functional requirements

---

## Contact & Collaboration

Frontend is 100% ready for integration. Backend development should follow the specifications in `/BACKEND_INTEGRATION.md` to ensure seamless connection.

**Integration Point**: `/services/api.ts` → Set `VITE_API_URL` to backend URL

**Type Contract**: `/types/index.ts` → Must match Python Pydantic models exactly

**Test Queries**: Available from dashboard cards → Pre-configured CFO questions
