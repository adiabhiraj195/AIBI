# Frontend: Conversation History with Visualizations

## Overview
The backend now properly stores and returns visualizations with conversation history. When users refresh the page, you can restore the entire chat including all visualizations.

## API Endpoint

### GET `/api/conversation/{session_id}`

Retrieves full conversation history including visualizations.

**Parameters:**
- `session_id` (path): The session identifier
- `limit` (query, optional): Number of turns to retrieve (default: 10)

**Response:**
```json
{
  "session_id": "abc-123",
  "user_id": "user_456",
  "turn_count": 3,
  "current_topic": "capacity_analysis",
  "last_activity": "2025-11-11T10:30:00",
  "turns": [
    {
      "turn_id": "turn-1",
      "timestamp": "2025-11-11T10:25:00",
      "user_query": "Show me total capacity by state",
      "agent_response": "Here's the capacity breakdown by state...",
      "visualizations": [
        {
          "type": "bar",
          "data": {
            "x": ["California", "Texas", "New York"],
            "y": [1500, 2000, 1200],
            "type": "bar",
            "name": "Capacity (MW)"
          },
          "layout": {
            "title": "Total Capacity by State",
            "xaxis": {"title": "State"},
            "yaxis": {"title": "Capacity (MW)"}
          },
          "config": {
            "responsive": true
          }
        }
      ],
      "session_id": "abc-123",
      "user_id": "user_456"
    }
  ]
}
```

## Frontend Implementation

### 1. Store Session ID
```javascript
// Store session ID in localStorage or state management
const sessionId = localStorage.getItem('sessionId') || generateNewSessionId();
localStorage.setItem('sessionId', sessionId);
```

### 2. Restore Conversation on Page Load
```javascript
async function restoreConversation(sessionId) {
  try {
    const response = await fetch(`/api/conversation/${sessionId}`);
    const data = await response.json();
    
    // Restore each turn
    data.turns.forEach(turn => {
      // Add user message
      addMessageToChat({
        role: 'user',
        content: turn.user_query,
        timestamp: turn.timestamp
      });
      
      // Add assistant message with visualizations
      addMessageToChat({
        role: 'assistant',
        content: turn.agent_response,
        visualizations: turn.visualizations,
        timestamp: turn.timestamp
      });
    });
    
    console.log(`Restored ${data.turn_count} conversation turns`);
  } catch (error) {
    console.error('Failed to restore conversation:', error);
  }
}

// Call on page load
window.addEventListener('DOMContentLoaded', () => {
  const sessionId = localStorage.getItem('sessionId');
  if (sessionId) {
    restoreConversation(sessionId);
  }
});
```

### 3. Render Visualizations
```javascript
function addMessageToChat(message) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${message.role}`;
  
  // Add text content
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  contentDiv.textContent = message.content;
  messageDiv.appendChild(contentDiv);
  
  // Add visualizations if present
  if (message.visualizations && message.visualizations.length > 0) {
    message.visualizations.forEach((viz, index) => {
      const vizContainer = document.createElement('div');
      vizContainer.id = `viz-${Date.now()}-${index}`;
      vizContainer.className = 'visualization-container';
      messageDiv.appendChild(vizContainer);
      
      // Render with Plotly
      Plotly.newPlot(vizContainer, viz.data, viz.layout, viz.config);
    });
  }
  
  chatContainer.appendChild(messageDiv);
}
```

### 4. React Example
```jsx
import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [sessionId] = useState(() => 
    localStorage.getItem('sessionId') || generateSessionId()
  );

  useEffect(() => {
    // Restore conversation on mount
    async function loadHistory() {
      try {
        const response = await fetch(`/api/conversation/${sessionId}`);
        const data = await response.json();
        
        const restoredMessages = data.turns.flatMap(turn => [
          {
            role: 'user',
            content: turn.user_query,
            timestamp: turn.timestamp
          },
          {
            role: 'assistant',
            content: turn.agent_response,
            visualizations: turn.visualizations,
            timestamp: turn.timestamp
          }
        ]);
        
        setMessages(restoredMessages);
      } catch (error) {
        console.error('Failed to load conversation history:', error);
      }
    }
    
    loadHistory();
  }, [sessionId]);

  return (
    <div className="chat-container">
      {messages.map((msg, idx) => (
        <div key={idx} className={`message ${msg.role}`}>
          <div className="message-content">{msg.content}</div>
          
          {msg.visualizations?.map((viz, vizIdx) => (
            <Plot
              key={vizIdx}
              data={viz.data}
              layout={viz.layout}
              config={viz.config}
            />
          ))}
        </div>
      ))}
    </div>
  );
}
```

## Key Points

1. **Session Management**: Always use the same `session_id` for a user's conversation
2. **Visualization Format**: Visualizations are Plotly-compatible objects with `data`, `layout`, and `config`
3. **Empty Arrays**: If no visualizations exist, the field will be an empty array `[]`
4. **Order**: Turns are returned in chronological order (oldest first)
5. **Limit**: Use the `limit` parameter to control how many turns to retrieve

## Testing

Test the conversation history endpoint:

```bash
# Get conversation history
curl http://localhost:8000/api/conversation/your-session-id

# With limit
curl http://localhost:8000/api/conversation/your-session-id?limit=5
```

## Clear Conversation

To clear conversation history (e.g., "New Chat" button):

```javascript
async function clearConversation(sessionId) {
  await fetch(`/api/conversation/${sessionId}`, {
    method: 'DELETE'
  });
  
  // Generate new session ID
  const newSessionId = generateSessionId();
  localStorage.setItem('sessionId', newSessionId);
  
  // Clear UI
  setMessages([]);
}
```

## Error Handling

```javascript
async function restoreConversation(sessionId) {
  try {
    const response = await fetch(`/api/conversation/${sessionId}`);
    
    if (response.status === 404) {
      // No conversation found - this is normal for new sessions
      console.log('No previous conversation found');
      return;
    }
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    // ... restore messages
    
  } catch (error) {
    console.error('Failed to restore conversation:', error);
    // Don't block the user - just start fresh
  }
}
```

## Performance Tips

1. **Lazy Loading**: Only load conversation history when needed
2. **Pagination**: Use the `limit` parameter to load recent messages first
3. **Caching**: Cache the conversation data to avoid repeated API calls
4. **Debouncing**: Debounce visualization rendering if there are many charts

## Complete Flow

```
User Opens App
    ↓
Check localStorage for sessionId
    ↓
If sessionId exists → Fetch /api/conversation/{sessionId}
    ↓
Restore messages + visualizations to UI
    ↓
User continues chatting with same session
    ↓
On refresh → Repeat process
```
