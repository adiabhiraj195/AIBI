# 🚀 Quick Start Guide - Testing with Real Backend

## Prerequisites

- ✅ Your FastAPI backend running at `http://localhost:8000`
- ✅ Node.js installed (v16 or higher)
- ✅ npm or yarn package manager

---

## Step 1: Start Your Backend

In your backend directory:

```bash
cd /path/to/your/backend
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**Verify Backend is Running:**
```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status": "healthy"}
```

---

## Step 2: Install Frontend Dependencies

In this frontend directory:

```bash
npm install
```

This will install all required packages including:
- React
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- Lucide icons
- And more...

---

## Step 3: Start Frontend Development Server

```bash
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## Step 4: Open Application

1. Open your browser
2. Navigate to: **http://localhost:5173**
3. Open browser console (F12) to see connection logs

---

## Step 5: Test Connection

### Visual Indicators:

**✅ Backend Connected:**
- Top-right shows green "Connected" badge
- Dashboard metrics show real data
- Queries process through backend agents

**⚠️ Backend Disconnected:**
- Top-right shows orange "Offline Mode" badge
- Application uses mock data
- All features still work with demo content

### Console Logs:

When backend is connected, you'll see:
```
[API] Checking backend health at: http://localhost:8000/health
[API] Backend health status: true
[API] Fetching system status
[API] System status: {apiHealth: true, ...}
```

When backend is disconnected:
```
[API] Backend health check failed: ...
[API] Backend connection failed, falling back to mock data
```

---

## Step 6: Test Core Features

### Test 1: Send a Query

1. Click **"Get Started"** on welcome page
2. Click **"Continue to Chat"** on dashboard
3. Type: `What was the revenue for Q3 2024?`
4. Press Enter

**Expected Behavior:**
- Agent pipeline appears showing all 5 agents
- Progress bars animate through stages
- Charts render in chat message
- Insights text appears (4-5 lines)
- Follow-up questions appear as clickable buttons

**Console Logs:**
```
[API] Sending query to backend: {query: "What was...", ...}
[API] Connected to backend successfully
[API] Received response: {...}
```

### Test 2: Check Session Persistence

1. Send a message (as above)
2. Refresh the page (F5)
3. Wait for page to load

**Expected Behavior:**
- Previous session appears in sidebar
- Session title matches your question
- Clicking the session loads the conversation

**Console Logs:**
```
[App] Loading user sessions for: demo_user
[API] Fetching sessions for user: demo_user
[API] Received sessions from backend: {sessions: [...]}
[API] Fetching conversation history for session: session_xxx
[App] Loaded sessions from backend: 1
```

### Test 3: Create Multiple Sessions

1. Click **"+ New Chat"** in sidebar
2. Send a different message
3. Check sidebar

**Expected Behavior:**
- Two sessions visible in sidebar
- Can switch between them
- Each maintains its own conversation

### Test 4: Use Follow-up Questions

1. After receiving a response
2. Click one of the follow-up question buttons
3. See new query being processed

**Expected Behavior:**
- Follow-up question appears as user message
- New response generated
- Context maintained from previous conversation

### Test 5: Dashboard Integration

1. Navigate to Dashboard (click "Dashboard" in sidebar)
2. Click on a metric card (e.g., "Total Revenue")
3. Gets redirected to chat with prefilled query

**Expected Behavior:**
- Automatically switches to chat page
- Query is sent immediately
- Results appear in chat

---

## Connection Status Indicator

In the top-right of the chat interface, you'll see a badge:

### 🟢 Connected
- Backend is reachable
- Real-time data and queries
- Sessions persist in backend database

### 🟠 Offline Mode
- Backend unavailable
- Uses mock data for queries
- Sessions saved in localStorage
- All features still functional

**Hover over the badge** for more details including:
- Backend URL
- Last connection check time
- Connection status

---

## Troubleshooting

### Issue 1: "Offline Mode" Badge Shows

**Possible Causes:**
1. Backend not running
2. Backend on different port
3. CORS not configured
4. Network issue

**Solutions:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check backend logs for errors
# Look for CORS errors in browser console

# Verify .env file
cat .env
# Should show: VITE_API_URL=http://localhost:8000
```

### Issue 2: CORS Errors in Console

**Error Message:**
```
Access to fetch at 'http://localhost:8000/api/query' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Solution:**
Add to your backend `main.py`:

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

### Issue 3: Sessions Not Persisting

**Symptoms:**
- Sessions disappear after refresh
- Empty array returned from backend

**Check:**
1. Is Redis running? `redis-cli ping` → Should return `PONG`
2. Does backend save sessions after `/api/query`?
3. Check backend logs for session save errors

