"""
Example usage of the authentication system.
Run these examples to test the authentication API.
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def example_register():
    """Example: Register a new user"""
    url = f"{BASE_URL}/api/v1/auth/register"
    
    data = {
        "email": "john.doe@example.com",
        "username": "john_doe",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    
    response = requests.post(url, json=data)
    print_response(response, "REGISTER NEW USER")
    
    return response.json() if response.status_code == 200 else None


def example_login():
    """Example: Login user"""
    url = f"{BASE_URL}/api/v1/auth/login"
    
    data = {
        "email": "john.doe@example.com",
        "password": "SecurePassword123"
    }
    
    response = requests.post(url, json=data)
    print_response(response, "LOGIN USER")
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def example_get_current_user(token):
    """Example: Get current user info"""
    url = f"{BASE_URL}/api/v1/auth/me"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "GET CURRENT USER")
    
    return response.json() if response.status_code == 200 else None


def example_change_password(token):
    """Example: Change password"""
    url = f"{BASE_URL}/api/v1/auth/change-password"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "current_password": "SecurePassword123",
        "new_password": "NewSecurePassword456",
        "confirm_password": "NewSecurePassword456"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print_response(response, "CHANGE PASSWORD")
    
    return response.status_code == 200


def example_verify_token(token):
    """Example: Verify token"""
    url = f"{BASE_URL}/api/v1/auth/verify-token"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(url, headers=headers)
    print_response(response, "VERIFY TOKEN")
    
    return response.json() if response.status_code == 200 else None


def example_logout(token):
    """Example: Logout user"""
    url = f"{BASE_URL}/api/v1/auth/logout"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(url, headers=headers)
    print_response(response, "LOGOUT USER")
    
    return response.status_code == 200


def example_invalid_login():
    """Example: Try login with wrong password"""
    url = f"{BASE_URL}/api/v1/auth/login"
    
    data = {
        "email": "john.doe@example.com",
        "password": "WrongPassword123"
    }
    
    response = requests.post(url, json=data)
    print_response(response, "LOGIN WITH WRONG PASSWORD (ERROR EXAMPLE)")
    
    return response


def example_duplicate_email():
    """Example: Try to register with existing email"""
    url = f"{BASE_URL}/api/v1/auth/register"
    
    data = {
        "email": "john.doe@example.com",
        "username": "another_user",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    
    response = requests.post(url, json=data)
    print_response(response, "REGISTER WITH DUPLICATE EMAIL (ERROR EXAMPLE)")
    
    return response


def example_invalid_token():
    """Example: Try to access protected route with invalid token"""
    url = f"{BASE_URL}/api/v1/auth/me"
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "ACCESS WITH INVALID TOKEN (ERROR EXAMPLE)")
    
    return response


def run_full_flow():
    """Run complete authentication flow"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "AUTHENTICATION SYSTEM - FULL FLOW EXAMPLE" + " "*7 + "║")
    print("╚" + "="*58 + "╝")
    
    # Step 1: Register
    print("\n[1/6] Registering new user...")
    register_result = example_register()
    if not register_result:
        print("Registration failed. Check if user already exists.")
    
    # Step 2: Login
    print("\n[2/6] Logging in...")
    token = example_login()
    if not token:
        print("Login failed!")
        return
    
    # Step 3: Get current user
    print("\n[3/6] Getting current user info...")
    user = example_get_current_user(token)
    
    # Step 4: Verify token
    print("\n[4/6] Verifying token...")
    verify = example_verify_token(token)
    
    # Step 5: Logout
    print("\n[5/6] Logging out...")
    logout = example_logout(token)
    
    # Step 6: Try invalid operations
    print("\n[6/6] Testing error cases...")
    print("\n--- Error Test 1: Invalid Login ---")
    example_invalid_login()
    
    print("\n--- Error Test 2: Invalid Token ---")
    example_invalid_token()
    
    print("\n--- Error Test 3: Duplicate Email ---")
    example_duplicate_email()
    
    # Summary
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*20 + "FLOW COMPLETED" + " "*24 + "║")
    print("╚" + "="*58 + "╝")
    print("\nTest Results:")
    print(f"  ✅ Register: {'Success' if register_result else 'Failed'}")
    print(f"  ✅ Login: {'Success' if token else 'Failed'}")
    print(f"  ✅ Get User: {'Success' if user else 'Failed'}")
    print(f"  ✅ Verify Token: {'Success' if verify else 'Failed'}")
    print(f"  ✅ Logout: {'Success' if logout else 'Failed'}")
    print(f"  ✅ Error Handling: Tested\n")


# Example of protecting a route
example_protected_endpoint_code = """
# Example: Using authentication in your own endpoints

from fastapi import APIRouter, Depends
from app.controllers.auth_controller import get_current_user
from app.models.user import UserResponse

router = APIRouter()

@router.post("/api/v1/upload-csv")
async def upload_csv(
    file: UploadFile,
    current_user: UserResponse = Depends(get_current_user)
):
    \"\"\"
    Upload CSV file - Protected endpoint.
    User must be authenticated (token required).
    \"\"\"
    # Access current user information
    user_id = current_user.id
    user_email = current_user.email
    user_name = current_user.username
    
    # Process file for this user
    # Save file with user_id association
    # ...
    
    return {
        "message": f"File uploaded by {user_name}",
        "user_id": user_id,
        "file_size": file.size
    }
"""


if __name__ == "__main__":
    print("\n")
    print("Authentication System - Examples")
    print("=" * 60)
    print("\nMake sure your API is running: python main.py")
    print("Database must be accessible at localhost:5432")
    print("\nRunning full authentication flow test...")
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ API is running!")
            run_full_flow()
        else:
            print("❌ API is not responding properly")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at http://localhost:8000")
        print("   Make sure the API is running: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Show example code
    print("\n\nExample: How to protect your own endpoints")
    print("=" * 60)
    print(example_protected_endpoint_code)
