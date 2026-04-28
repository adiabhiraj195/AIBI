"""
Integration test for Orchestrator with Visualization Agent
Tests the full pipeline: Query -> NL2SQL/Statistical -> Insights -> Visualizations
"""

import asyncio
import json
from agents.orchestrator import orchestrator_agent
from agents.base import QueryContext


async def test_orchestrator_with_visualizations():
    """Test orchestrator with visualization generation"""
    
    # Initialize orchestrator (which initializes all sub-agents)
    await orchestrator_agent.initialize()
    
    print("\n" + "=" * 80)
    print("🚀 ORCHESTRATOR + VISUALIZATION INTEGRATION TEST")
    print("=" * 80)
    
    # Test queries
    test_queries = [
        "Show me total capacity by state",
        "What is the capacity breakdown by business module?",
        "List top 5 customers by capacity"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*80}")
        print(f"📝 Test Query {i}: {query}")
        print('='*80)
        
        # Create context
        context = QueryContext(
            query=query,
            session_id=f"test_session_{i}",
            user_id="test_user"
        )
        
        # Process with orchestrator
        response = await orchestrator_agent.process(context)
        
        print(f"\n✅ Agent: {response.agent_name}")
        print(f"✅ Confidence: {response.confidence}")
        print(f"✅ Execution Time: {response.execution_time:.2f}s")
        print(f"✅ Handler: {response.metadata.get('handler', 'unknown')}")
        
        print(f"\n📊 Response Content:")
        print("-" * 80)
        print(response.content)
        print("-" * 80)
        
        if response.visualizations:
            print(f"\n📈 Generated {len(response.visualizations)} Visualizations:")
            for j, viz in enumerate(response.visualizations, 1):
                print(f"  {j}. {viz.get('type', 'unknown').upper()}: {viz.get('title', 'Untitled')}")
            
            # Save visualizations
            filename = f"test_orchestrator_viz_{i}.json"
            with open(filename, 'w') as f:
                json.dump(response.visualizations, f, indent=2)
            print(f"\n💾 Visualizations saved to {filename}")
        else:
            print("\n⚠️  No visualizations generated")
        
        print(f"\n📋 Metadata:")
        for key, value in response.metadata.items():
            if key not in ['sql_query', 'cfo_response']:  # Skip long values
                print(f"  - {key}: {value}")
    
    print("\n\n" + "=" * 80)
    print("✅ ALL INTEGRATION TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_orchestrator_with_visualizations())
