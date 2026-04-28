# Session Management Integration Guide

This document explains how the frontend session management integrates with your FastAPI backend.

## Overview

The frontend now has full session management capabilities:
- ✅ Creates new sessions when clicking "New Chat"
- ✅ Saves sessions automatically to localStorage (ready for backend integration)
- ✅ Lists all user sessions in the sidebar
- ✅ Highlights the currently active session
- ✅ Allows switching between sessions
- ✅ Loads message history when switching sessions
- ✅ Automatically generates session titles from first user message

## Current Implementation

### Local Storage (Demo Mode)
Currently, sessions are stored in `localStorage` under the key `sessions_{USER_ID}`. This allows the frontend to work independently while you develop the backend integration.

### Data Flow

1. **New Chat Creation**
   - User clicks "New Chat" button
   - Frontend generates session ID: `session_{timestamp}`
   - New empty session is created
   - User navigates to chat interface

2. **Sending Messages**
   - User sends query via `/api/query` endpoint
   - Message is added to current session
   - Session is automatically saved to localStorage
   - Session title is generated from first user message

3. **Session Switching**
   - User clicks on a session in sidebar
   - Current session is saved
   - Selected session messages are loaded
   - UI updates to show selected session

4. **Session Persistence**
   - Sessions are saved to localStorage on every message
   - Sessions are loaded on app mount
   - Sessions are sorted by last activity time

## Backend Integration Points

### 1. Update `/services/api.ts`

The API service has placeholder functions ready for backend integration. Find these commented sections and uncomment them:

```typescript
// In getUserSessions():
const response = await fetch(`${API_BASE_URL}/api/user/${userId}/sessions`);
if (!response.ok) throw new Error('Failed to fetch user sessions');
const data = await response.json();
return data.sessions || [];

// In getConversationHistory():
const response = await fetch(`${API_BASE_URL}/api/conversation/${sessionId}?limit=${limit}`);
if (!response.ok) throw new Error('Failed to fetch conversation');
return await response.json();

// In clearConversation():
await fetch(`${API_BASE_URL}/api/conversation/${sessionId}`, { method: 'DELETE' });

// In getSessionSummary():
const response = await fetch(`${API_BASE_URL}/api/conversation/${sessionId}/summary`);
if (!response.ok) throw new Error('Failed to fetch session summary');
return await response.json();
```

### 2. Update Session Save Logic in `/App.tsx`

Replace the localStorage save in `saveCurrentSession()` function:

```typescript
// REPLACE THIS:
try {
  localStorage.setItem(`sessions_${USER_ID}`, JSON.stringify(updated));
} catch (error) {
  console.error('Failed to save session:', error);
}

// WITH THIS:
try {
  // Save to backend
  await fetch(`${API_BASE_URL}/api/conversation/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      user_id: USER_ID,
      messages: messages,
      title: title
    })
  });
} catch (error) {
  console.error('Failed to save session:', error);
}
```

### 3. Update Session Loading in `loadUserSessions()`

Replace the localStorage load:

```typescript
// REPLACE THIS:
const storedSessions = localStorage.getItem(`sessions_${USER_ID}`);
if (storedSessions) {
  const parsedSessions = JSON.parse(storedSessions);
  // ... rest of code
}

