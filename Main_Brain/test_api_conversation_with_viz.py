"""
End-to-end test for conversation history with visualizations via API
"""

import asyncio
import httpx
import uuid

async def test_api_conversation_flow():
    """Test the full API flow: query -> store -> retrieve with visualizations"""
    
    base_url = "http://localhost:8000"
    session_id = str(uuid.uuid4())
    
    print(f"Testing with session_id: {session_id}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Send a query that should generate visualizations
        print("Step 1: Sending query...")
        query_request = {
            "query": "Show me total capacity by state",
            "session_id": session_id,
            "user_id": "test_user"
        }
        
        response = await client.post(f"{base_url}/api/query", json=query_request)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query processed successfully")
            print(f"   - Content length: {len(data.get('content', ''))}")
            print(f"   - Visualizations: {len(data.get('visualizations', []))}")
            print(f"   - Confidence: {data.get('confidence')}")
            
            if data.get('visualizations'):
                print(f"\n   Visualization details:")
                for i, viz in enumerate(data['visualizations']):
                    print(f"     [{i+1}] Type: {viz.get('type')}")
                    print(f"         Data keys: {list(viz.get('data', {}).keys())}")
        else:
            print(f"❌ Query failed: {response.text}")
            return
        
        # Step 2: Retrieve conversation history
        print(f"\nStep 2: Retrieving conversation history...")
        response = await client.get(f"{base_url}/api/conversation/{session_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversation retrieved successfully")
            print(f"   - Turn count: {data.get('turn_count')}")
            print(f"   - Turns: {len(data.get('turns', []))}")
            
            if data.get('turns'):
                for i, turn in enumerate(data['turns']):
                    print(f"\n   Turn {i+1}:")
                    print(f"     - Query: {turn.get('user_query')[:50]}...")
                    print(f"     - Response length: {len(turn.get('agent_response', ''))}")
                    print(f"     - Visualizations: {len(turn.get('visualizations', []))}")
                    
                    if turn.get('visualizations'):
                        print(f"     - Visualization types: {[v.get('type') for v in turn['visualizations']]}")
                        print(f"\n✅ SUCCESS: Visualizations are present in conversation history!")
                    else:
                        print(f"\n❌ FAILED: No visualizations in conversation history!")
            else:
                print(f"\n❌ FAILED: No turns in conversation history!")
        else:
            print(f"❌ Failed to retrieve conversation: {response.text}")
            return
        
        # Step 3: Clean up
        print(f"\nStep 3: Cleaning up...")
        response = await client.delete(f"{base_url}/api/conversation/{session_id}")
        if response.status_code == 200:
            print(f"✅ Conversation cleared successfully")
        else:
            print(f"⚠️  Failed to clear conversation: {response.text}")

if __name__ == "__main__":
    print("=" * 70)
    print("API Conversation with Visualizations Test")
    print("=" * 70)
    print("\nMake sure the server is running on http://localhost:8000\n")
    
    try:
        asyncio.run(test_api_conversation_flow())
    except httpx.ConnectError:
        print("\n❌ ERROR: Could not connect to server at http://localhost:8000")
        print("   Please start the server with: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
