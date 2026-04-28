# Testing Checklist - Backend Integration

## Pre-Flight Checks

### Backend Setup
- [ ] Backend is running: `python main.py`
- [ ] Backend accessible at `http://localhost:8000`
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] CORS configured for `http://localhost:5173`
- [ ] Redis is running (for session persistence): `redis-cli ping`
- [ ] Database connection established

### Frontend Setup
- [ ] Dependencies installed: `npm install`
- [ ] `.env` file configured with `VITE_API_URL=http://localhost:8000`
- [ ] Development server started: `npm run dev`
- [ ] Browser open at `http://localhost:5173`
- [ ] Browser console open (F12)

---

## Automated Tests

### Run Test Scripts

**Linux/Mac:**
```bash
chmod +x test-backend.sh
./test-backend.sh
```

**Windows:**
```cmd
test-backend.bat
```

**Expected:** All tests return status 200

---

## Manual Testing

### 1. Connection Status

**Test:** Open application in browser

**Expected:**
- [ ] Top-right badge shows 🟢 "Connected"
- [ ] Console logs: `[API] Backend health status: true`
- [ ] No CORS errors in console
- [ ] No 404 or 500 errors in Network tab

**If Failed:**
- Check backend is running
- Verify CORS configuration
- Check `.env` file

---

### 2. System Status Dashboard

**Test:** Navigate to Dashboard page

**Steps:**
1. Click "Get Started" on welcome page
2. View dashboard

**Expected:**
- [ ] All metric cards display
- [ ] Green status indicators
- [ ] Database connection shown
- [ ] No loading spinners stuck
- [ ] Console logs: `[API] Fetching system status`

**If Failed:**
- Check `/api/system/status` endpoint
- Check `/api/system/database` endpoint
- Verify response format matches types

---

### 3. Send First Query

**Test:** Send a simple query

**Steps:**
1. Click "Continue to Chat" from dashboard
2. Type: `What was the revenue for Q3 2024?`
3. Press Enter

**Expected:**
- [ ] User message appears immediately
- [ ] Assistant message shows "Analyzing your query..."
- [ ] Agent pipeline displays with 5 agents
- [ ] Progress bars animate (pending → processing → completed)
- [ ] Charts render in message
- [ ] Insights text appears (4-5 lines)
- [ ] Follow-up questions appear as buttons
- [ ] Message marked as complete (no spinner)

**Console Logs:**
```
[API] Sending query to backend: {...}
[API] Connected to backend successfully
[API] Received response: {...}
```

**If Failed:**
- Check `/api/query` endpoint exists
- Verify POST request in Network tab
- Check response format
- Look for backend errors

---

### 4. Agent Pipeline Progress

**Test:** Watch agent pipeline during query

**Expected:**
- [ ] **Orchestrator:** Pending → Processing → Completed (~400ms)
- [ ] **Visualization:** Pending → Processing → Completed (~800ms)
- [ ] **Insights:** Pending → Processing → Completed (~900ms)
- [ ] **Forecasting:** Shows if forecast query (skip if not)
- [ ] **Follow-Up:** Pending → Processing → Completed (~500ms)
- [ ] All stages show green checkmarks when done
- [ ] Duration shown for each stage
- [ ] Total execution time displayed

**If Failed:**
- Check backend sends `processing_stages` in response
- Verify stage status updates
- Check agent names match exactly

---

### 5. Visualizations

**Test:** Charts display correctly

**Expected:**
- [ ] Chart container appears
- [ ] Plotly chart renders
- [ ] Interactive features work (zoom, pan, hover)
- [ ] Dark theme applied
- [ ] Responsive sizing
- [ ] No console errors about Plotly

**If Failed:**
- Check visualization data format
- Verify Plotly data structure
- Check chart type is valid

---

### 6. CFO Insights

**Test:** Insights display correctly

**Expected:**
- [ ] Summary text (4-5 lines)
- [ ] Key metrics section with 4-6 metrics
- [ ] Each metric shows: name, value, unit, trend
- [ ] Trend indicators (↑ ↓ →)
- [ ] Color coding (green/red/gray)
- [ ] Recommendations list (3-4 items)
- [ ] Risk flags (if any)

**If Failed:**
- Check `cfo_response` in backend response
- Verify field names match types
- Check data structure

---

### 7. Follow-Up Questions

**Test:** Click follow-up question button

**Steps:**
1. Wait for query to complete
2. Click one of the 4 follow-up question buttons
3. Observe new query processing

**Expected:**
- [ ] Clicked question appears as user message
- [ ] New assistant response generated
- [ ] Agent pipeline runs again
- [ ] Context from previous query maintained
- [ ] New follow-ups relevant to conversation

**Console Logs:**
```
[API] Sending query to backend: {query: "What is the breakdown...", ...}
```

