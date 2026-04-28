# Session Management Testing Guide

## Quick Testing Checklist

### ✅ Feature 1: New Chat Creation
**How to test:**
1. Click "New Chat" button in sidebar
2. Verify empty chat interface appears
3. Send a message
4. Check that session appears in sidebar with message as title

**Expected behavior:**
- Session ID changes (visible in browser console if you add logging)
- Messages array is cleared
- New session appears in sidebar after first message

### ✅ Feature 2: Session Persistence
**How to test:**
1. Send a few messages in a chat
2. Refresh the page (F5)
3. Check sidebar for your session

**Expected behavior:**
- Session appears in sidebar with title from first message
- Clicking the session loads all your messages

### ✅ Feature 3: Session Switching
**How to test:**
1. Create multiple chat sessions (click "New Chat" between each)
2. Send different messages in each session
3. Click on different sessions in sidebar

**Expected behavior:**
- Messages change when you click different sessions
- Active session is highlighted in emerald green
- Current session updates when you click

### ✅ Feature 4: Session Titles
**How to test:**
1. Create a new chat
2. Send message: "What was the revenue for Q3 2024?"
3. Check sidebar

**Expected behavior:**
- Title shows: "What was the revenue for Q3 2024?" (or truncated if > 50 chars)
- Empty sessions show: "New Conversation"

### ✅ Feature 5: Session Ordering
**How to test:**
1. Create 3 sessions on different days (you can modify localStorage to test)
2. Check sidebar organization

**Expected behavior:**
- Today's sessions appear under "Today" section
- Older sessions appear under "Previous" section
- Sessions sorted by last activity time (newest first)

### ✅ Feature 6: Active Session Highlighting
**How to test:**
1. Create 2 sessions
2. Click between them

**Expected behavior:**
- Active session has emerald green background
- Active session has emerald icon and text
- Other sessions remain gray

## Browser Console Tests

Open browser DevTools (F12) and run these commands:

### View Stored Sessions
```javascript
JSON.parse(localStorage.getItem('sessions_demo_user'))
```

### Clear All Sessions (Reset)
```javascript
localStorage.removeItem('sessions_demo_user')
location.reload()
```

### Count Sessions
```javascript
JSON.parse(localStorage.getItem('sessions_demo_user')).length
```

### View Current Session Data
```javascript
JSON.parse(localStorage.getItem('sessions_demo_user'))[0]
```

## Common Test Scenarios

### Scenario 1: New User Experience
1. Open app for first time
2. Navigate to chat
3. Sidebar shows "No chat history yet"
4. Send first message
5. Session appears in sidebar

### Scenario 2: Returning User
1. User has 5 existing sessions
2. Opens app
3. All sessions load in sidebar
4. Can switch between any session
5. Can create new session

### Scenario 3: Multi-Day Usage
1. User has sessions from:
   - Today (2 sessions)
   - Yesterday (3 sessions)
   - Last week (5 sessions)
2. Today's sessions appear under "Today"
3. Older sessions appear under "Previous"

### Scenario 4: Dashboard → Chat Flow
1. User clicks metric card on dashboard
2. Query is sent
3. User navigates to chat page
4. Session is created with query
5. Session appears in sidebar

## Backend Integration Test Points

When connecting to your FastAPI backend:

### Test 1: Session Creation
```bash
# Send a query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was the revenue for Q3 2024?",
    "session_id": "session_1234567890",
    "user_id": "demo_user"
  }'

# Verify session was saved
curl http://localhost:8000/api/user/demo_user/sessions
```

### Test 2: Session Retrieval
```bash
# Get all user sessions
curl http://localhost:8000/api/user/demo_user/sessions

# Get specific conversation
curl http://localhost:8000/api/conversation/session_1234567890?limit=10
```

### Test 3: Session Summary
```bash
# Get session summary
curl http://localhost:8000/api/conversation/session_1234567890/summary
```

## Performance Tests

### Load Time Test
1. Create 50+ sessions
2. Refresh page
3. Measure time to load and render all sessions

**Expected:** < 500ms for 50 sessions

### Switch Speed Test
1. Create 10 sessions with 20 messages each
2. Click through sessions rapidly

**Expected:** Instant switching (< 100ms)

### Save Speed Test
1. Send message in session
2. Check localStorage save time

**Expected:** < 50ms (synchronous)

## Edge Cases to Test

### Edge Case 1: Very Long Message Title
- Send message: "This is a very long query that should be truncated when used as session title because it exceeds the 50 character limit"
- Expected: Title truncated to 50 chars with "..."

### Edge Case 2: Empty Session
- Create new chat but don't send any messages
- Expected: Session titled "New Conversation"

### Edge Case 3: Rapid Session Creation
- Click "New Chat" 5 times rapidly
- Expected: 5 distinct sessions created

### Edge Case 4: localStorage Quota
- Create 1000+ sessions
- Expected: Graceful error handling (console.error logged)

### Edge Case 5: Corrupted localStorage
```javascript
// Corrupt the data
localStorage.setItem('sessions_demo_user', 'invalid json{]')
location.reload()
```
- Expected: Error caught, empty session list shown

## Visual Regression Tests

### Sidebar States
- ✅ Empty state (no sessions)
- ✅ Single session (active)
- ✅ Multiple sessions (one active)
- ✅ Today + Previous sections
- ✅ Collapsed sidebar
- ✅ Expanded sidebar

### Session Card States
- ✅ Normal (inactive)
- ✅ Hover
- ✅ Active
- ✅ Long title (ellipsis)
- ✅ Short title

## Debugging Tips

### Issue: Sessions not appearing
**Check:**
```javascript
// Is data in localStorage?
localStorage.getItem('sessions_demo_user')

// Is sessions state populated?
// Add console.log in App.tsx after setSessions()
```

### Issue: Session not switching
**Check:**
```javascript
// Add logging to handleSessionSelect:
console.log('Switching from', sessionId, 'to', selectedSessionId);
console.log('Found session:', selectedSession);
```

### Issue: Active session not highlighted
**Check:**
```javascript
// In browser DevTools, inspect QueryHistory component
// Verify currentSessionId prop is passed correctly
```

### Issue: Title not updating
**Check:**
```javascript
// In saveCurrentSession, log:
console.log('First user message:', firstUserMessage);
console.log('Generated title:', title);
```

## Success Criteria

All tests pass when:
- ✅ New sessions can be created
- ✅ Sessions persist across page refreshes  
- ✅ Sessions can be switched
- ✅ Active session is visually highlighted
- ✅ Session titles are generated correctly
- ✅ Sessions are sorted by activity
- ✅ Today/Previous grouping works
- ✅ No console errors
- ✅ UI remains responsive with 50+ sessions

## Next Steps After Testing

1. Uncomment production endpoints in `/services/api.ts`
2. Test with real FastAPI backend
3. Verify backend session storage in Redis/PostgreSQL
4. Add error handling for network failures
5. Add loading states during session fetch
6. Implement session deletion feature
7. Add session export/import functionality
