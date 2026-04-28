# Visualization Persistence Fix

## Problem
When users refreshed the frontend and returned to the chat, visualizations would disappear while insights remained. This was because visualizations were not being properly stored and retrieved with conversation history.

## Root Cause
The issue had two parts:

1. **Model Issue**: The `ConversationTurnResponse` model only included `agent_response: str` (just the text content) but didn't include a `visualizations` field.

2. **Serialization Issue**: When storing `AgentResponse` objects in Redis, the Pydantic `PlotlyChart` models in the `visualizations` list were being converted to string representations instead of proper dictionaries.

## Solution

### 1. Updated ConversationTurnResponse Model
Added `visualizations` field to the model in `models.py`:

```python
class ConversationTurnResponse(BaseModel):
    """Response for a single conversation turn"""
    turn_id: str
    timestamp: datetime
    user_query: str
    agent_response: str
    visualizations: List[PlotlyChart] = Field(default_factory=list)  # ← Added
    session_id: str
    user_id: Optional[str] = None
```

### 2. Fixed Visualization Serialization
Updated `ConversationTurn.to_dict()` in `agents/memory.py` to properly serialize Pydantic models:

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary for storage"""
    agent_response_dict = asdict(self.agent_response)
    
    # Properly serialize visualizations (they might be Pydantic models)
    if self.agent_response.visualizations:
        serialized_viz = []
        for viz in self.agent_response.visualizations:
            if hasattr(viz, 'model_dump'):  # Pydantic v2
                serialized_viz.append(viz.model_dump())
            elif hasattr(viz, 'dict'):  # Pydantic v1
                serialized_viz.append(viz.dict())
            elif isinstance(viz, dict):
                serialized_viz.append(viz)
            else:
                serialized_viz.append(dict(viz) if hasattr(viz, '__dict__') else viz)
        agent_response_dict['visualizations'] = serialized_viz
    
    return {
        "turn_id": self.turn_id,
        "timestamp": self.timestamp.isoformat(),
        "user_query": self.user_query,
        "agent_response": agent_response_dict,
        "session_id": self.session_id,
        "user_id": self.user_id
    }
```

### 3. Updated API Endpoint
Modified the `/api/conversation/{session_id}` endpoint in `main.py` to convert visualization dictionaries back to PlotlyChart objects:

```python
@app.get("/api/conversation/{session_id}", response_model=ConversationContextResponse)
async def get_conversation(session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    context = await conversation_memory.get_context(session_id, lookback=limit)
    
    turns = []
    for turn in context.turns:
        # Convert visualization dicts to PlotlyChart objects
        visualizations = []
        if turn.agent_response.visualizations:
            from models import PlotlyChart
            for viz_data in turn.agent_response.visualizations:
                if isinstance(viz_data, dict):
                    visualizations.append(PlotlyChart(**viz_data))
                else:
                    visualizations.append(viz_data)
        
        turns.append(ConversationTurnResponse(
            turn_id=turn.turn_id,
            timestamp=turn.timestamp,
            user_query=turn.user_query,
            agent_response=turn.agent_response.content,
            visualizations=visualizations,  # ← Now included
            session_id=turn.session_id,
            user_id=turn.user_id
        ))
    
    return ConversationContextResponse(...)
```

## Testing

### Unit Test
Run `test_conversation_visualizations.py` to verify visualizations are stored and retrieved correctly:

```bash
python test_conversation_visualizations.py
```

Expected output:
```
✅ Stored turn: <turn_id>
✅ Retrieved 1 turns
Visualization details:
  - Type: bar
  - Data keys: ['x', 'y', 'type']
  - Layout title: Test Chart
✅ SUCCESS: Visualizations are stored and retrieved correctly!
```

### API Integration Test
Run `test_api_conversation_with_viz.py` to test the full API flow:

```bash
# Start the server first
python main.py

# In another terminal
python test_api_conversation_with_viz.py
```

Expected output:
```
✅ Query processed successfully
   - Visualizations: 2
✅ Conversation retrieved successfully
   - Visualizations: 2
✅ SUCCESS: Visualizations are present in conversation history!
```

## Frontend Integration

The frontend should now receive visualizations when fetching conversation history:

```javascript
// Fetch conversation history
const response = await fetch(`/api/conversation/${sessionId}`);
const data = await response.json();

// Each turn now includes visualizations
data.turns.forEach(turn => {
  console.log('Query:', turn.user_query);
  console.log('Response:', turn.agent_response);
  console.log('Visualizations:', turn.visualizations); // ← Now available!
  
  // Render visualizations
  turn.visualizations.forEach(viz => {
    Plotly.newPlot(container, viz.data, viz.layout, viz.config);
  });
});
```

## Files Modified

1. `models.py` - Added `visualizations` field to `ConversationTurnResponse`
2. `agents/memory.py` - Fixed visualization serialization in `ConversationTurn.to_dict()`
3. `main.py` - Updated `/api/conversation/{session_id}` endpoint to include visualizations

## Impact

- ✅ Visualizations now persist across page refreshes
- ✅ Full conversation history (text + visualizations) is maintained
- ✅ No breaking changes to existing API contracts
- ✅ Backward compatible (empty list if no visualizations)

## Next Steps

The frontend should be updated to:
1. Fetch conversation history on page load/refresh
2. Render both text responses and visualizations from history
3. Maintain the same UI state as before the refresh
