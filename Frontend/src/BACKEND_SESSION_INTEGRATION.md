# Backend Session Integration - Step-by-Step Guide

## For Your Backend Developer

This guide provides everything needed to integrate the frontend session management with your FastAPI backend.

## Quick Start

### Step 1: Verify Your Backend Endpoints

Your `main.py` already has these endpoints. Verify they work:

```bash
# Start your FastAPI server
python main.py

# Test health endpoint
curl http://localhost:8000/health

# Test system status
curl http://localhost:8000/api/system/status

# Test query endpoint
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was the revenue for Q3 2024?",
    "session_id": "session_test_123",
    "user_id": "demo_user"
  }'

# Test session retrieval
curl http://localhost:8000/api/user/demo_user/sessions

# Test conversation history
curl http://localhost:8000/api/conversation/session_test_123?limit=10
```

### Step 2: Update Frontend API Calls

In `/services/api.ts`, uncomment the production code:

#### For `getUserSessions()`:

```typescript
export async function getUserSessions(userId: string): Promise<string[]> {
  try {
    // UNCOMMENT THIS:
    const response = await fetch(`${API_BASE_URL}/api/user/${userId}/sessions`);
    if (!response.ok) throw new Error('Failed to fetch user sessions');
    const data = await response.json();
    return data.sessions || [];
    
    // REMOVE THIS:
    // return [];
  } catch (error) {
    console.error('Failed to fetch user sessions:', error);
    return [];
  }
}
```

#### For `getConversationHistory()`:

```typescript
export async function getConversationHistory(sessionId: string, limit: number = 10): Promise<any> {
  try {
    // UNCOMMENT THIS:
    const response = await fetch(`${API_BASE_URL}/api/conversation/${sessionId}?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch conversation');
    return await response.json();
    
    // REMOVE THE MOCK RETURN
  } catch (error) {
    console.error('Failed to fetch conversation:', error);
    throw error;
  }
}
```

### Step 3: Update Session Loading in App.tsx

Replace `loadUserSessions()` function in `/App.tsx`:

```typescript
const loadUserSessions = async () => {
  try {
    // Get all session IDs from backend
    const sessionIds = await getUserSessions(USER_ID);
    
    if (sessionIds.length === 0) {
      setSessions([]);
      return;
    }
    
    // Load full conversation data for each session
    const sessionsData = await Promise.all(
      sessionIds.map(async (sessionId) => {
        try {
          const conversation = await getConversationHistory(sessionId, 50);
          
          // Transform backend data to frontend format
          const messages: Message[] = [];
          
          for (const turn of conversation.turns) {
            // Add user message
            messages.push({
              id: `${turn.turn_id}_user`,
              type: 'user',
              content: turn.user_query,
              timestamp: new Date(turn.timestamp)
            });
            
            // Add assistant message
            messages.push({
              id: `${turn.turn_id}_assistant`,
              type: 'assistant',
              content: turn.agent_response,
              timestamp: new Date(turn.timestamp)
            });
          }
          
          // Generate title from first user message or use current topic
          const title = conversation.current_topic || 
                       (messages[0]?.content.slice(0, 50) + 
                       (messages[0]?.content.length > 50 ? '...' : '')) ||
                       'New Conversation';
          
          return {
            id: conversation.session_id,
            userId: conversation.user_id,
            messages,
            timestamp: new Date(conversation.turns[0]?.timestamp || Date.now()),
            lastActivity: new Date(conversation.last_activity || Date.now()),
            title
          } as ChatSession;
        } catch (error) {
          console.error(`Failed to load session ${sessionId}:`, error);
          return null;
        }
      })
    );
    
    // Filter out failed sessions and sort by last activity
    const validSessions = sessionsData
      .filter((s): s is ChatSession => s !== null)
      .sort((a, b) => (b.lastActivity?.getTime() || 0) - (a.lastActivity?.getTime() || 0));
    
    setSessions(validSessions);
  } catch (error) {
    console.error('Failed to load sessions:', error);
    setSessions([]);
  }
};
```

### Step 4: Backend Requirements

Your backend needs to implement these features:

#### A. Save conversations from `/api/query` endpoint

In your `main.py`, modify the `/api/query` endpoint:

```python
@app.post("/api/query")
async def process_query(request: QueryRequest):
    try:
        # ... existing query processing ...
        
        # IMPORTANT: Save to conversation memory
        await conversation_memory.add_turn(
            session_id=request.session_id,
            user_id=request.user_id,
            user_query=request.query,
            agent_response=agent_response  # Your response object
        )
        
        # ... return response ...
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### B. Implement session storage in Redis

