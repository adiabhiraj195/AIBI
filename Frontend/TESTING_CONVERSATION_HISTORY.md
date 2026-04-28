# Testing Conversation History with Visualizations

## Backend Changes Summary
Your backend now properly:
1. Serializes visualizations using Pydantic's `model_dump()` or `dict()`
2. Returns visualizations in conversation history endpoint
3. Converts visualization dicts to `PlotlyChart` objects in the response

## Frontend Implementation
The frontend now:
1. Stores `currentSessionId` in localStorage
2. Restores conversation history on page load
3. Reconstructs `queryResponse` objects with visualizations
4. Displays action buttons automatically when visualizations exist

## Test Scenarios

### Test 1: Basic Visualization Persistence
**Steps:**
1. Open the app (http://localhost:3000)
2. Ask: "Show me revenue trends by quarter"
3. Wait for visualization to appear
4. Verify action buttons appear below visualization
5. **Refresh the page (F5 or Cmd+R)**
6. ✅ Verify visualization is still visible
7. ✅ Verify action buttons are still visible
8. ✅ Verify you can click the buttons and popups work

**Expected Result:**
- Visualization persists after refresh
- Action buttons persist after refresh
- All interactive features work

### Test 2: Multiple Visualizations
**Steps:**
1. Start a new chat
2. Ask: "Show me project pipeline breakdown by phase"
3. Wait for visualizations to appear
4. Note how many visualizations are shown
5. **Refresh the page**
6. ✅ Verify all visualizations are restored
7. ✅ Verify you can switch between visualization tabs
8. ✅ Verify action buttons work

**Expected Result:**
- All visualizations restored
- Tab navigation works
- Action buttons functional

### Test 3: Multiple Messages with Visualizations
**Steps:**
1. Start a new chat
2. Ask: "What was the revenue for Q3 2024?"
3. Wait for response with visualization
4. Ask: "Show me customer concentration"
5. Wait for second response with visualization
6. **Refresh the page**
7. ✅ Verify both messages are restored
8. ✅ Verify both visualizations are visible
9. ✅ Verify action buttons appear on both messages

**Expected Result:**
- Complete conversation history restored
- All visualizations visible
- Action buttons on all messages with visualizations

### Test 4: Session Switching
**Steps:**
1. Create first conversation with visualizations
2. Click "New Chat"
3. Create second conversation with different visualizations
4. Click on first session in sidebar
5. ✅ Verify first conversation's visualizations appear
6. **Refresh the page**
7. ✅ Verify first conversation is still active
8. Click on second session
9. ✅ Verify second conversation's visualizations appear

**Expected Result:**
- Session switching works correctly
- Visualizations switch with sessions
- Refresh maintains current session

### Test 5: Action Buttons After Refresh
**Steps:**
1. Ask a question that generates visualizations
2. **Refresh the page**
3. Click "Track / Monitor" button
4. ✅ Verify popup shows correct monitoring type
5. Close popup
6. Click "Set Reminder" button
7. ✅ Verify reminder popup works
8. Close popup
9. Click "Send Mail" button
10. ✅ Verify email popup works

**Expected Result:**
- All action buttons functional after refresh
- Popups display correct information
- No errors in console

### Test 6: Save as Favorite After Refresh
**Steps:**
1. Ask a question that generates visualizations
2. **Refresh the page**
3. Click "Save as Favorite" button at top of message
4. ✅ Verify toast notification appears
5. ✅ Verify no errors in console

**Expected Result:**
- Favorite button works after refresh
- Toast notification displays correctly

## Debugging

### Check Browser Console
Open DevTools (F12) and look for:

```javascript
// Should see these logs on page load:
[App] Restoring session: session_xxxxx
[API] Fetching conversation history for session: session_xxxxx
[API] Received conversation history: {...}
[App] Restored X messages with visualizations

// Should see these logs when rendering:
[ChatMessage] Query response: {...}
[ChatMessage] Visualizations found: [...]
[VisualizationPanel] Received visualizations: [...]
```

### Check localStorage
In DevTools Console, run:
```javascript
localStorage.getItem('currentSessionId')
// Should return: "session_1234567890"
```

### Check Network Tab
1. Open DevTools → Network tab
2. Refresh page
3. Look for request to: `/api/conversation/session_xxxxx`
4. Check response contains `turns` array with `visualizations`

### Common Issues

**Issue: Visualizations don't appear after refresh**
- Check: Does backend response include `visualizations` array?
- Check: Are visualizations in correct format (type, data, layout)?
- Check: Console for errors in VisualizationPanel

**Issue: Action buttons don't appear**
- Check: Are visualizations in `agent_responses[0].visualizations`?
- Check: Is `visualizations.length > 0`?
- Check: ChatMessage component rendering logic

**Issue: Wrong session restored**
- Check: `localStorage.getItem('currentSessionId')`
- Clear localStorage: `localStorage.clear()`
- Start fresh session

## Backend API Verification

Test your backend endpoint directly:

```bash
# Get conversation history
curl http://localhost:8000/api/conversation/session_xxxxx

# Expected response:
{
  "session_id": "session_xxxxx",
  "user_id": "demo_user",
  "turn_count": 2,
  "turns": [
    {
      "turn_id": "turn-1",
      "timestamp": "2025-11-11T10:25:00",
      "user_query": "Show me revenue trends",
      "agent_response": "Here's the analysis...",
      "visualizations": [
        {
          "type": "line",
          "data": { "traces": [...] },
          "layout": { "title": "Revenue Trends" },
          "config": { "responsive": true }
        }
      ]
    }
  ]
}
```

## Success Criteria

✅ Visualizations persist after page refresh
✅ Action buttons persist after page refresh  
✅ Multiple visualizations all restored
✅ Session switching maintains visualizations
✅ All popups functional after refresh
✅ No console errors
✅ localStorage properly stores session ID
✅ Backend returns visualizations in correct format

## Performance Notes

- First load: ~500ms (fetches conversation history)
- Subsequent renders: Instant (data already loaded)
- Large conversations (50+ turns): May need pagination
- Multiple visualizations: Renders efficiently with tabs

## Next Steps

After testing, consider:
1. Add loading spinner during restoration
2. Implement conversation pagination
3. Add "Export Conversation" feature
4. Cache conversation data for offline access
5. Add conversation search functionality
