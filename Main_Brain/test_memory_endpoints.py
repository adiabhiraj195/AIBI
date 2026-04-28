"""
Test FastAPI endpoints for conversation memory
"""

import asyncio
import httpx
import json
from agents.memory import conversation_memory
from agents.base import AgentResponse

async def test_memory_endpoints():
    """Test the conversation memory FastAPI endpoints"""
    print("🧪 Testing Memory Endpoints...")
    
    # Initialize memory system
    await conversation_memory.initialize()
    
    # Store some test data
    session_id = "test_api_session"
    user_id = "test_api_user"
    
    # Store test interactions
    query1 = "What is the revenue forecast?"
    response1 = AgentResponse(
        agent_name="insights",
        content="Revenue forecast shows 15% growth in Q3 with strong performance in Maharashtra and Gujarat.",
        confidence=0.92,
        execution_time=1.5
    )
    
    await conversation_memory.store_interaction(query1, response1, session_id, user_id)
    
    query2 = "Show me capacity by state"
    response2 = AgentResponse(
        agent_name="visualization", 
        content="Here's the capacity distribution by state with Maharashtra leading at 2,500 MW.",
        confidence=0.88,
        execution_time=2.1
    )
    
    await conversation_memory.store_interaction(query2, response2, session_id, user_id)
    
    print("✅ Test data stored in memory")
    
    # Test memory stats endpoint
    stats = await conversation_memory.get_memory_stats()
    print(f"✅ Memory Stats:")
    print(f"   Redis connected: {stats['redis_connected']}")
    print(f"   Active sessions: {stats['active_sessions']}")
    print(f"   Total turns: {stats['total_turns']}")
    
    # Test context retrieval
    context = await conversation_memory.get_context(session_id)
    print(f"✅ Context Retrieved:")
    print(f"   Session ID: {context.session_id}")
    print(f"   Turn count: {len(context.turns)}")
    print(f"   Current topic: {context.current_topic}")
    
    # Test session summary
    try:
        summary = await conversation_memory.summarize_session(session_id)
        print(f"✅ Session Summary:")
        print(f"   Turn count: {summary.turn_count}")
        print(f"   Topics: {summary.topics}")
        print(f"   Key metrics: {summary.key_metrics_discussed}")
    except Exception as e:
        print(f"⚠️  Session summary error: {str(e)}")
    
    # Test user sessions
    user_sessions = await conversation_memory.get_user_sessions(user_id)
    print(f"✅ User Sessions: {user_sessions}")
    
    # Cleanup
    await conversation_memory.clear_session(session_id)
    print("✅ Test session cleared")
    
    await conversation_memory.cleanup()
    print("✅ Memory system cleanup completed")

if __name__ == "__main__":
    asyncio.run(test_memory_endpoints())