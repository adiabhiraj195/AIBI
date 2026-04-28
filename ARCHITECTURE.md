# Suzlon System Architecture 🏗️

Complete technical architecture for the multi-service setup.

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                       │
│                       Port: 3000                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Dashboard with financial visualizations                 │ │
│  │ • Real-time conversation interface                        │ │
│  │ • File upload and management UI                           │ │
│  │ • Built with: React 18, TypeScript, Tailwind CSS         │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────┬──────────────────────────────────┬──────────────────┘
             │ REST API Calls                   │ REST API Calls
             │ (http://localhost:8000)         │ (http://localhost:8001)
             ▼                                  ▼
┌────────────────────────────────┐  ┌────────────────────────────────┐
│   Backend 1: Main Brain RAG    │  │  Backend 2: CSV Processing     │
│        (FastAPI)               │  │       (FastAPI)                │
│      Port: 8000                │  │      Port: 8001                │
│                                │  │                                │
│ Multi-Agent Orchestration:     │  │ Features:                      │
│ ├─ Query Intent Classifier     │  │ ├─ CSV upload/preview         │
│ ├─ NL-to-SQL Agent             │  │ ├─ Groq AI analysis           │
│ ├─ Financial Analysis Agent    │  │ ├─ Supabase storage           │
│ ├─ Visualization Agent         │  │ ├─ Knowledge base management  │
│ ├─ RAG Retrieval System        │  │ └─ Metadata indexing          │
│ └─ Response Orchestrator       │  │                                │
│                                │  │ Dependencies:                  │
│ Technologies:                  │  │ ├─ Pandas (CSV processing)    │
│ ├─ LangChain (orchestration)   │  │ ├─ Groq API client            │
│ ├─ LlamaIndex (RAG)            │  │ ├─ Supabase Python SDK        │
│ ├─ pgvector (embeddings)       │  │ ├─ FastAPI                    │
│ ├─ AsyncPG (DB access)        │  │ └─ Uvicorn (ASGI server)      │
│ └─ Uvicorn (ASGI server)       │  │                                │
└────────────┬───────────────────┘  └────────────┬───────────────────┘
             │ SQL Queries                       │ SQL Queries
             │ Connection pooling                │ Connection pooling
             └──────────────────┬────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (Shared)                        │
│                    Port: 5432                                    │
│                                                                  │
│ Database: Suzlon_Backend                                         │
│                                                                  │
│ Extensions:                                                      │
│ • pgvector - For vector embeddings and similarity search        │
│ • UUID - For unique identifiers                                 │
│                                                                  │
│ Shared Tables:                                                   │
│ ├─ csv_documents (Backend A: file metadata)                     │
│ ├─ csv_content (Backend A: preprocessed CSV data)               │
│ ├─ rag_embeddings (Backend B: vector embeddings)                │
│ ├─ conversations (Backend B: chat history)                      │
│ ├─ feedback (Backend B: user feedback)                          │
│ └─ user_sessions (Both: session management)                     │
│                                                                  │
│ Features:                                                        │
│ • Connection pooling (10-20 connections)                        │
│ • Persistent storage volume: postgres_data                      │
│ • Auto-initialization with schema SQL                           │
│ • Health checks every 10 seconds                                │
└─────────────────────────────────────────────────────────────────┘
             │ Publish/Subscribe
             │ Session data
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Redis Cache (In-Memory)                       │
│                     Port: 6379                                   │
│                                                                  │
│ Usage (Backend B - Main Brain):                                 │
│ • Conversation memory storage                                   │
│ • Session management                                            │
│ • Query result caching                                          │
│ • Rate limiting counters                                        │
│                                                                  │
│ Configuration:                                                   │
│ • Persistent storage: RDB snapshots                             │
│ • AOF (Append-Only File) enabled                                │
│ • Standalone mode (no clustering)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Specifications

### Frontend: React + Vite SPA

**Location:** `Suzlon_Copilot_Frontend/`

**Technology Stack:**
- **Framework:** React 18.3.1
- **Build Tool:** Vite
- **Styling:** Tailwind CSS + Radix UI
- **HTTP Client:** Axios (via custom hooks)
- **State Management:** React Context / Hooks
- **Charting:** Recharts, Plotly.js
- **UI Components:** Radix UI (accessible)

**Build Process:**
```
src/ → Vite → dist/ → Serve
```

**Key Features:**
1. **Dashboard**
   - Real-time financial metrics
   - Interactive visualizations
   - Performance indicators

2. **Chat Interface**
   - Message history
   - Streaming responses
   - Agent stage visualization

3. **File Management**
   - CSV upload
   - File preview
   - Metadata display

**API Integration:**
- Main Brain: `VITE_API_URL` → http://localhost:8000
- CSV API: `VITE_CSV_API_URL` → http://localhost:8001

**Docker Details:**
- Multi-stage build
- Node.js 18-alpine
- Serve.js for static hosting
- Port: 3000

---

### Backend A: CSV Upload & Processing API

**Location:** `Suzlon_Backend/`

**Technology Stack:**
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn (ASGI)
- **Database:** PostgreSQL + Supabase
- **Data Processing:** Pandas 2.1.3
- **LLM Integration:** Groq API
- **Validation:** Pydantic 2.5.0

**Architecture:**
```
Routes (Controllers)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Database Connection
```

**Key Endpoints:**
```
POST   /api/files/upload          - Upload CSV file
GET    /api/files/{id}            - Get file metadata
GET    /api/files/{id}/preview    - Get file preview (first 100 rows)
POST   /api/files/{id}/analyze    - AI-powered analysis
GET    /api/knowledge-base        - Query knowledge base
PUT    /api/files/{id}            - Update file metadata
DELETE /api/files/{id}            - Delete file
```

**Database Connection:**
```python
# Via environment variables
DATABASE_URL = "postgresql://user:pass@database:5432/Suzlon_Backend"

# Or via components
db_host = "database" (in Docker)
db_port = 5432
db_name = "Suzlon_Backend"
db_user = "suzlon_user"
db_password = os.getenv("DB_PASSWORD")
```

**Features:**
1. **CSV Processing**
   - Validation and sanitization
   - Large file handling (up to 200MB)
   - Data type detection

2. **AI Analysis**
   - Groq LLM integration
   - Intelligent column analysis
   - Pattern detection

3. **Knowledge Base**
   - Indexed CSV storage
   - Full-text search capability
   - Metadata tagging

**Docker Details:**
- Multi-stage build
- Python 3.11-slim
- Port: 8001
- Health check: GET /docs

---

### Backend B: Multi-Agent RAG System

**Location:** `Suzlon_Copilot_Main_Brain/`

**Technology Stack:**
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn (ASGI)
- **Orchestration:** LangChain 0.2.16
- **RAG:** LlamaIndex 0.11.20
- **Database:** AsyncPG (PostgreSQL)
- **Cache:** Redis 5.0.1
- **ML/Embeddings:** Sentence-transformers
- **LLM:** OpenRouter/OpenAI compatible APIs

**Architecture:**
```
HTTP Request
    ↓
FastAPI Route
    ↓
Agent Orchestrator
    ├─→ Query Intent Classifier
    ├─→ Relevant Agent Selection
    ├─→ Agent Execution (with memory)
    ├─→ RAG Retrieval (if needed)
    ├─→ LLM Call (with context)
    └─→ Response Generation
    ↓
Database Storage (conversations, embeddings)
    ↓
Redis Cache (session/memory)
    ↓
HTTP Response (StreamingResponse)
```

**Key Endpoints:**
```
POST   /api/query                 - Process user query
GET    /api/conversation/{id}     - Get conversation history
POST   /api/feedback              - Submit feedback
GET    /api/memory/status         - Check memory status
GET    /api/health                - Health check
POST   /api/session               - Create session
```

**Multi-Agent System:**
```
┌─ Intent Classification Agent
│  └─ Classifies query type (financial, operational, strategic)
│
├─ NL-to-SQL Agent
│  └─ Generates SQL for database queries
│
├─ Financial Analysis Agent
│  └─ Performs calculations and trend analysis
│
├─ Visualization Agent
│  └─ Generates chart data and metadata
│
└─ RAG + Orchestrator
   └─ Retrieves relevant documents, coordinates response
```

**Database Connection:**
```python
# Shared Suzlon_Backend database
db_host = "database" (in Docker)
db_port = 5432
db_name = "Suzlon_Backend"
db_user = "suzlon_user"

# Connection pool
min_connections = 2
max_connections = 10
command_timeout = 30s
```

**Redis Connection:**
```python
redis_host = "redis" (in Docker)
redis_port = 6379
redis_db = 0
# Used for: conversation memory, session state, query cache
```

**Features:**
1. **Multi-Agent Orchestration**
   - Intent classification
   - Agent routing
   - Response aggregation

2. **RAG System**
   - Vector embeddings (pgvector)
   - Document retrieval
   - Contextual augmentation

3. **Conversation Memory**
   - Redis-backed history
   - Session management
   - Context retention across turns

4. **Streaming Responses**
   - Real-time token streaming
   - Agent stage visualization
   - Error handling with fallbacks

**Docker Details:**
- Multi-stage build
- Python 3.11-slim
- Heavy ML dependencies (torch, transformers)
- Port: 8000
- Health check: GET /docs

---

## Data Flow Examples

### Example 1: User Uploads CSV

```
User (Frontend)
    │
    └─→ POST /api/files/upload
        ├─→ Validate file
        ├─→ Parse CSV
        ├─→ Extract metadata
        ├─→ Store in PostgreSQL (csv_documents table)
        └─→ Response: { file_id, rows_count, columns }
```

### Example 2: User Asks Financial Question

```
User (Frontend)
    │
    └─→ POST /api/query { question: "What are Q3 revenue trends?" }
        ├─→ Backend Brain receives query
        ├─→ Intent Classifier → Type: "financial_analysis"
        ├─→ NL-to-SQL Agent → Generate SQL from question
        ├─→ Query PostgreSQL (from csv_documents)
        ├─→ RAG Retrieval → Get relevant embeddings
        ├─→ LLM Call → Generate response with context
        ├─→ Visualization Agent → Generate chart metadata
        ├─→ Store in conversations table
        ├─→ Cache in Redis
        └─→ StreamingResponse: tokens + visualization
```

### Example 3: Multi-Turn Conversation

```
Turn 1: User asks "What are total sales?"
    → Answer: $1.5M
    → Stored in Redis conversation memory
    → Stored in PostgreSQL conversations table

Turn 2: User asks "Compare with last year"
    → Retrieve previous context from memory
    → Add to system prompt
    → Generate comparative analysis
    → Return enhanced response
```

---

## Networking Architecture

### Docker Network: `suzlon-network`

All services on a shared bridge network:

```
┌─────────────────────────────────────────┐
│        Docker Bridge Network             │
│         (suzlon-network)                │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ frontend (3000)                  │  │
│  │ ├─ http://backend-brain:8000    │  │
│  │ └─ http://backend-csv:8001      │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ backend-brain (8000)             │  │
│  │ ├─ postgresql://database:5432    │  │
│  │ └─ redis://redis:6379            │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ backend-csv (8001)               │  │
│  │ └─ postgresql://database:5432    │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ database (5432)                  │  │
│  │ └─ PostgreSQL listening on 5432  │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ redis (6379)                     │  │
│  │ └─ Redis listening on 6379       │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**Service Discovery:**
- Services refer to each other by container name
- Docker DNS resolves names to IPs
- No need for explicit IP management

---

## Deployment Environments

### Local Development
```
Host: localhost / 127.0.0.1
DB: localhost:5432
Redis: localhost:6379
```

### Docker Compose (Current)
```
Host: container name (database, redis, etc.)
DB: database:5432
Redis: redis:6379
```

### Production (Cloud)
```
Host: RDS endpoint / managed PostgreSQL
Redis: ElastiCache / managed Redis
Networking: VPC / private subnets
```

---

## Performance Considerations

### Database Connection Pooling
```python
# Backend A (Supabase client)
# Automatic pooling via Supabase SDK

# Backend B (AsyncPG)
min_size=2      # Minimum connections
max_size=10     # Maximum connections
command_timeout=30  # Seconds
```

### Redis Memory Management
```
maxmemory: unlimited
maxmemory-policy: allkeys-lru
persistence: AOF + RDB snapshots
```

### Frontend Optimization
```
• Vite code splitting
• Lazy loading of routes
• Component-level code splitting
• Image optimization
```

---

## Scaling Considerations

### Horizontal Scaling
```
• Frontend: Stateless, multiple instances behind load balancer
• Backend A: Stateless, database connection pooling
• Backend B: Needs session affinity for conversations
• Database: Connection pooling + read replicas
• Redis: Clustering or replication
```

### Vertical Scaling
```
• Increase container resources
• Increase connection pool sizes
• Increase Redis memory
• Increase PostgreSQL shared_buffers
```

---

## Monitoring & Observability

### Health Checks
```
Frontend:   GET http://localhost:3000
Backend A:  GET http://localhost:8001/docs
Backend B:  GET http://localhost:8000/docs
Database:   pg_isready -U user
Redis:      PING
```

### Logging
```
Frontend:   Browser console + server logs
Backend A:  stdout/stderr (structured logs)
Backend B:  stdout/stderr + Redis session logs
Database:   PostgreSQL log file
```

### Metrics to Monitor
```
• API response times
• Database query performance
• Memory usage (all services)
• Redis memory consumption
• Conversation processing time
• Error rates
```

---

## Security Architecture

### Data Protection
```
• Environment variables for secrets
• Database credentials via .env
• API keys not in code
• TLS/HTTPS in production
```

### Network Security
```
• Docker network isolation
• Service-to-service authentication (future)
• CORS configuration
• Rate limiting
```

### Database Security
```
• User roles and permissions
• Connection pooling isolation
• Query parameterization
• Audit logging
```

---

**Last Updated:** January 2026
