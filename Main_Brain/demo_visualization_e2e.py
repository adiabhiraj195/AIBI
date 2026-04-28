"""
End-to-End Demo: Visualization Agent Integration
Demonstrates the complete flow from query to visualizations
"""

import asyncio
import json
from agents.orchestrator import orchestrator_agent
from agents.base import QueryContext


async def demo_visualization_pipeline():
    """
    Complete demonstration of the visualization pipeline:
    Query -> NL2SQL -> Insights -> Visualizations
    """
    
    print("\n" + "=" * 80)
    print("🎨 VISUALIZATION AGENT - END-TO-END DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo shows how the Visualization Agent automatically generates")
    print("3 charts from raw data retrieved by the NL2SQL agent.\n")
    
    # Initialize orchestrator (initializes all sub-agents)
    print("🔧 Initializing agents...")
    await orchestrator_agent.initialize()
    print("✅ All agents initialized\n")
    
    # Demo query
    query = "Show me the top 10 customers by total capacity"
    
    print("=" * 80)
    print(f"📝 User Query: {query}")
    print("=" * 80)
    
    # Create context
    context = QueryContext(
        query=query,
        session_id="demo_session",
        user_id="demo_user"
    )
    
    # Process query
    print("\n⚙️  Processing pipeline:")
    print("   1️⃣  Orchestrator routes to NL2SQL Agent")
    print("   2️⃣  NL2SQL generates and executes SQL query")
    print("   3️⃣  Insights Agent creates CFO-grade summary")
    print("   4️⃣  Visualization Agent generates 3 charts")
    print("   5️⃣  Response combines insights + visualizations\n")
    
    response = await orchestrator_agent.process(context)
    
    # Display results
    print("=" * 80)
    print("📊 RESULTS")
    print("=" * 80)
    
    print(f"\n✅ Confidence: {response.confidence}")
    print(f"✅ Execution Time: {response.execution_time:.2f}s")
    print(f"✅ Handler: {response.metadata.get('handler', 'unknown')}")
    print(f"✅ Insights Generated: {response.metadata.get('insights_generated', False)}")
    print(f"✅ Visualizations Generated: {response.metadata.get('visualizations_generated', False)}")
    
    # Display content
    print("\n" + "-" * 80)
    print("📄 RESPONSE CONTENT")
    print("-" * 80)
    print(response.content)
    print("-" * 80)
    
    # Display visualizations
    if response.visualizations:
        print(f"\n📈 GENERATED VISUALIZATIONS ({len(response.visualizations)} charts)")
        print("-" * 80)
        
        for i, viz in enumerate(response.visualizations, 1):
            chart_type = viz.get('type', 'unknown').upper()
            title = viz.get('title', 'Untitled')
            
            print(f"\n{i}. {chart_type} CHART")
            print(f"   Title: {title}")
            print(f"   Data Structure: {list(viz.get('data', {}).keys())}")
            
            # Show some chart details
            if 'data' in viz and 'data' in viz['data']:
                traces = viz['data']['data']
                if traces:
                    first_trace = traces[0]
                    if 'x' in first_trace and 'y' in first_trace:
                        x_len = len(first_trace['x']) if isinstance(first_trace['x'], list) else 'N/A'
                        y_len = len(first_trace['y']) if isinstance(first_trace['y'], list) else 'N/A'
                        print(f"   Data Points: {x_len} x-values, {y_len} y-values")
        
        print("-" * 80)
        
        # Save visualizations
        filename = "demo_visualizations.json"
        with open(filename, 'w') as f:
            json.dump(response.visualizations, f, indent=2)
        print(f"\n💾 Visualizations saved to: {filename}")
        print("   You can use this JSON with Plotly.js or plotly.py to render the charts")
    else:
        print("\n⚠️  No visualizations were generated")
    
    # Show SQL query if available
    if 'sql_query' in response.metadata:
        print("\n" + "-" * 80)
        print("🔍 SQL QUERY EXECUTED")
        print("-" * 80)
        sql = response.metadata['sql_query']
        print(sql[:500] + "..." if len(sql) > 500 else sql)
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  • Visualization Agent automatically generates 3 relevant charts")
    print("  • Charts are selected based on data characteristics")
    print("  • Output is in Plotly JSON format for frontend rendering")
    print("  • Seamlessly integrated with Insights Agent for complete responses")
    print("  • Total processing time: ~15-20 seconds for complex queries")
    print("\n")


async def show_chart_types_demo():
    """Demonstrate different chart types with various data patterns"""
    
    print("\n" + "=" * 80)
    print("📊 CHART TYPE SELECTION DEMONSTRATION")
    print("=" * 80)
    
    test_cases = [
        {
            "query": "Show capacity by state",
            "expected": "Bar chart (categorical comparison)"
        },
        {
            "query": "Show capacity trends over fiscal years",
            "expected": "Line chart (temporal trend)"
        },
        {
            "query": "What is the distribution of projects by business module?",
            "expected": "Pie chart (composition)"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Query: {test['query']}")
        print(f"   Expected: {test['expected']}")
    
    print("\n" + "=" * 80)
    print("The Visualization Agent intelligently selects chart types based on:")
    print("  • Data dimensions (numeric vs categorical)")
    print("  • Temporal patterns (dates, periods, years)")
    print("  • Cardinality (number of unique values)")
    print("  • Query context (keywords like 'trend', 'distribution', 'compare')")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting Visualization Agent Demo...\n")
    
    # Run chart types demo
    asyncio.run(show_chart_types_demo())
    
    # Run full pipeline demo
    asyncio.run(demo_visualization_pipeline())
    
    print("🎉 Demo completed successfully!\n")
