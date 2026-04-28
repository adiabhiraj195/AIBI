"""
Test suite for Conversation Memory System
Tests Redis integration, session management, and context retrieval
"""

import asyncio
import pytest
import uuid
from datetime import datetime
from agents.memory import ConversationMemory, ConversationTurn, ConversationContext
from agents.base import AgentResponse
from config import settings

# Test configuration
TEST_SESSION_ID = "test_session_123"
TEST_USER_ID = "test_user_456"

async def test_conversation_memory_basic():
    """Test basic conversation memory functionality"""
    print("🧪 Testing Conversation Memory System...")
    
    # Initialize memory system
    memory = ConversationMemory()
    
    try:
        await memory.initialize()
        print("✅ Memory system initialized")
        
        # Test storing interactions
        query1 = "What is the total capacity by state?"
        response1 = AgentResponse(
            agent_name="insights",
            content="The total capacity varies by state. Maharashtra leads with 2,500 MW, followed by Gujarat with 1,800 MW.",
            confidence=0.95,
            execution_time=1.2
        )
        
        turn_id1 = await memory.store_interaction(query1, response1, TEST_SESSION_ID, TEST_USER_ID)
        print(f"✅ Stored first interaction: {turn_id1}")
        
        # Store second interaction
        query2 = "Show me a chart of capacity by business module"
        response2 = AgentResponse(
            agent_name="visualization",
            content="Here's a bar chart showing capacity distribution across business modules.",
            visualizations=[{"type": "bar", "data": {"x": ["Module A", "Module B"], "y": [1000, 1500]}}],
            confidence=0.88,
            execution_time=2.1
        )
        
        turn_id2 = await memory.store_interaction(query2, response2, TEST_SESSION_ID, TEST_USER_ID)
        print(f"✅ Stored second interaction: {turn_id2}")
        
        # Test context retrieval
        context = await memory.get_context(TEST_SESSION_ID)
        print(f"✅ Retrieved context with {len(context.turns)} turns")
        print(f"   Current topic: {context.current_topic}")
        print(f"   User ID: {context.user_id}")
        
        # Verify context content
        assert len(context.turns) == 2
        assert context.turns[0].user_query == query1
        assert context.turns[1].user_query == query2
        assert context.user_id == TEST_USER_ID
        
        # Test conversation summary
        summary = await memory.summarize_session(TEST_SESSION_ID)
        print(f"✅ Generated session summary:")
        print(f"   Turn count: {summary.turn_count}")
        print(f"   Topics: {summary.topics}")
        print(f"   Key metrics: {summary.key_metrics_discussed}")
        
        # Test memory stats
        stats = await memory.get_memory_stats()
        print(f"✅ Memory stats:")
        print(f"   Redis connected: {stats['redis_connected']}")
        print(f"   Active sessions: {stats['active_sessions']}")
        print(f"   Total turns: {stats['total_turns']}")
        
        # Test session clearing
        success = await memory.clear_session(TEST_SESSION_ID)
        print(f"✅ Session cleared: {success}")
        
        # Verify session is cleared
        empty_context = await memory.get_context(TEST_SESSION_ID)
        assert len(empty_context.turns) == 0
        print("✅ Verified session is empty after clearing")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise
    finally:
        await memory.cleanup()
        print("✅ Memory system cleanup completed")

async def test_conversation_memory_limits():
    """Test conversation memory limits and session management"""
    print("\n🧪 Testing Memory Limits...")
    
    memory = ConversationMemory()
    
    try:
        await memory.initialize()
        
        # Store more interactions than the memory limit
        session_id = f"test_limit_{uuid.uuid4()}"
        memory_limit = settings.agents.conversation_memory_limit
        
        for i in range(memory_limit + 5):  # Store 5 more than limit
            query = f"Test query number {i}"
            response = AgentResponse(
                agent_name="test",
                content=f"Test response {i}",
                confidence=0.9
            )
            await memory.store_interaction(query, response, session_id)
        
        # Check that only memory_limit interactions are kept
        context = await memory.get_context(session_id)
        print(f"✅ Stored {memory_limit + 5} interactions, kept {len(context.turns)}")
        assert len(context.turns) <= memory_limit
        
        # Verify most recent interactions are kept
        assert "Test query number" in context.turns[-1].user_query
        
        # Cleanup
        await memory.clear_session(session_id)
        
    except Exception as e:
        print(f"❌ Memory limits test failed: {str(e)}")
        raise
    finally:
        await memory.cleanup()

async def test_conversation_memory_topic_detection():
    """Test topic detection functionality"""
    print("\n🧪 Testing Topic Detection...")
    
    memory = ConversationMemory()
    
    try:
        await memory.initialize()
        
        session_id = f"test_topic_{uuid.uuid4()}"
        
        # Store financial analysis queries
        financial_queries = [
            "What is the revenue forecast for Q3?",
            "Show me the profit margins by project",
            "Analyze the cost breakdown by state"
        ]
        
        for query in financial_queries:
            response = AgentResponse(
                agent_name="insights",
                content=f"Financial analysis response for: {query}",
                confidence=0.9
            )
            await memory.store_interaction(query, response, session_id)
        
        # Check topic detection
        context = await memory.get_context(session_id)
        print(f"✅ Detected topic: {context.current_topic}")
        
        # Should detect financial_analysis topic
        assert context.current_topic == "financial_analysis"
        
        # Cleanup
        await memory.clear_session(session_id)
        
    except Exception as e:
        print(f"❌ Topic detection test failed: {str(e)}")
        raise
    finally:
        await memory.cleanup()

async def main():
    """Run all conversation memory tests"""
    print("🚀 Starting Conversation Memory Tests\n")
    
    try:
        await test_conversation_memory_basic()
        await test_conversation_memory_limits()
        await test_conversation_memory_topic_detection()
        
        print("\n🎉 All conversation memory tests passed!")
        
    except Exception as e:
        print(f"\n💥 Tests failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)