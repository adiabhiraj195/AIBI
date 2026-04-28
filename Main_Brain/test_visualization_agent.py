"""
Test script for Visualization Agent
Tests the agent's ability to generate charts from raw data
"""

import asyncio
import json
from agents.visualization import visualization_agent
from agents.base import QueryContext


async def test_visualization_agent():
    """Test visualization agent with sample data"""
    
    # Initialize agent
    await visualization_agent.initialize()
    
    # Sample data similar to what NL2SQL agent would return
    sample_data = [
        {"customer_name": "Customer A", "state": "State 1", "capacity": 150.5, "wtg_count": 50},
        {"customer_name": "Customer B", "state": "State 2", "capacity": 200.3, "wtg_count": 65},
        {"customer_name": "Customer C", "state": "State 1", "capacity": 180.7, "wtg_count": 58},
        {"customer_name": "Customer D", "state": "State 3", "capacity": 220.1, "wtg_count": 72},
        {"customer_name": "Customer E", "state": "State 2", "capacity": 190.4, "wtg_count": 61},
        {"customer_name": "Customer F", "state": "State 1", "capacity": 165.8, "wtg_count": 54},
        {"customer_name": "Customer G", "state": "State 3", "capacity": 210.2, "wtg_count": 68},
        {"customer_name": "Customer H", "state": "State 2", "capacity": 175.6, "wtg_count": 56},
    ]
    
    # Create query context
    context = QueryContext(
        query="Show me capacity by customer",
        session_id="test_session",
        user_id="test_user",
        metadata={
            "processed_data": sample_data,
            "handler": "nl2sql_agent"
        }
    )
    
    # Process with visualization agent
    print("🎨 Testing Visualization Agent...")
    print("=" * 60)
    
    response = await visualization_agent.process(context)
    
    print(f"\n✅ Agent: {response.agent_name}")
    print(f"✅ Confidence: {response.confidence}")
    print(f"✅ Execution Time: {response.execution_time:.2f}s")
    print(f"\n📊 Content:\n{response.content}")
    print(f"\n📈 Generated {len(response.visualizations)} visualizations:")
    
    for i, viz in enumerate(response.visualizations, 1):
        print(f"\n  {i}. Type: {viz.get('type')}")
        title = viz.get('layout', {}).get('title', {})
        if isinstance(title, dict):
            title = title.get('text', 'Untitled')
        print(f"     Title: {title}")
        print(f"     Data traces: {len(viz.get('data', {}).get('traces', []))}")
        print(f"     Layout keys: {list(viz.get('layout', {}).keys())[:5]}")
    
    # Save visualizations to file for inspection
    with open('test_visualizations.json', 'w') as f:
        json.dump(response.visualizations, f, indent=2)
    
    print(f"\n💾 Visualizations saved to test_visualizations.json")
    print("=" * 60)
    
    return response


async def test_with_aggregated_data():
    """Test with aggregated data (like from statistical handler)"""
    
    print("\n\n🎨 Testing with Aggregated Data...")
    print("=" * 60)
    
    # Sample aggregated data
    aggregated_data = [
        {"state": "State 1", "total_capacity": 496.0, "project_count": 15},
        {"state": "State 2", "total_capacity": 566.3, "project_count": 18},
        {"state": "State 3", "total_capacity": 430.3, "project_count": 12},
        {"state": "State 4", "total_capacity": 380.5, "project_count": 10},
    ]
    
    context = QueryContext(
        query="Show me total capacity by state",
        session_id="test_session_2",
        user_id="test_user",
        metadata={
            "processed_data": aggregated_data,
            "handler": "statistical_handler"
        }
    )
    
    response = await visualization_agent.process(context)
    
    print(f"\n✅ Generated {len(response.visualizations)} visualizations")
    print(f"📊 Content:\n{response.content}")
    
    for i, viz in enumerate(response.visualizations, 1):
        chart_type = viz.get('type', 'unknown').upper()
        title = viz.get('layout', {}).get('title', {})
        if isinstance(title, dict):
            title = title.get('text', 'Untitled')
        print(f"\n  {i}. {chart_type}: {title}")
    
    print("=" * 60)
    
    return response


async def test_with_no_data():
    """Test with empty data"""
    
    print("\n\n🎨 Testing with No Data...")
    print("=" * 60)
    
    context = QueryContext(
        query="Show me something",
        session_id="test_session_3",
        user_id="test_user",
        metadata={
            "processed_data": [],
            "handler": "nl2sql_agent"
        }
    )
    
    response = await visualization_agent.process(context)
    
    print(f"\n✅ Confidence: {response.confidence}")
    print(f"📊 Content: {response.content}")
    print(f"📈 Visualizations: {len(response.visualizations)}")
    print("=" * 60)
    
    return response


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 VISUALIZATION AGENT TEST SUITE")
    print("=" * 60)
    
    asyncio.run(test_visualization_agent())
    asyncio.run(test_with_aggregated_data())
    asyncio.run(test_with_no_data())
    
    print("\n✅ All tests completed!")
