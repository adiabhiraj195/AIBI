"""
Integration test for conversation memory with base agent system
"""

import asyncio
from agents.memory import conversation_memory
from agents.base import BaseAgent, AgentResponse, QueryContext

class TestInsightsAgent(BaseAgent):
    """Test agent for memory integration"""
    
    async def _initialize_impl(self):
        """Initialize test agent"""
        pass
    
    async def _process_impl(self, context: QueryContext) -> AgentResponse:
        """Process query with memory context"""
        # Use conversation history for context-aware responses
        if context.conversation_history:
            previous_queries = [msg.get('query', '') for msg in context.conversation_history[-3:]]
            context_info = f"Based on our previous discussion about {', '.join(previous_queries[:2])}, "
        else:
            context_info = ""
        
        return AgentResponse(
            agent_name=self.name,
            content=f"{context_info}Here's the financial analysis for your query: {context.query}",
            confidence=0.9,
            execution_time=1.0
        )
    
    def _calculate_confidence(self, query: str, context: QueryContext = None) -> float:
        """Calculate confidence for handling query"""
        financial_keywords = ["revenue", "profit", "cost", "margin", "financial"]
        return 0.8 if any(keyword in query.lower() for keyword in financial_keywords) else 0.3

async def test_memory_integration():
    """Test conversation memory integration with agents"""
    print("🧪 Testing Memory Integration with Agents...")
    
    # Initialize systems
    await conversation_memory.initialize()
    
    # Create test agent
    agent = TestInsightsAgent("test_insights")
    await agent.initialize()
    
    session_id = "integration_test_session"
    user_id = "integration_test_user"
    
    try:
        # First query - no context
        query1 = "What is the revenue forecast for Q3?"
        context1 = QueryContext(
            query=query1,
            session_id=session_id,
            user_id=user_id,
            conversation_history=[]
        )
        
        response1 = await agent.process(context1)
        print(f"✅ First response: {response1.content[:100]}...")
        
        # Store in memory
        await conversation_memory.store_interaction(query1, response1, session_id, user_id)
        
        # Second query - with context
        query2 = "What about the profit margins?"
        
        # Get conversation context
        conv_context = await conversation_memory.get_context(session_id)
        conversation_history = []
        for turn in conv_context.turns:
            conversation_history.append({
                'query': turn.user_query,
                'response': turn.agent_response.content
            })
        
        context2 = QueryContext(
            query=query2,
            session_id=session_id,
            user_id=user_id,
            conversation_history=conversation_history
        )
        
        response2 = await agent.process(context2)
        print(f"✅ Second response (with context): {response2.content[:100]}...")
        
        # Store second interaction
        await conversation_memory.store_interaction(query2, response2, session_id, user_id)
        
        # Verify context is maintained
        final_context = await conversation_memory.get_context(session_id)
        print(f"✅ Final context has {len(final_context.turns)} turns")
        print(f"   Current topic: {final_context.current_topic}")
        
        # Test that second response includes context from first
        assert "previous discussion" in response2.content or "Based on" in response2.content
        print("✅ Context-aware response confirmed")
        
        # Cleanup
        await conversation_memory.clear_session(session_id)
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        raise
    finally:
        await agent.cleanup()
        await conversation_memory.cleanup()
        print("✅ Integration test cleanup completed")

if __name__ == "__main__":
    asyncio.run(test_memory_integration())