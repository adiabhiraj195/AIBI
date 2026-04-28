# Backend Testing Guide - Real API Integration

## ✅ What Was Updated

The frontend is now fully configured to connect to your FastAPI backend at `http://localhost:8000`.

### Updated Files:

1. **`/services/api.ts`** - All API endpoints now connect to real backend:
   - `processQuery()` - Connects to `/api/query` with streaming support
   - `getUserSessions()` - Fetches from `/api/user/{userId}/sessions`
   - `getConversationHistory()` - Fetches from `/api/conversation/{sessionId}`
   - `clearConversation()` - Calls DELETE `/api/conversation/{sessionId}`
   - `checkAPIHealth()` - Checks `/health` endpoint
   - `getDatabaseStatus()` - Fetches from `/api/system/database`
   - `getSystemStatus()` - Fetches from `/api/system/status`

2. **`/App.tsx`** - Session management updated:
   - Loads sessions from backend on mount
   - Falls back to localStorage if backend unavailable
   - Transforms backend conversation data to frontend format

### Fallback Mechanism:

The frontend has intelligent fallbacks:
- If backend is unavailable → uses mock data for queries
- If sessions can't be loaded → uses localStorage
- All features work offline with demo data

---

## 🚀 Quick Start Testing

### Step 1: Start Your Backend

```bash
cd /path/to/your/backend
python main.py

# Expected output:
# INFO:     Started server process
# INFO:     Uvicorn running on http://localhost:8000
```

### Step 2: Start Frontend

```bash
# In this project directory
npm install
npm run dev

# Expected output:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

### Step 3: Open Browser

Navigate to: **http://localhost:5173**

Open browser console (F12) to see connection logs.

---

## 🧪 Testing Checklist

### Test 1: Backend Health Check

**Expected Behavior:**
- Dashboard should show green status indicators
- Console should log: `[API] Backend health status: true`

**If Failed:**
- Check if backend is running on port 8000
- Check for CORS errors in console
- Verify `/health` endpoint exists in backend

### Test 2: Send a Query

**Steps:**
1. Click "Get Started"
2. Click "Continue to Chat"
3. Type: "What was the revenue for Q3 2024?"
4. Press Enter

**Expected Console Logs:**
```
[API] Sending query to backend: {query: "What was...", session_id: "session_xxx", user_id: "demo_user"}
[API] Connected to backend successfully
[API] Received response: {...}
```

**Expected UI:**
- Agent pipeline shows all 5 agents
- Progress bars animate through stages
- Charts and insights appear in chat
- Follow-up questions appear as clickable buttons

**If Failed:**
- Check backend logs for errors
- Verify `/api/query` endpoint exists
- Check if response format matches `QueryResponse` type
- Look for CORS errors

### Test 3: Session Persistence

**Steps:**
1. Send a message (as in Test 2)
2. Refresh the page (F5)
3. Wait for page to reload

**Expected Behavior:**
- Previous session appears in sidebar
- Session title matches your first question
- Clicking the session loads the conversation

**Expected Console Logs:**
```
[App] Loading user sessions for: demo_user
[API] Fetching sessions for user: demo_user
[API] Received sessions from backend: {sessions: ["session_xxx"]}
[API] Fetching conversation history for session: session_xxx
[API] Received conversation history: {turns: [...]}
[App] Loaded sessions from backend: 1
```

**If Failed:**
- Backend not saving sessions → Check conversation memory
- Endpoint returns empty → Verify Redis storage
- CORS errors → Check backend CORS settings

### Test 4: Create New Session

**Steps:**
1. Click "+ New Chat" button in sidebar
2. Send a different message
3. Check sidebar

**Expected Behavior:**
- New session created with unique ID
- Old session still visible in sidebar
- Can switch between sessions

**If Backend Not Implemented:**
- Frontend creates sessions locally
- Sessions stored in localStorage
- Still fully functional

### Test 5: System Status Monitoring

**Steps:**
1. Go to Dashboard (click logo or "Dashboard" in sidebar)
2. Check metric cards

**Expected Behavior:**
- All status indicators green
- Database connection shown
- Agent status displayed

**Console Logs:**
```
[API] Checking backend health at: http://localhost:8000/health
[API] Backend health status: true
[API] Fetching database status
[API] Database status: {connected: true, ...}
[API] Fetching system status
[API] System status: {apiHealth: true, ...}
```

---

## 🔍 Debugging Guide

### Check Backend Endpoints

Test each endpoint independently:

```bash
# Health check
curl http://localhost:8000/health

