# Backend Integration Guide

This directory contains the frontend service layer that integrates with your Python backend running the multi-agent LangGraph system.

## Architecture

```
Frontend (React/TypeScript) <--> Backend (Python/FastAPI) <--> PostgreSQL Database
                                        |
                                        ├── LangGraph Agents
                                        ├── LlamaIndex RAG
                                        └── LLM Providers (OpenRouter/Cerebras/Groq)
```

## API Service (`api.ts`)

Handles communication with the Python FastAPI backend that orchestrates the multi-agent system.

### Key Functions:

- `processQuery()` - Streams query results from the agent pipeline
- `checkAPIHealth()` - Monitors backend availability
- `getDatabaseStatus()` - Checks PostgreSQL connection status
- `getLLMProviderStatus()` - Reports active LLM provider

### Integration with Python Backend

Your Python backend should expose these endpoints:

```python
# FastAPI endpoints needed

@app.post("/api/query")
async def process_query(request: QueryRequest):
    """
    Processes a query through the LangGraph agent pipeline
    Returns streaming SSE (Server-Sent Events) for real-time updates
    """
    pass

@app.get("/health")
async def health_check():
    """Check API health"""
    pass

@app.get("/api/database/status")
async def database_status():
    """Check PostgreSQL connection"""
    pass

@app.get("/api/llm/status")
async def llm_status():
    """Report active LLM provider"""
    pass
```

## Database Service (`database.ts`)

Provides schema information and query execution interfaces.

### Key Functions:

- `getDatabaseSchema()` - Fetches table and column metadata
- `executeQuery()` - Executes SQL queries securely
- `getTableStats()` - Retrieves table statistics

## Environment Variables

The frontend expects these variables (create a `.env.local` file):

```bash
VITE_API_URL=http://localhost:8000
```

The Python backend should use these from your `.env`:

```bash
DB_HOST=34.232.69.47
DB_PORT=5432
DB_NAME=Prescience_Dev
DB_USER=postgres
DB_PASSWORD=SecureP@ss123

OPENROUTER_API_KEY=sk-or-v1-...
CEREBRAS_API_KEY=csk-...
GROQ_API_KEY=gsk_...
```

## Backend Implementation Example

Here's how your Python backend should handle queries:

```python
from fastapi import FastAPI
from langraph.graph import StateGraph
from sse_starlette.sse import EventSourceResponse
import asyncio

app = FastAPI()

@app.post("/api/query")
async def process_query(request: QueryRequest):
    async def event_generator():
        # Initialize LangGraph workflow
        workflow = create_agent_workflow()
        
        # Stream updates from each agent
        async for state in workflow.astream({"query": request.query}):
            # Send stage updates
            yield {
                "event": "stage_update",
                "data": json.dumps({
                    "stage": state["current_agent"],
                    "status": state["status"]
                })
            }
            
            # Send final result
            if state.get("complete"):
                yield {
                    "event": "result",
                    "data": json.dumps(state["result"])
                }
    
    return EventSourceResponse(event_generator())
```

## Running the Full Stack

1. **Start Python Backend:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend:**
   ```bash
   npm run dev
   ```

3. **Connect:**
   - Frontend will automatically connect to `http://localhost:8000`
   - Check System Metrics tab to verify connection status

## Mock vs Production Mode

Currently, the frontend runs in **mock mode** with simulated data. To enable production mode:

1. Implement the FastAPI endpoints as shown above
2. Set `VITE_API_URL` environment variable
3. The frontend will automatically detect and use the real backend

## Security Notes

- Never commit API keys or database passwords
- Use environment variables for all sensitive data
- Implement proper CORS policies in FastAPI
- Use parameterized queries to prevent SQL injection
- Implement rate limiting on backend endpoints