In your `agents/memory.py`, ensure you have:

```python
class ConversationMemory:
    async def add_turn(
        self, 
        session_id: str, 
        user_id: str,
        user_query: str, 
        agent_response: AgentResponse
    ):
        """Save conversation turn to Redis"""
        # Store session ID in user's session list
        user_sessions_key = f"user:{user_id}:sessions"
        await self.redis.sadd(user_sessions_key, session_id)
        
        # Store conversation turn
        turn_id = f"turn_{int(time.time() * 1000)}"
        turn_data = {
            "turn_id": turn_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_query": user_query,
            "agent_response": agent_response.content,
            "session_id": session_id,
            "user_id": user_id
        }
        
        # Add to session's conversation list
        conversation_key = f"session:{session_id}:turns"
        await self.redis.rpush(conversation_key, json.dumps(turn_data))
        
        # Update session metadata
        metadata_key = f"session:{session_id}:metadata"
        await self.redis.hset(metadata_key, mapping={
            "user_id": user_id,
            "last_activity": datetime.utcnow().isoformat(),
            "turn_count": await self.redis.llen(conversation_key)
        })
        
        # Set expiration (30 days)
        await self.redis.expire(conversation_key, 30 * 24 * 60 * 60)
        await self.redis.expire(metadata_key, 30 * 24 * 60 * 60)
        
    async def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user"""
        user_sessions_key = f"user:{user_id}:sessions"
        sessions = await self.redis.smembers(user_sessions_key)
        return list(sessions)
    
    async def get_session_turns(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """Get conversation turns for a session"""
        conversation_key = f"session:{session_id}:turns"
        
        # Get last N turns
        turns_json = await self.redis.lrange(
            conversation_key, 
            -limit if limit > 0 else 0, 
            -1
        )
        
        # Parse JSON
        turns = [json.loads(turn) for turn in turns_json]
        return turns
```

#### C. Update your endpoint implementations

```python
@app.get("/api/user/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    """Get all session IDs for a user"""
    try:
        sessions = await conversation_memory.get_user_sessions(user_id)
        return {"user_id": user_id, "sessions": sessions}
    except Exception as e:
        logger.error(f"Failed to get user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversation/{session_id}")
async def get_conversation(session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    try:
        # Get turns from Redis
        turns = await conversation_memory.get_session_turns(session_id, limit)
        
        # Get metadata
        metadata_key = f"session:{session_id}:metadata"
        metadata = await conversation_memory.redis.hgetall(metadata_key)
        
        # Determine current topic from last user query
        current_topic = None
        if turns:
            current_topic = turns[-1].get('user_query', '')[:50]
        
        return {
            "session_id": session_id,
            "user_id": metadata.get("user_id", "unknown"),
            "turns": turns,
            "current_topic": current_topic,
            "turn_count": len(turns),
            "last_activity": metadata.get("last_activity")
        }
    except Exception as e:
        logger.error(f"Failed to get conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

## Environment Setup

### Frontend `.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

### Backend `.env` file:

```bash
# Your existing environment variables
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Session configuration
SESSION_TIMEOUT=3600  # 1 hour
SESSION_MAX_TURNS=100
```

## Testing the Integration

### Test 1: Create Session and Send Message

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev

# Browser: Open http://localhost:5173
1. Click "Get Started"
2. Click "Continue to Chat"
3. Send message: "What was the revenue for Q3 2024?"
4. Check backend logs for session save
```

### Test 2: Verify Session Persistence

```bash
# Check Redis for saved session
redis-cli
> KEYS user:demo_user:*
> KEYS session:*
> LRANGE session:session_1234567890:turns 0 -1
> HGETALL session:session_1234567890:metadata
```

### Test 3: Session Retrieval

```bash
# Refresh browser (F5)
# Sessions should load from backend
# Click on a session in sidebar
# Messages should load
```

## Debugging

### Enable Debug Logging

Frontend (`/services/api.ts`):
```typescript
const DEBUG = true;