# System status
curl http://localhost:8000/api/system/status

# Database status
curl http://localhost:8000/api/system/database

# Query endpoint
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was the revenue for Q3 2024?",
    "session_id": "test_session_123",
    "user_id": "demo_user"
  }'

# Get user sessions
curl http://localhost:8000/api/user/demo_user/sessions

# Get conversation history
curl http://localhost:8000/api/conversation/test_session_123?limit=10
```

### Common Issues

#### Issue 1: CORS Error

```
Access to fetch at 'http://localhost:8000/api/query' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Solution:** Add to your backend `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue 2: Backend Returns 404

```
[API] Backend connection failed: Error: API error: 404
```

**Solution:**
- Verify endpoint exists in backend
- Check endpoint path matches exactly
- Look at backend startup logs for registered routes

#### Issue 3: Invalid Response Format

```
[API] Failed to parse chunk: {...}
```

**Solution:**
- Backend response must match `QueryResponse` type
- Check response structure in `/types/index.ts`
- Ensure field names match exactly (snake_case in JSON)

#### Issue 4: Sessions Not Persisting

```
[API] Received sessions from backend: {sessions: []}
```

**Solution:**
- Backend not implementing session storage
- Check if Redis is running: `redis-cli ping`
- Verify `/api/query` saves to conversation memory
- Check backend logs for session save errors

#### Issue 5: Streaming Not Working

**If you see only final response:**
- Backend might not be streaming
- Check `Content-Type` header
- Frontend handles both streaming and non-streaming

**For streaming:** Backend should:
- Use `StreamingResponse` from FastAPI
- Yield JSON objects separated by newlines
- Or use Server-Sent Events (SSE)

---

## 📊 Expected Backend Response Formats

### `/api/query` Response

```json
{
  "query_intent": {
    "intent_type": "insights",
    "confidence": 0.89,
    "entities": ["revenue", "Q3 2024"],
    "temporal_scope": "Q3 2024"
  },
  "agent_responses": [
    {
      "agent_name": "Visualization",
      "content": "Generated visualizations",
      "visualizations": [
        {
          "type": "bar",
          "data": [...],
          "layout": {...}
        }
      ],
      "confidence": 0.92,
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
        "What is the breakdown by turbine model?",
        "How do margins compare to Q2?",
        "Show geographic distribution",
        "What are the top customers?"
      ],
      "cfo_response": {
        "summary": "Q3 2024 revenue reached ₹228.6 Cr...",
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
          "Scale E4 production capacity...",
          "Investigate Q1 performance patterns..."
        ],
        "risk_flags": [
          "Customer concentration: Top 5 customers represent 64% of revenue"
        ]
      }
    }
  ],
  "conversation_context": {
    "session_id": "session_1234567890",
    "user_id": "demo_user",
    "previous_queries": [],
    "previous_responses": [],
    "current_topic": "Revenue Analysis"
  },
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
    }
  ],
  "total_execution_time": 2030,
  "timestamp": "2024-11-06T10:30:45.123Z"
}
```

### `/api/user/{user_id}/sessions` Response

```json
{
  "user_id": "demo_user",
  "sessions": [
    "session_1730890245123",
    "session_1730889123456",
    "session_1730888987654"
  ]
}
```

### `/api/conversation/{session_id}` Response

```json
{
  "session_id": "session_1730890245123",
  "user_id": "demo_user",
  "turns": [
    {
      "turn_id": "turn_1730890245200",
      "timestamp": "2024-11-06T10:30:45.200Z",
      "user_query": "What was the revenue for Q3 2024?",
      "agent_response": "Q3 2024 revenue reached ₹228.6 Cr, marking a 23% increase...",
      "query_response": {...}  // Optional: full QueryResponse object
    },
    {
      "turn_id": "turn_1730890267800",
      "timestamp": "2024-11-06T10:31:07.800Z",
      "user_query": "What is the breakdown by turbine model?",
      "agent_response": "E4 turbines drive 72% of total revenue...",
      "query_response": {...}
    }
  ],
  "current_topic": "Revenue Analysis",
  "turn_count": 2,
  "last_activity": "2024-11-06T10:31:07.800Z"
}
```

### `/health` Response

```json
{
  "status": "healthy",
  "timestamp": "2024-11-06T10:30:45.123Z"
}
```

### `/api/system/status` Response

```json
{
  "apiHealth": true,
  "dbConnected": true,
  "ragSystemActive": true,
  "modelsLoaded": true,
  "activeAgents": [
    "Orchestrator",
    "Visualization",
    "Insights",
    "Forecasting",
    "Follow-Up"
  ]
}
```

### `/api/system/database` Response

```json
{
  "connected": true,
  "host": "34.232.69.47:5432",
  "database": "Prescience_Dev",
  "embedding_count": 105984,
  "latency": 45
}
```

---

## 🎯 Testing Scenarios

### Scenario 1: Complete User Journey

```
1. User visits app → Sees welcome page
2. Clicks "Get Started" → Goes to dashboard
3. Clicks on "Total Revenue" card → Opens chat with prefilled query
4. Message sent to backend → Receives streaming response
5. Sees agent pipeline progress → All 5 agents execute
6. Views charts and insights → Embedded in chat message
7. Clicks follow-up question → Sends new query
8. Refreshes page → Session persists
9. Can continue conversation → Context maintained
```

**Expected Backend Calls:**
```
GET  /health
GET  /api/system/status
GET  /api/system/database
GET  /api/user/demo_user/sessions
POST /api/query (first message)
POST /api/query (follow-up)
GET  /api/conversation/session_xxx (after refresh)
```

### Scenario 2: Multiple Sessions

```
1. Send message in Session A
2. Click "+ New Chat"
3. Send message in Session B
4. Switch to Session A from sidebar
5. Continue conversation in Session A
6. Refresh browser
7. Both sessions visible
8. Can switch between them
```

**Backend Verification:**
```bash
# Should show 2 session IDs
curl http://localhost:8000/api/user/demo_user/sessions