**If Failed:**
- Check follow-up questions array in response
- Verify button click handlers
- Check session context maintained

---

### 8. Session Creation

**Test:** Session appears in sidebar

**Steps:**
1. Send first message (as in Test 3)
2. Check sidebar

**Expected:**
- [ ] New session appears in "Recent Sessions"
- [ ] Session title matches first question
- [ ] Timestamp shows current time
- [ ] Session is highlighted as active
- [ ] Session shows message count

**If Failed:**
- Check session creation logic
- Verify localStorage or backend save
- Check session title generation

---

### 9. Multiple Sessions

**Test:** Create and manage multiple sessions

**Steps:**
1. Send message in Session A
2. Click "+ New Chat" button
3. Send different message in Session B
4. Click "+ New Chat" again
5. Send message in Session C
6. Click Session A in sidebar

**Expected:**
- [ ] 3 sessions visible in sidebar
- [ ] Each has unique ID
- [ ] Each has different title
- [ ] Clicking switches between them
- [ ] Messages persist in each session
- [ ] Active session highlighted
- [ ] Sessions sorted by last activity

**If Failed:**
- Check new session creation
- Verify session switching logic
- Check session state management

---

### 10. Session Persistence (Backend)

**Test:** Sessions survive page refresh

**Steps:**
1. Send 2-3 messages in a session
2. Note the session ID
3. Refresh page (F5)
4. Wait for page to load

**Expected:**
- [ ] Previous session appears in sidebar
- [ ] Session title preserved
- [ ] Clicking session loads all messages
- [ ] Messages in correct order
- [ ] Agent responses preserved
- [ ] Charts re-render correctly

**Console Logs:**
```
[App] Loading user sessions for: demo_user
[API] Fetching sessions for user: demo_user
[API] Received sessions from backend: {sessions: [...]}
[API] Fetching conversation history for session: session_xxx
[App] Loaded sessions from backend: 1
```

**If Failed:**
- Check backend session storage
- Verify Redis is saving data
- Test session endpoints manually
- Check conversation history format

---

### 11. Session Persistence (LocalStorage Fallback)

**Test:** Sessions work when backend unavailable

**Steps:**
1. Stop backend server
2. Refresh frontend page
3. Send a message
4. Refresh page again

**Expected:**
- [ ] "Offline Mode" badge shows
- [ ] Can still send messages (mock data)
- [ ] Sessions saved to localStorage
- [ ] Sessions persist after refresh
- [ ] All UI features work

**Console Logs:**
```
[API] Backend unavailable for session fetch, using localStorage fallback
[API] Backend connection failed, falling back to mock data
```

---

### 12. Offline Mode

**Test:** Graceful degradation when backend down

**Steps:**
1. Stop backend server: Ctrl+C in backend terminal
2. Wait 30 seconds (for connection check)
3. Try sending query

**Expected:**
- [ ] Badge changes to 🟠 "Offline Mode"
- [ ] Tooltip explains using mock data
- [ ] Queries still process
- [ ] Mock data returned
- [ ] Agent pipeline still shows
- [ ] Charts still render
- [ ] No UI crashes
- [ ] Helpful message displayed

**If Failed:**
- Check fallback logic in api.ts
- Verify mock data generators work
- Check error handling

---

### 13. Reconnection

**Test:** Automatic reconnection when backend returns

**Steps:**
1. Backend is stopped (from Test 12)
2. Badge shows "Offline Mode"
3. Restart backend: `python main.py`
4. Wait 30 seconds (auto-check interval)

**Expected:**
- [ ] Badge automatically changes to "Connected"
- [ ] Next query uses real backend
- [ ] No page refresh needed
- [ ] Console logs show successful connection

**Console Logs:**
```
[API] Backend health status: true
```

---

### 14. Query with Visualization Intent

**Test:** Query that should generate charts

**Steps:**
1. Type: `Show me the revenue trend over the last 4 quarters`
2. Send query

**Expected:**
- [ ] Orchestrator routes to Visualization agent
- [ ] Line chart or bar chart renders
- [ ] Chart shows quarterly data
- [ ] X-axis labeled with quarters
- [ ] Y-axis shows revenue values
- [ ] Chart is interactive

---

### 15. Query with Forecasting Intent

**Test:** Query that triggers forecasting agent

**Steps:**
1. Type: `Forecast the Q4 2024 revenue`
2. Send query

**Expected:**
- [ ] Orchestrator routes to Forecasting agent
- [ ] Forecasting agent stage appears
- [ ] Prophet or XGBoost mentioned
- [ ] Confidence intervals shown
- [ ] Forecast visualization appears
- [ ] Future period predictions displayed

---

### 16. Navigation

**Test:** Navigate between pages

