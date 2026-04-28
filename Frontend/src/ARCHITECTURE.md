# Session Management Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│                                                              │
│  ┌────────────┐      ┌─────────────┐      ┌──────────────┐ │
│  │ App.tsx    │◄────►│ api.ts      │◄────►│ FastAPI      │ │
│  │            │      │ (Service)   │      │ Backend      │ │
│  │ - State    │      │ - API calls │      │              │ │
│  │ - Sessions │      │ - Streaming │      │ - LangGraph  │ │
│  │ - Messages │      │             │      │ - Redis      │ │
│  └────────────┘      └─────────────┘      │ - PostgreSQL │ │
│        │                                   └──────────────┘ │
│        ▼                                                     │
│  ┌────────────┐                                             │
│  │ localStorage│ (Demo Mode)                                │
│  └────────────┘                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
App.tsx
├── WelcomePage (currentPage === 'welcome')
├── DashboardPage (currentPage === 'dashboard')
└── Chat Interface (currentPage === 'chat')
    ├── Sidebar
    │   ├── Header
    │   ├── New Chat Button → handleNewChat()
    │   ├── Navigation (Welcome, Dashboard)
    │   └── QueryHistory
    │       └── Session Cards → handleSessionSelect()
    │           ├── Today Sessions
    │           └── Previous Sessions
    ├── Main Chat Area
    │   ├── Header
    │   ├── Messages (ScrollArea)
    │   │   ├── ChatMessage (user)
    │   │   ├── ChatMessage (assistant)
    │   │   └── ...
    │   └── ChatInput → handleQuerySubmit()
    └── ...
```

## Data Flow

### 1. New Chat Creation Flow

```
User clicks "New Chat"
        ↓
handleNewChat() called
        ↓
Save current session (if messages exist)
        ↓
Generate new session_id: 'session_' + Date.now()
        ↓
setSessionId(newSessionId)
setMessages([])
        ↓
Navigate to chat page
        ↓
Empty chat interface shown
```

### 2. Message Sending Flow

```
User types query → ChatInput
        ↓
handleQuerySubmit(query)
        ↓
Create user message
        ↓
Add to messages state
        ↓
Create assistant message (processing state)
        ↓
Call processQuery() API
        ↓
Stream response chunks
        ↓
Update message with real-time agent stages
        ↓
Final response received
        ↓
useEffect triggers saveCurrentSession()
        ↓
Session saved to localStorage
        ↓
Sessions state updated
        ↓
Sidebar shows updated session
```

### 3. Session Switching Flow

```
User clicks session in sidebar
        ↓
handleSessionSelect(sessionId) called
        ↓
Check if same session → return
        ↓
Save current session (if messages exist)
        ↓
Find selected session in sessions array
        ↓
setSessionId(selectedSession.id)
setMessages(selectedSession.messages)
        ↓
Navigate to chat page
        ↓
Messages load and render
        ↓
Scroll to bottom
```

### 4. Session Persistence Flow

```
App mounts
        ↓
useEffect() runs
        ↓
loadUserSessions() called
        ↓
Read from localStorage['sessions_demo_user']
        ↓
Parse JSON
        ↓
Convert timestamp strings → Date objects
        ↓
setSessions(parsed sessions)
        ↓
Sidebar renders session list
```

### 5. Auto-Save Flow

```
User sends message
        ↓
messages state changes
        ↓
useEffect([messages, sessionId]) triggers
        ↓
if (messages.length > 0)
        ↓
saveCurrentSession() called
        ↓
Generate title from first user message
        ↓
Create session object
        ↓
Update sessions array (filter + prepend)
        ↓
Save to localStorage
        ↓
Sidebar re-renders with updated session
```

## State Management

### App.tsx State

```typescript
// Core page navigation
currentPage: AppPage = 'welcome' | 'dashboard' | 'chat'

// Current active session
sessionId: string = 'session_1234567890'

// Messages in current session
messages: Message[] = [
  { id, type: 'user', content, timestamp },
  { id, type: 'assistant', content, timestamp, queryResponse }
]

// All user sessions
sessions: ChatSession[] = [
  {
    id: 'session_1234567890',
    title: 'Q3 Revenue Analysis',
    messages: [...],
    timestamp: Date,
    lastActivity: Date,
    userId: 'demo_user'
  }
]

// UI state
isProcessing: boolean
sidebarOpen: boolean