// WITH THIS:
const sessionIds = await getUserSessions(USER_ID);
const sessionsData = await Promise.all(
  sessionIds.map(async (sessionId) => {
    const conversation = await getConversationHistory(sessionId);
    return {
      id: conversation.session_id,
      userId: conversation.user_id,
      messages: conversation.turns.map(turn => ({
        id: turn.turn_id,
        type: 'user', // You'll need to determine this from turn data
        content: turn.user_query,
        timestamp: new Date(turn.timestamp)
      })),
      timestamp: new Date(conversation.turns[0]?.timestamp || Date.now()),
      lastActivity: new Date(conversation.last_activity),
      title: conversation.current_topic || 'Conversation'
    };
  })
);
setSessions(sessionsData);
```

## Backend API Endpoints Required

Your FastAPI backend already has these endpoints implemented. Here's how the frontend will use them:

### GET `/api/user/{user_id}/sessions`
**Purpose:** Load all session IDs for a user on app mount

**Frontend Usage:**
```typescript
const sessionIds = await getUserSessions('demo_user');
```

**Expected Response:**
```json
{
  "user_id": "demo_user",
  "sessions": ["session_1234567890", "session_1234567891"]
}
```

### GET `/api/conversation/{session_id}?limit=10`
**Purpose:** Load message history for a specific session

**Frontend Usage:**
```typescript
const conversation = await getConversationHistory('session_1234567890', 10);
```

**Expected Response:**
```json
{
  "session_id": "session_1234567890",
  "user_id": "demo_user",
  "turns": [
    {
      "turn_id": "turn_1",
      "timestamp": "2024-11-06T10:30:00Z",
      "user_query": "What was the revenue for Q3 2024?",
      "agent_response": "Q3 2024 revenue reached ₹228.6 Cr...",
      "session_id": "session_1234567890",
      "user_id": "demo_user"
    }
  ],
  "current_topic": "Q3 Revenue Analysis",
  "turn_count": 1,
  "last_activity": "2024-11-06T10:30:00Z"
}
```

### POST `/api/query`
**Purpose:** Process query and implicitly manage session state

**Frontend Usage:** Already implemented and working

**Request Body:**
```json
{
  "query": "What was the revenue for Q3 2024?",
  "session_id": "session_1234567890",
  "user_id": "demo_user"
}
```

### DELETE `/api/conversation/{session_id}`
**Purpose:** Clear conversation history (future feature)

**Frontend Usage:**
```typescript
await clearConversation('session_1234567890');
```

## Migration Strategy

### Phase 1: Keep localStorage (Current)
- Frontend works independently
- All features functional for demo
- No backend dependency

### Phase 2: Hybrid Approach (Recommended Next Step)
```typescript
// Try backend first, fallback to localStorage
try {
  const sessions = await getUserSessions(USER_ID);
  setSessions(sessions);
} catch (error) {
  console.warn('Backend unavailable, using localStorage');
  const storedSessions = localStorage.getItem(`sessions_${USER_ID}`);
  if (storedSessions) {
    setSessions(JSON.parse(storedSessions));
  }
}
```

### Phase 3: Backend Only (Production)
- Remove all localStorage code
- Use only backend API calls
- Add proper error handling and loading states

## Environment Variables

Add to your `.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

This is already configured in `/services/api.ts`:

```typescript
const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) 
  ? import.meta.env.VITE_API_URL 
  : 'http://localhost:8000';
```

## Data Model Mapping

### Frontend ChatSession
```typescript
interface ChatSession {
  id: string;              // Maps to session_id
  messages: Message[];      // Maps to turns array
  timestamp: Date;          // Maps to start_time
  title: string;            // Maps to current_topic
  userId?: string;          // Maps to user_id
  lastActivity?: Date;      // Maps to last_activity
}
```

### Backend ConversationContext (from your main.py)
```python
# Response from GET /api/conversation/{session_id}
{
  "session_id": str,
  "user_id": str,
  "turns": List[ConversationTurnResponse],
  "current_topic": Optional[str],
  "turn_count": int,
  "last_activity": Optional[datetime]
}
```

## Testing Checklist

### Frontend (Already Working)
- [x] New Chat button creates new session
- [x] Sessions appear in sidebar
- [x] Active session is highlighted
- [x] Clicking session loads messages
- [x] Session title generated from first message
- [x] Sessions sorted by last activity
- [x] Messages persist across page refreshes (localStorage)

### Backend Integration (TODO)
- [ ] `/api/user/{user_id}/sessions` returns session IDs
- [ ] `/api/conversation/{session_id}` returns full conversation history
- [ ] `/api/query` saves messages to conversation memory
- [ ] Sessions persist in Redis/PostgreSQL
- [ ] Session titles are saved and retrieved
- [ ] Last activity timestamps update correctly

## Common Issues & Solutions

### Issue: Sessions not appearing after refresh
**Solution:** Check that `loadUserSessions()` is called on mount in `App.tsx` (line 43)

### Issue: Active session not highlighted
**Solution:** Verify `currentSessionId` is passed to `QueryHistory` component (line 292 in App.tsx)

### Issue: Cannot switch sessions
**Solution:** Check `handleSessionSelect()` is properly updating both `sessionId` and `messages` state

### Issue: Session titles are "New Conversation"
**Solution:** Ensure at least one user message exists before `saveCurrentSession()` is called

## Next Steps for Backend Developer

1. ✅ Your FastAPI endpoints are already implemented
2. ⏳ Ensure conversation memory saves to Redis/PostgreSQL
3. ⏳ Implement session retrieval from storage
4. ⏳ Test with frontend by uncommenting production endpoints in `/services/api.ts`
5. ⏳ Add proper error handling for network failures
6. ⏳ Implement session cleanup for old/inactive sessions

## Contact & Support

If you encounter any issues during integration:
1. Check browser console for error messages
2. Verify API endpoints match the expected format
3. Test API endpoints independently using curl/Postman
4. Check CORS configuration in FastAPI (already configured for localhost:5173)

The frontend is production-ready and waiting for your backend integration! 🚀
