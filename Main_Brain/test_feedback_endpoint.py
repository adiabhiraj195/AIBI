"""
Test script for feedback endpoint
"""
import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_feedback_endpoint():
    """Test the feedback submission endpoint"""
    
    # Test data
    feedback_data = {
        "query": "What is the total capacity of wind turbines in Maharashtra?",
        "response": "The total capacity of wind turbines in Maharashtra is 450 MW across 180 turbines.",
        "feedback": "thumbs_up",
        "session_id": "test-session-123",
        "user_id": "test-user-456"
    }
    
    print("Testing feedback endpoint...")
    print(f"Sending feedback: {feedback_data['feedback']}")
    
    try:
        # Submit feedback
        response = requests.post(
            f"{BASE_URL}/api/feedback",
            json=feedback_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Feedback submitted successfully!")
        else:
            print(f"\n❌ Failed to submit feedback: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Make sure the server is running on port 8000.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_thumbs_down():
    """Test thumbs down feedback"""
    
    feedback_data = {
        "query": "Show me revenue trends",
        "response": "I don't have revenue data available.",
        "feedback": "thumbs_down"
    }
    
    print("\n\nTesting thumbs down feedback...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/feedback",
            json=feedback_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Thumbs down feedback submitted successfully!")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    test_feedback_endpoint()
    test_thumbs_down()
