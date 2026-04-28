#!/usr/bin/env python3
"""
Example usage of the new CSV upload endpoints.
This demonstrates how to use the single and multiple file upload endpoints.
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def upload_single_file_example():
    """Example: Upload a single CSV file"""
    print("Example 1: Uploading a single CSV file")
    print("-" * 40)
    
    # Prepare the file
    csv_content = """id,name,email,age
1,John Doe,john@example.com,25
2,Jane Smith,jane@example.com,30
3,Bob Johnson,bob@example.com,35"""
    
    files = {
        'file': ('example_single.csv', csv_content, 'text/csv')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/upload-single", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['message']}")
            print(f"📄 File: {result['data'][0]['filename']}")
            print(f"📊 Rows: {result['data'][0]['row_count']}, Columns: {result['data'][0]['column_count']}")
            print(f"🔍 Preview: {json.dumps(result['data'][0]['preview'][:2], indent=2)}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()

def upload_multiple_files_example():
    """Example: Upload multiple CSV files"""
    print("Example 2: Uploading multiple CSV files")
    print("-" * 40)
    
    # Prepare multiple files
    csv_content_1 = """product_id,product_name,price
1,Laptop,999.99
2,Mouse,29.99
3,Keyboard,79.99"""
    
    csv_content_2 = """order_id,customer_id,total
101,1,1109.97
102,2,29.99
103,3,79.99"""
    
    files = [
        ('files', ('products.csv', csv_content_1, 'text/csv')),
        ('files', ('orders.csv', csv_content_2, 'text/csv'))
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/upload-multiple", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['message']}")
            
            for i, file_data in enumerate(result['data'], 1):
                print(f"\n📄 File {i}: {file_data['filename']}")
                print(f"📊 Rows: {file_data['row_count']}, Columns: {file_data['column_count']}")
                print(f"🔍 Preview: {json.dumps(file_data['preview'][:1], indent=2)}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()

def deprecated_upload_example():
    """Example: Using the deprecated upload endpoint"""
    print("Example 3: Using deprecated upload endpoint (single file)")
    print("-" * 40)
    
    csv_content = """user_id,username,status
1,alice,active
2,bob,inactive
3,charlie,active"""
    
    files = {
        'files': ('users.csv', csv_content, 'text/csv')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['message']}")
            print("⚠️  Note: This endpoint is deprecated. Consider using /upload-single")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()

def error_handling_example():
    """Example: Error handling scenarios"""
    print("Example 4: Error handling scenarios")
    print("-" * 40)
    
    # Try to upload a single file to the multiple endpoint
    csv_content = """test_id,test_value
1,test"""
    
    files = {
        'files': ('single_file.csv', csv_content, 'text/csv')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/upload-multiple", files=files)
        
        if response.status_code == 400:
            result = response.json()
            print(f"✅ Expected error: {result['error']}")
            print("💡 Tip: Use /upload-single for single file uploads")
        else:
            print(f"Unexpected response: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()

def main():
    """Run all examples"""
    print("🚀 CSV Upload API Examples")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first:")
            print("   uvicorn main:app --reload")
            return
        print("✅ Server is running\n")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please start the server: uvicorn main:app --reload")
        return
    
    # Run examples
    upload_single_file_example()
    upload_multiple_files_example()
    deprecated_upload_example()
    error_handling_example()
    
    print("🎉 Examples completed!")
    print("💡 Try the interactive docs at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()