export async function getUserSessions(userId: string): Promise<string[]> {
  if (DEBUG) console.log('[API] Fetching sessions for user:', userId);
  
  const response = await fetch(`${API_BASE_URL}/api/user/${userId}/sessions`);
  const data = await response.json();
  
  if (DEBUG) console.log('[API] Received sessions:', data);
  
  return data.sessions || [];
}
```

Backend (`main.py`):
```python
@app.get("/api/user/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    logger.debug(f"Fetching sessions for user: {user_id}")
    sessions = await conversation_memory.get_user_sessions(user_id)
    logger.debug(f"Found {len(sessions)} sessions")
    return {"user_id": user_id, "sessions": sessions}
```

### Common Issues

#### Issue 1: CORS Error
```
Access to fetch at 'http://localhost:8000/api/user/demo_user/sessions' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution:** Already configured in your `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue 2: Sessions Not Saving
**Check:**
1. Redis is running: `redis-cli ping` → Should return `PONG`
2. Backend logs show session save
3. Redis keys exist: `redis-cli KEYS session:*`

#### Issue 3: Sessions Not Loading
**Check:**
1. `/api/user/demo_user/sessions` returns array
2. Each session ID has data in Redis
3. Frontend console shows no errors
4. Network tab shows successful requests

#### Issue 4: Empty Messages
**Check:**
1. Backend saves `user_query` and `agent_response` fields
2. Field names match frontend expectations
3. JSON parsing works correctly

## Data Migration (Optional)

If you have existing localStorage data:

```typescript
// Add to App.tsx temporarily
const migrateLocalStorageToBackend = async () => {
  const storedSessions = localStorage.getItem(`sessions_${USER_ID}`);
  if (!storedSessions) return;
  
  const sessions = JSON.parse(storedSessions);
  
  for (const session of sessions) {
    // Send each session to backend
    await fetch(`${API_BASE_URL}/api/conversation/${session.id}/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(session)
    });
  }
  
  console.log('Migration complete');
};

// Call once on mount
useEffect(() => {
  migrateLocalStorageToBackend();
}, []);
```

## Performance Optimization

### 1. Lazy Loading Sessions

Instead of loading all sessions at once:

```typescript
const loadUserSessions = async () => {
  // Only load session IDs initially
  const sessionIds = await getUserSessions(USER_ID);
  
  // Create lightweight session objects
  const sessions = sessionIds.map(id => ({
    id,
    title: 'Loading...',
    messages: [],
    timestamp: new Date(),
    isLoaded: false
  }));
  
  setSessions(sessions);
  
  // Load full data only when needed
};

const handleSessionSelect = async (sessionId: string) => {
  const session = sessions.find(s => s.id === sessionId);
  
  if (!session.isLoaded) {
    // Load messages on demand
    const conversation = await getConversationHistory(sessionId);
    // Update session with full data
  }
  
  // ... rest of logic
};
```

### 2. Caching

```typescript
const sessionCache = new Map<string, ChatSession>();

const loadSession = async (sessionId: string) => {
  // Check cache first
  if (sessionCache.has(sessionId)) {
    return sessionCache.get(sessionId);
  }
  
  // Load from backend
  const conversation = await getConversationHistory(sessionId);
  const session = transformToSession(conversation);
  
  // Cache it
  sessionCache.set(sessionId, session);
  
  return session;
};
```

## Monitoring

Add these metrics to your backend:

```python
from prometheus_client import Counter, Histogram

session_created = Counter('sessions_created_total', 'Total sessions created')
session_retrieved = Counter('sessions_retrieved_total', 'Total sessions retrieved')
session_load_time = Histogram('session_load_seconds', 'Session load time')

@app.get("/api/conversation/{session_id}")
async def get_conversation(session_id: str, limit: int = 10):
    with session_load_time.time():
        session_retrieved.inc()
        # ... existing code ...
```

## Next Steps

1. ✅ Verify all backend endpoints work
2. ⏳ Implement Redis session storage
3. ⏳ Update frontend API calls
4. ⏳ Test session creation and retrieval
5. ⏳ Test session persistence across refreshes
6. ⏳ Add error handling for network failures
7. ⏳ Implement session cleanup for old sessions
8. ⏳ Add analytics and monitoring
9. ⏳ Performance testing with 100+ sessions
10. ⏳ Production deployment

## Success Checklist

- [ ] Backend endpoints return correct data format
- [ ] Redis stores sessions correctly
- [ ] Frontend can fetch all user sessions
- [ ] Frontend can load session messages
- [ ] Sessions persist across page refreshes
- [ ] Active session is highlighted correctly
- [ ] New sessions are created and saved
- [ ] Session switching works smoothly
- [ ] No CORS errors
- [ ] No console errors
- [ ] Performance is acceptable (< 500ms load time)

You're almost there! The frontend is ready and waiting for your backend integration. 🚀