**Temporary Workaround:**
Frontend automatically falls back to localStorage if backend sessions unavailable.

### Issue 4: Queries Return Mock Data

**Console Shows:**
```
[API] Backend connection failed, falling back to mock data
```

**Check:**
1. Is `/api/query` endpoint implemented?
2. Does it accept POST requests?
3. Does it return correct response format?

**Test Manually:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was the revenue for Q3 2024?",
    "session_id": "test_123",
    "user_id": "demo_user"
  }'
```

### Issue 5: TypeScript Errors

**Run:**
```bash
npm run build
```

This will show any TypeScript compilation errors.

### Issue 6: Port Already in Use

**Frontend Port (5173) in use:**
```bash
# Vite will automatically try 5174, 5175, etc.
# Or specify a different port:
npm run dev -- --port 3000
```

**Backend Port (8000) in use:**
```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port in backend
```

---

## Environment Configuration

### Frontend `.env` File

Located at project root: `.env`

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# User ID for testing
VITE_DEFAULT_USER_ID=demo_user

# Enable debug logging
VITE_DEBUG_MODE=true
```

**To use different backend URL:**
```env
VITE_API_URL=http://192.168.1.100:8000  # Local network
VITE_API_URL=https://api.yourcompany.com  # Production
```

After changing `.env`, restart the dev server:
```bash
# Stop: Ctrl+C
npm run dev
```

---

## Development Tips

### Hot Reload

Frontend has hot module replacement (HMR):
- Edit any `.tsx` file
- Changes appear instantly in browser
- No need to refresh

### Console Logging

All API calls are logged with `[API]` prefix:
```
[API] Sending query to backend: ...
[API] Connected to backend successfully
[API] Received response: ...
```

All app-level logs use `[App]` prefix:
```
[App] Loading user sessions for: demo_user
[App] Loaded sessions from backend: 3
```

### Network Tab

Open browser DevTools → Network tab to see:
- All API requests
- Request/response payloads
- Response times
- Status codes

---

## Production Build

When ready to deploy:

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

Output files will be in `dist/` directory.

---

## Testing Scenarios

### Scenario 1: Full User Journey
```
1. Open app → Welcome page
2. Get Started → Dashboard
3. Click metric card → Chat with query
4. Send message → See agent pipeline
5. View charts → Embedded in chat
6. Click follow-up → Continue conversation
7. Refresh → Session persists
8. Switch sessions → Load previous chats
```

### Scenario 2: Offline Functionality
```
1. Stop backend server
2. Frontend still works
3. Uses mock data
4. Sessions in localStorage
5. All UI functional
6. Restart backend → Reconnects automatically
```

### Scenario 3: Multi-Session Workflow
```
1. Start conversation about revenue
2. Create new chat
3. Ask about projects
4. Create new chat
5. Ask about forecasts
6. All 3 sessions in sidebar
7. Switch between them
8. Each maintains context
```

---

## Next Steps

After testing locally:

1. ✅ Verify all backend endpoints work
2. ✅ Test session persistence across refreshes
3. ✅ Try all agent types (visualization, insights, forecasting)
4. ✅ Test error handling (invalid queries, network issues)
5. ✅ Performance testing (query response times)
6. 📝 Configure production environment
7. 🚀 Deploy to staging/production

---

## Resources

- **API Documentation:** `/BACKEND_TESTING.md`
- **Session Integration:** `/SESSION_INTEGRATION.md`
- **Backend Integration:** `/BACKEND_SESSION_INTEGRATION.md`
- **Architecture:** `/ARCHITECTURE.md`
- **Project Overview:** `/PROJECT_OVERVIEW.md`

---

## Support

### Check Logs

**Frontend Console:**
- Press F12 in browser
- Look for `[API]` and `[App]` prefixed logs

**Backend Logs:**
- Check terminal where `python main.py` is running
- Look for request logs and errors

### Common Questions

**Q: Do I need Redis?**
A: Only if you want backend session persistence. Frontend works without it using localStorage.

**Q: Can I use a different port?**
A: Yes, update `VITE_API_URL` in `.env` and restart dev server.

**Q: Does it work without backend?**
A: Yes! Frontend has complete fallback to mock data and localStorage.

**Q: How do I deploy to production?**
A: Run `npm run build`, deploy `dist/` folder to any static host (Vercel, Netlify, S3, etc.)

---

**You're all set! Start both servers and begin testing.** 🎉

**Backend:** `python main.py`
**Frontend:** `npm run dev`
**Open:** `http://localhost:5173`
