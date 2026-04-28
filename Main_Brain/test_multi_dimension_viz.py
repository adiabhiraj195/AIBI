"""
Test visualization agent with multi-dimensional data
"""
import asyncio
import json
from agents.visualization import VisualizationAgent
from agents.base import QueryContext

# Your actual data
test_data = [
    {"formatted_period": "Total", "project_phase": "Erection Plan", "avg_mwg_deviation": 2.6826086957},
    {"formatted_period": "Dec-25", "project_phase": "PE Plan", "avg_mwg_deviation": 1.2402173913},
    {"formatted_period": "May-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.6760869565},
    {"formatted_period": "Feb-26", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.633423913},
    {"formatted_period": "Oct-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.6059782609},
    {"formatted_period": "Jan-26", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.5706521739},
    {"formatted_period": "Nov-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.5686594203},
    {"formatted_period": "Mar-26", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.5519021739},
    {"formatted_period": "Jul-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.514673913},
    {"formatted_period": "Dec-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.4544384058},
    {"formatted_period": "Jun-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.4385869565},
    {"formatted_period": "Apr-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.2519927536},
    {"formatted_period": "Aug-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0.1439311594},
    {"formatted_period": "Feb-26", "project_phase": "PE Plan", "avg_mwg_deviation": 0.1255434783},
    {"formatted_period": "May-25", "project_phase": "PE Plan", "avg_mwg_deviation": 0.0076086957},
    {"formatted_period": "Jan-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "O/S", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Feb-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Jul-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Sep-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Jan-25", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Jun-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "May-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Dec-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Feb-25", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Oct-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Dec-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Nov-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Jun-25", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Mar-25", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Oct-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Aug-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Mar-25", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "May-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Jun-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Nov-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Jul-25", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Oct-25", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Sep-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Apr-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Aug-25", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Apr-24", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Aug-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Jul-24", "project_phase": "PE Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "O/S", "project_phase": "Erection Plan", "avg_mwg_deviation": 0},
    {"formatted_period": "Mar-26", "project_phase": "PE Plan", "avg_mwg_deviation": -0.0076086957},
    {"formatted_period": "Sep-25", "project_phase": "PE Plan", "avg_mwg_deviation": -0.0152173913},
    {"formatted_period": "Sep-25", "project_phase": "Erection Plan", "avg_mwg_deviation": -0.0451086957},
    {"formatted_period": "Jan-26", "project_phase": "PE Plan", "avg_mwg_deviation": -0.1902173913},
    {"formatted_period": "Total", "project_phase": "PE Plan", "avg_mwg_deviation": -0.6137681159},
    {"formatted_period": "Apr-25", "project_phase": "PE Plan", "avg_mwg_deviation": -0.6269927536},
    {"formatted_period": "Nov-25", "project_phase": "PE Plan", "avg_mwg_deviation": -1.7608695652}
]

async def test_multi_dimension():
    """Test visualization with multi-dimensional data"""
    print("Testing visualization agent with multi-dimensional data...")
    print(f"Data has {len(test_data)} rows")
    
    # Initialize agent
    agent = VisualizationAgent()
    await agent.initialize()
    
    # Create context
    context = QueryContext(
        query="Show me average MWG deviation by period and project phase",
        session_id="test_session",
        metadata={
            'processed_data': test_data,
            'handler': 'test'
        }
    )
    
    # Process
    response = await agent.process(context)
    
    print(f"\nAgent Response:")
    print(f"Confidence: {response.confidence}")
    print(f"Number of visualizations: {len(response.visualizations)}")
    
    for i, viz in enumerate(response.visualizations, 1):
        print(f"\nVisualization {i}:")
        print(f"  Type: {viz.get('type')}")
        print(f"  Number of traces: {len(viz.get('data', {}).get('traces', []))}")
        
        # Show trace details
        for j, trace in enumerate(viz.get('data', {}).get('traces', []), 1):
            print(f"  Trace {j}:")
            print(f"    Name: {trace.get('name', 'N/A')}")
            print(f"    Type: {trace.get('type', 'N/A')}")
            if 'x' in trace:
                print(f"    X data points: {len(trace['x'])}")
            if 'y' in trace:
                print(f"    Y data points: {len(trace['y'])}")
        
        # Show layout title
        layout = viz.get('layout', {})
        if 'title' in layout:
            title_text = layout['title'].get('text') if isinstance(layout['title'], dict) else layout['title']
            print(f"  Title: {title_text}")
    
    # Save visualizations to file for inspection
    with open('test_multi_dimension_output.json', 'w') as f:
        json.dump(response.visualizations, f, indent=2)
    
    print("\n✅ Visualizations saved to test_multi_dimension_output.json")

if __name__ == "__main__":
    asyncio.run(test_multi_dimension())