**Steps:**
1. Start at chat
2. Click "Dashboard" in sidebar
3. Click "Welcome" in sidebar
4. Click "Get Started"
5. Click logo to go home

**Expected:**
- [ ] Smooth transitions
- [ ] State preserved when returning
- [ ] No console errors
- [ ] Active page highlighted
- [ ] Back button works

---

### 17. Sidebar Toggle

**Test:** Collapse and expand sidebar

**Steps:**
1. Click collapse button (← icon)
2. Sidebar hides
3. Click expand button (→ icon)
4. Sidebar shows

**Expected:**
- [ ] Sidebar smoothly animates
- [ ] Chat area expands/contracts
- [ ] State preserved
- [ ] Button icons change
- [ ] Responsive behavior

---

### 18. Error Handling

**Test:** Invalid query

**Steps:**
1. Type gibberish: `asdjkfhasdkjfh`
2. Send query

**Expected:**
- [ ] Backend handles gracefully
- [ ] Or fallback provides response
- [ ] No UI crash
- [ ] Error message displayed
- [ ] Can continue using app

---

### 19. Long Conversation

**Test:** Send 10+ messages

**Steps:**
1. Send 10 different queries
2. Scroll through conversation
3. Check performance

**Expected:**
- [ ] All messages display
- [ ] Scrolling smooth
- [ ] No memory leaks
- [ ] Charts render correctly
- [ ] Follow-ups work
- [ ] Session updates

---

### 20. Network Tab Verification

**Test:** Inspect network requests

**Steps:**
1. Open DevTools → Network tab
2. Send a query
3. Watch requests

**Expected Requests:**
- [ ] `POST /api/query` - Status 200
- [ ] Request payload has query, session_id, user_id
- [ ] Response has all required fields
- [ ] Response time reasonable (< 5s)
- [ ] Content-Type correct

---

## Backend Response Validation

### Check Response Structure

For each query, verify backend returns:

```json
{
  "query_intent": {
    "intent_type": "insights",
    "confidence": 0.89,
    "entities": [...],
    "temporal_scope": "Q3 2024"
  },
  "agent_responses": [
    {
      "agent_name": "Visualization",
      "content": "...",
      "visualizations": [...],
      "confidence": 0.92,
      "execution_time": 780,
      "follow_up_questions": []
    },
    {
      "agent_name": "Insights",
      "content": "...",
      "cfo_response": {
        "summary": "...",
        "key_metrics": [...],
        "recommendations": [...],
        "risk_flags": [...]
      }
    }
  ],
  "processing_stages": [...],
  "conversation_context": {...},
  "total_execution_time": 2030,
  "timestamp": "2024-11-06T10:30:45.123Z"
}
```

---

## Performance Benchmarks

Expected timings (with real backend):

- [ ] Health check: < 100ms
- [ ] Session list: < 500ms
- [ ] Load conversation: < 1000ms
- [ ] Query processing: 2-5 seconds
- [ ] Chart rendering: < 1 second
- [ ] Page load: < 2 seconds

---

## Browser Compatibility

Test in:

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Mobile Responsiveness

Test on:

- [ ] Mobile viewport (375px)
- [ ] Tablet viewport (768px)
- [ ] Desktop viewport (1920px)

**Expected:**
- Sidebar collapses on mobile
- Charts responsive
- Touch-friendly buttons
- Readable text

---

## Console Verification

### Expected Logs (Backend Connected)

```
[API] Checking backend health at: http://localhost:8000/health
[API] Backend health status: true
[App] Loading user sessions for: demo_user
[API] Fetching sessions for user: demo_user
[API] Received sessions from backend: {...}
[API] Sending query to backend: {...}
[API] Connected to backend successfully
[API] Received response: {...}
```

### No Errors

- [ ] No CORS errors
- [ ] No 404 errors
- [ ] No TypeScript errors
- [ ] No React warnings
- [ ] No Plotly errors

---

## Final Verification

### Production Readiness

- [ ] All 20 manual tests pass
- [ ] Backend response format correct
- [ ] Session persistence works
- [ ] Offline mode functional
- [ ] Error handling robust
- [ ] Performance acceptable
- [ ] No console errors
- [ ] No memory leaks
- [ ] Responsive design works
- [ ] Cross-browser compatible

---

## Sign Off

**Tested By:** _________________

**Date:** _________________

**Backend Version:** _________________

**Frontend Version:** _________________

**Status:** ⬜ Pass  ⬜ Fail  ⬜ Needs Work

**Notes:**

```
_____________________________________________________
_____________________________________________________
_____________________________________________________
```

---

**Next Steps:**

- [ ] Deploy to staging environment
- [ ] User acceptance testing
- [ ] Performance testing at scale
- [ ] Security audit
- [ ] Production deployment

---

**You've completed the testing checklist!** 🎉

If all tests pass, your integration is successful and ready for the next phase.
