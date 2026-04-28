# Conversation History with Visualizations

## Overview
Implemented full conversation history restoration that persists visualizations and action buttons across page refreshes.

## Problem Solved
Previously, when users refreshed the page, only the text insights were visible - visualizations and action buttons would disappear. Now the entire conversation state is restored from the backend.

## Implementation

### 1. Session ID Persistence
- Session ID is stored in `localStorage` as `currentSessionId`
- Saved whenever:
  - A new query is submitted
  - A new chat is created
  - A session is selected from history

### 2. Conversation Restoration on Page Load
When the app loads, it:
1. Checks `localStorage` for `currentSessionId`
2. Calls `/api/conversation/{session_id}` to fetch full history
3. Reconstructs messages with proper `queryResponse` objects
4. Restores visualizations from backend data
5. Sets the chat page as active if messages exist

### 3. Message Reconstruction
Each turn from the backend is transformed into two messages:

**User Message:**
```typescript
{
  id: `${turn.turn_id}_user`,
  type: 'user',
  content: turn.user_query,
  timestamp: new Date(turn.timestamp)
}
```

**Assistant Message with Visualizations:**
```typescript
{
  id: `${turn.turn_id}_assistant`,
  type: 'assistant',
  content: turn.agent_response,
  timestamp: new Date(turn.timestamp),
  queryResponse: {
    agent_responses: [{
      agent_name: AgentType.INSIGHTS,
      content: turn.agent_response,
      visualizations: turn.visualizations, // ← Restored from backend
      confidence: 0.8,
      execution_time: 0,
      follow_up_questions: []
    }],
    processing_stages: [
      { agent_name: AgentType.ORCHESTRATOR, status: 'completed' },
      { agent_name: AgentType.INSIGHTS, status: 'completed' },
      { agent_name: AgentType.VISUALIZATION, status: 'completed' }
    ],
    // ... other fields
  },
  isProcessing: false
}
```

### 4. Backend API Integration
Uses the existing API functions:
- `getConversationHistory(sessionId, limit)` - Fetches conversation turns
- `getUserSessions(userId)` - Gets list of user's sessions

### 5. Visualization Restoration
The key is that `turn.visualizations` from the backend contains the full Plotly visualization objects:
```json
{
  "type": "bar",
  "data": { "x": [...], "y": [...], "type": "bar" },
  "layout": { "title": "...", "xaxis": {...}, "yaxis": {...} },
  "config": { "responsive": true }
}
```

These are directly passed to the `VisualizationPanel` component, which renders them using Plotly.

### 6. Action Buttons Restoration
Since visualizations are restored in the `queryResponse.agent_responses[].visualizations` array, the `ChatMessage` component automatically shows the action buttons:

```tsx
{visualizations && visualizations.length > 0 && (
  <ActionButtons 
    messageContent={message.content}
    visualizations={visualizations}
  />
)}
```

## User Flow

### First Visit
1. User opens app → No `currentSessionId` in localStorage
2. Shows welcome screen
3. User asks a question → Session ID saved to localStorage
4. Visualizations and action buttons appear

### Page Refresh
1. User refreshes page
2. App reads `currentSessionId` from localStorage
3. Fetches conversation history from backend
4. Reconstructs all messages with visualizations
5. User sees complete conversation with all visualizations and action buttons

### Session Switching
1. User clicks on a previous session in sidebar
2. Session ID saved to localStorage
3. Messages loaded from that session
4. On refresh, that session is restored

## Key Files Modified

### `src/App.tsx`
- Added `restoreCurrentSession()` function
- Updated `loadUserSessions()` to properly reconstruct queryResponse
- Added localStorage persistence for `currentSessionId`
- Modified `handleNewChat()`, `handleSessionSelect()`, and `handleQuerySubmit()`

### `src/services/api.ts`
- Already had `getConversationHistory()` function
- Already had `getUserSessions()` function
- No changes needed

### `src/components/ChatMessage.tsx`
- No changes needed
- Already properly renders visualizations from `queryResponse`
- Already shows action buttons when visualizations exist

## Testing

1. **Test Restoration:**
   - Ask a question that generates visualizations
   - Refresh the page
   - Verify visualizations and action buttons are still visible

2. **Test Multiple Sessions:**
   - Create multiple conversations
   - Switch between them
   - Refresh page
   - Verify correct session is restored

3. **Test New Chat:**
   - Click "New Chat"
   - Refresh page
   - Verify empty chat (no previous messages)

## Backend Requirements

The backend must return conversation history in this format:

```json
{
  "session_id": "session_123",
  "user_id": "demo_user",
  "turn_count": 2,
  "current_topic": "revenue_analysis",
  "last_activity": "2025-11-11T10:30:00",
  "turns": [
    {
      "turn_id": "turn-1",
      "timestamp": "2025-11-11T10:25:00",
      "user_query": "Show me revenue trends",
      "agent_response": "Here's the revenue analysis...",
      "visualizations": [
        {
          "type": "line",
          "data": { "x": [...], "y": [...] },
          "layout": { "title": "Revenue Trends" },
          "config": { "responsive": true }
        }
      ]
    }
  ]
}
```

## Benefits

1. **Persistent State** - Users don't lose their work on refresh
2. **Better UX** - Seamless experience across sessions
3. **Full Fidelity** - Visualizations and action buttons fully restored
4. **Backend-Driven** - Single source of truth for conversation data
5. **Scalable** - Works with any number of visualizations per message

## Future Enhancements

1. Add loading indicator during restoration
2. Implement pagination for very long conversations
3. Add "Clear History" button
4. Cache conversation data to reduce API calls
5. Add offline support with service workers