// System status
systemStatus: SystemStatus
```

## localStorage Schema

### Key: `sessions_demo_user`

```json
[
  {
    "id": "session_1730897654321",
    "title": "What was the revenue for Q3 2024?",
    "userId": "demo_user",
    "timestamp": "2024-11-06T10:30:00.000Z",
    "lastActivity": "2024-11-06T10:35:00.000Z",
    "messages": [
      {
        "id": "1730897654321",
        "type": "user",
        "content": "What was the revenue for Q3 2024?",
        "timestamp": "2024-11-06T10:30:00.000Z"
      },
      {
        "id": "1730897654322",
        "type": "assistant",
        "content": "Q3 2024 revenue reached ₹228.6 Cr...",
        "timestamp": "2024-11-06T10:30:05.000Z",
        "queryResponse": {
          "query_intent": {...},
          "agent_responses": [...],
          "conversation_context": {...},
          "processing_stages": [...],
          "total_execution_time": 2500,
          "timestamp": "2024-11-06T10:30:05.000Z"
        }
      }
    ]
  }
]
```

## Backend API Integration (Production)

### Endpoint Mapping

| Frontend Function | Backend Endpoint | Method | Purpose |
|------------------|------------------|--------|---------|
| `getUserSessions(userId)` | `/api/user/{user_id}/sessions` | GET | Get all session IDs |
| `getConversationHistory(sessionId)` | `/api/conversation/{session_id}` | GET | Get messages |
| `processQuery(request)` | `/api/query` | POST | Send query |
| `clearConversation(sessionId)` | `/api/conversation/{session_id}` | DELETE | Clear session |
| `getSessionSummary(sessionId)` | `/api/conversation/{session_id}/summary` | GET | Get summary |

### Request/Response Flow

```
Frontend                    Backend                     Database
   │                           │                            │
   │  POST /api/query          │                            │
   ├──────────────────────────►│                            │
   │                           │  Save to conversation      │
   │                           ├───────────────────────────►│
   │                           │  memory (Redis)            │
   │                           │                            │
   │  ◄─────────────────────── │  Stream response           │
   │  (SSE/JSON chunks)        │                            │
   │                           │  Update session metadata   │
   │                           ├───────────────────────────►│
   │                           │                            │
   │  GET /api/user/          │                            │
   │      demo_user/sessions   │                            │
   ├──────────────────────────►│                            │
   │                           │  Query Redis/PostgreSQL    │
   │                           ├───────────────────────────►│
   │  ◄─────────────────────── │  Return session IDs        │
   │  ["session_1", ...]       │                            │
   │                           │                            │
```

## Session Lifecycle

### Session States

```
┌─────────────┐
│   CREATED   │ (New session, no messages)
└──────┬──────┘
       │ First message sent
       ▼
┌─────────────┐
│   ACTIVE    │ (Has messages, user interacting)
└──────┬──────┘
       │ User switches session / closes app
       ▼
┌─────────────┐
│   STORED    │ (Saved to localStorage/backend)
└──────┬──────┘
       │ User reopens session
       ▼
┌─────────────┐
│   ACTIVE    │ (Loaded from storage)
└─────────────┘
```

### Session Expiration (Future)

```
Session created
        ↓
Last activity timestamp recorded
        ↓
After 30 days of inactivity
        ↓
Backend cleanup job marks as inactive
        ↓
Frontend shows archived sessions separately
        ↓
After 90 days of inactivity
        ↓
Session deleted from database
```

## Scaling Considerations

### Current Limitations (localStorage)
- Max ~5-10 MB storage per domain
- ~50-100 sessions with full message history
- Client-side only (no cross-device sync)

### Production (Backend)
- Redis: Real-time session state
  - Fast reads/writes
  - TTL-based expiration
  - Session locking for concurrency
  
- PostgreSQL: Persistent storage
  - Full conversation history
  - Searchable message content
  - Analytics and reporting
  - User session metadata

### Optimization Strategies

1. **Lazy Loading**
   ```
   Load session IDs only → User clicks → Load full messages
   ```

2. **Pagination**
   ```
   Load recent 50 messages → User scrolls up → Load more
   ```

3. **Compression**
   ```
   Compress message content before storing
   ```

4. **Caching**
   ```
   Cache frequently accessed sessions in memory
   ```

## Error Handling

### Frontend Errors

```typescript
try {
  const sessions = await getUserSessions(USER_ID);
  setSessions(sessions);
} catch (error) {
  console.error('Failed to load sessions:', error);
  // Fallback to localStorage
  // Show error toast to user
  // Continue with empty session list
}
```

### Network Failures

```
Backend unavailable
        ↓
API call fails
        ↓
Catch error in api.ts
        ↓
Check if localStorage has data
        ↓
Use cached data + show "Offline" indicator
        ↓
Queue writes for when back online
```

## Security Considerations

### Current (Demo Mode)
- ⚠️ No authentication
- ⚠️ Sessions stored in plain localStorage
- ⚠️ Anyone can access any session

### Production Requirements
- ✅ User authentication (JWT tokens)
- ✅ Session ownership verification
- ✅ HTTPS only
- ✅ CSRF protection
- ✅ Rate limiting
- ✅ Input validation
- ✅ XSS prevention

### Implementation Plan

1. Add authentication provider
   ```typescript
   const { user, token } = useAuth();
   ```

2. Include token in API calls
   ```typescript
   headers: {
     'Authorization': `Bearer ${token}`,
     'Content-Type': 'application/json'
   }
   ```

3. Backend validates token
   ```python
   @require_auth
   async def get_user_sessions(user_id: str):
       if current_user.id != user_id:
           raise HTTPException(403, "Forbidden")
       # ... rest of logic
   ```

## Performance Metrics

### Target Performance

| Metric | Target | Current |
|--------|--------|---------|
| Session load time | < 500ms | ~100ms (localStorage) |
| Session switch time | < 100ms | ~50ms (in-memory) |
| Message send time | < 2s | ~2.5s (multi-agent) |
| Sidebar render time | < 50ms | ~30ms (50 sessions) |
| localStorage save time | < 50ms | ~10ms |

### Monitoring Points

```typescript
// Add timing logs
console.time('loadSessions');
await loadUserSessions();
console.timeEnd('loadSessions');

console.time('switchSession');
await handleSessionSelect(sessionId);
console.timeEnd('switchSession');
```

## Testing Strategy

### Unit Tests
- Session creation logic
- Title generation
- Date parsing/formatting
- Session sorting

### Integration Tests
- API calls
- localStorage reads/writes
- State updates

### E2E Tests
- Full user flow
- Multi-session scenarios
- Persistence across refreshes

See `TESTING_GUIDE.md` for detailed test cases.