# Each session should have its own turns
curl http://localhost:8000/api/conversation/session_A
curl http://localhost:8000/api/conversation/session_B
```

### Scenario 3: Offline Mode

```
1. Stop backend server
2. Frontend should still work
3. Uses mock data for queries
4. Uses localStorage for sessions
5. All UI features functional
```

**Console Should Show:**
```
[API] Backend connection failed, falling back to mock data
[API] Backend unavailable for session fetch, using localStorage fallback
```

---

## 📈 Performance Benchmarks

Expected timings (with real backend):

- **Health Check:** < 100ms
- **Session List Load:** < 500ms
- **Conversation Load:** < 1000ms (per session)
- **Query Processing:** 2-5 seconds (all agents)
- **Agent Stage Updates:** Real-time streaming

If slower:
- Check network latency
- Check database query performance
- Check Redis response times
- Review backend agent execution

---

## 🔐 Environment Configuration

Create `.env` file in frontend root:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# For production
# VITE_API_URL=https://your-production-api.com
```

Backend `.env`:

```env
# CORS origins
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## ✅ Production Readiness

Before deploying to production:

- [ ] All backend endpoints tested
- [ ] Session persistence verified
- [ ] CORS configured correctly
- [ ] Error handling tested
- [ ] Performance benchmarks met
- [ ] Streaming works correctly
- [ ] Fallbacks tested
- [ ] Security review completed
- [ ] Monitoring setup
- [ ] Logging configured

---

## 🆘 Need Help?

### Frontend Issues
- Check browser console for errors
- Verify API calls in Network tab
- Review `/services/api.ts` logs

### Backend Issues
- Check backend server logs
- Test endpoints with curl
- Verify Redis is running
- Check database connection

### Integration Issues
- Compare request/response formats
- Check type definitions in `/types/index.ts`
- Review CORS configuration
- Test with Postman/curl first

---

**Your frontend is now fully connected to the backend!** 🎉

Start your backend, run the frontend, and begin testing with real queries and data.
