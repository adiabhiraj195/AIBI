#!/usr/bin/env python3
"""
Simple test script to verify the new CSV upload endpoints work correctly.
This script creates sample CSV files and tests the new endpoints.
"""

import requests
import io
import csv
import tempfile
import os
from typing import Dict, Any

# Base URL for the API (adjust if running on different host/port)
BASE_URL = "http://localhost:8000/api/v1"

def create_sample_csv(filename: str, rows: int = 10) -> str:
    """Create a sample CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['id', 'name', 'email', 'age'])
        # Write data rows
        for i in range(1, rows + 1):
            writer.writerow([i, f'User {i}', f'user{i}@example.com', 20 + (i % 50)])
        return f.name

def test_single_upload():
    """Test the single file upload endpoint"""
    print("Testing single file upload endpoint...")
    
    # Create a sample CSV file
    csv_file = create_sample_csv("test_single.csv", 5)
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': ('test_single.csv', f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/upload-single", files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Single file upload test PASSED")
            return True
        else:
            print("❌ Single file upload test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Single file upload test ERROR: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(csv_file):
            os.unlink(csv_file)

def test_multiple_upload():
    """Test the multiple files upload endpoint"""
    print("\nTesting multiple files upload endpoint...")
    
    # Create multiple sample CSV files
    csv_file1 = create_sample_csv("test_multiple_1.csv", 3)
    csv_file2 = create_sample_csv("test_multiple_2.csv", 7)
    
    try:
        files = []
        with open(csv_file1, 'rb') as f1, open(csv_file2, 'rb') as f2:
            files = [
                ('files', ('test_multiple_1.csv', f1.read(), 'text/csv')),
                ('files', ('test_multiple_2.csv', f2.read(), 'text/csv'))
            ]
            response = requests.post(f"{BASE_URL}/upload-multiple", files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Multiple files upload test PASSED")
            return True
        else:
            print("❌ Multiple files upload test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Multiple files upload test ERROR: {e}")
        return False
    finally:
        # Clean up
        for csv_file in [csv_file1, csv_file2]:
            if os.path.exists(csv_file):
                os.unlink(csv_file)

def test_deprecated_upload():
    """Test the deprecated upload endpoint"""
    print("\nTesting deprecated upload endpoint...")
    
    # Create a sample CSV file
    csv_file = create_sample_csv("test_deprecated.csv", 4)
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'files': ('test_deprecated.csv', f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Deprecated upload test PASSED")
            return True
        else:
            print("❌ Deprecated upload test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Deprecated upload test ERROR: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(csv_file):
            os.unlink(csv_file)

def test_validation_errors():
    """Test validation error scenarios"""
    print("\nTesting validation scenarios...")
    
    # Test 1: Single file to multiple endpoint
    csv_file = create_sample_csv("test_validation.csv", 2)
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'files': ('test_validation.csv', f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/upload-multiple", files=files)
        
        print(f"Multiple endpoint with single file - Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Validation test PASSED - correctly rejected single file")
        else:
            print("❌ Validation test FAILED - should reject single file")
            
    except Exception as e:
        print(f"❌ Validation test ERROR: {e}")
    finally:
        if os.path.exists(csv_file):
            os.unlink(csv_file)

def main():
    """Run all tests"""
    print("🚀 Starting CSV Upload Endpoints Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code != 200:
            print("❌ Server is not running or not healthy. Please start the server first.")
            return
        print("✅ Server is running and healthy")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the server is running on http://localhost:8000")
        return
    
    print("\n" + "=" * 50)
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_single_upload():
        tests_passed += 1
    
    if test_multiple_upload():
        tests_passed += 1
        
    if test_deprecated_upload():
        tests_passed += 1
        
    test_validation_errors()  # This doesn't count towards pass/fail
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The new endpoints are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server logs and configuration.")

if __name__ == "__main__":
    main()

# ===== METADATA AND KNOWLEDGE BASE API TESTS =====

def test_extract_column_metadata():
    """Test extracting column metadata from a document"""
    print("\n🔍 Testing column metadata extraction...")
    
    # First upload a file to get a document ID
    test_file_path = "test_sample.csv"
    create_test_csv(test_file_path)
    
    try:
        # Upload file
        with open(test_file_path, 'rb') as file:
            files = {'file': (test_file_path, file, 'text/csv')}
            upload_response = requests.post(f"{BASE_URL}/upload-single", files=files)
        
        if upload_response.status_code == 200:
            document_id = upload_response.json()['data'][0]['id']
            
            # Extract column metadata
            response = requests.get(f"{BASE_URL}/metadata/document/{document_id}/columns")
            
            if response.status_code == 200:
                columns = response.json()
                print(f"✅ Successfully extracted {len(columns)} columns")
                for col in columns:
                    print(f"  - {col['column_name']} ({col['data_type']})")
                return document_id, columns
            else:
                print(f"❌ Column extraction failed: {response.status_code}")
                print(response.text)
        else:
            print(f"❌ File upload failed: {upload_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error in column metadata extraction: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    return None, []

def test_save_document_metadata():
    """Test saving document metadata with enriched information"""
    print("\n💾 Testing document metadata saving...")
    
    # Get document and columns from previous test
    document_id, columns = test_extract_column_metadata()
    
    if not document_id or not columns:
        print("❌ Cannot test metadata saving without valid document and columns")
        return None
    
    try:
        # Enrich columns with additional information
        enriched_columns = []
        for i, col in enumerate(columns):
            enriched_col = {
                "column_name": col["column_name"],
                "data_type": col["data_type"],
                "connection_key": f"test_key_{i+1}",
                "alias": f"test_alias_{col['column_name'].lower()}",
                "description": f"Test description for {col['column_name']}"
            }
            enriched_columns.append(enriched_col)
        
        payload = {
            "document_id": document_id,
            "columns": enriched_columns
        }
        
        response = requests.post(f"{BASE_URL}/metadata/document/save", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document metadata saved successfully")
            print(f"  Document ID: {result['document_id']}")
            print(f"  Filename: {result['filename']}")
            print(f"  Columns: {len(result['columns'])}")
            return document_id
        else:
            print(f"❌ Metadata saving failed: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error in metadata saving: {e}")
    
    return None

def test_llm_analysis():
    """Test LLM analysis of document metadata"""
    print("\n🤖 Testing LLM analysis...")
    
    # Get document ID from previous test
    document_id = test_save_document_metadata()
    
    if not document_id:
        print("❌ Cannot test LLM analysis without valid document metadata")
        return None
    
    try:
        response = requests.post(f"{BASE_URL}/metadata/document/{document_id}/analyze")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM analysis completed successfully")
            print(f"  Success: {result['success']}")
            print(f"  Knowledge Base ID: {result['knowledge_base_id']}")
            print(f"  Message: {result['message']}")
            
            # Print some analysis details
            analysis = result.get('analysis', {})
            if 'summary' in analysis:
                print(f"  Summary: {analysis['summary'][:100]}...")
            
            return result['knowledge_base_id']
        else:
            print(f"❌ LLM analysis failed: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error in LLM analysis: {e}")
    
    return None

def test_get_knowledge_base_entry():
    """Test retrieving knowledge base entry"""
    print("\n📖 Testing knowledge base entry retrieval...")
    
    # This test depends on having a knowledge base entry
    # For demo purposes, we'll try to get any existing entry
    try:
        # First, list entries to see if any exist
        list_response = requests.get(f"{BASE_URL}/metadata/knowledge-base?limit=1")
        
        if list_response.status_code == 200:
            entries = list_response.json()
            if entries:
                document_id = entries[0]['document_id']
                
                # Get specific entry
                response = requests.get(f"{BASE_URL}/metadata/knowledge-base/document/{document_id}")
                
                if response.status_code == 200:
                    entry = response.json()
                    print("✅ Knowledge base entry retrieved successfully")
                    print(f"  Entry ID: {entry['id']}")
                    print(f"  Document ID: {entry['document_id']}")
                    print(f"  Filename: {entry['filename']}")
                    
                    analysis = entry.get('llm_analysis', {})
                    print(f"  Data Category: {analysis.get('data_category', 'N/A')}")
                    print(f"  Key Insights: {len(analysis.get('key_insights', []))}")
                    
                    return True
                else:
                    print(f"❌ Entry retrieval failed: {response.status_code}")
            else:
                print("ℹ️ No knowledge base entries found")
        else:
            print(f"❌ Failed to list entries: {list_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error in knowledge base entry retrieval: {e}")
    
    return False

def test_list_knowledge_base_entries():
    """Test listing knowledge base entries"""
    print("\n📋 Testing knowledge base entries listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/metadata/knowledge-base?limit=10")
        
        if response.status_code == 200:
            entries = response.json()
            print(f"✅ Successfully retrieved {len(entries)} knowledge base entries")
            
            for entry in entries[:3]:  # Show first 3 entries
                print(f"  - ID: {entry['id']}, File: {entry['filename']}")
            
            return True
        else:
            print(f"❌ Listing failed: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error in listing knowledge base entries: {e}")
    
    return False

def test_search_knowledge_base():
    """Test searching knowledge base entries"""
    print("\n🔎 Testing knowledge base search...")
    
    try:
        # Search for CSV files (common term)
        response = requests.get(f"{BASE_URL}/metadata/knowledge-base/search?query=csv&limit=5")
        
        if response.status_code == 200:
            entries = response.json()
            print(f"✅ Search completed, found {len(entries)} matching entries")
            
            for entry in entries:
                print(f"  - {entry['filename']} (ID: {entry['id']})")
            
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error in knowledge base search: {e}")
    
    return False

def test_metadata_workflow():
    """Test the complete metadata workflow"""
    print("\n🚀 Testing complete metadata workflow...")
    print("=" * 50)
    
    success_count = 0
    total_tests = 6
    
    # Run all metadata tests
    tests = [
        ("Column Metadata Extraction", lambda: test_extract_column_metadata()[0] is not None),
        ("Document Metadata Saving", lambda: test_save_document_metadata() is not None),
        ("LLM Analysis", lambda: test_llm_analysis() is not None),
        ("Knowledge Base Entry Retrieval", test_get_knowledge_base_entry),
        ("Knowledge Base Listing", test_list_knowledge_base_entries),
        ("Knowledge Base Search", test_search_knowledge_base)
    ]
    
    for test_name, test_func in tests:
        try:
            if test_func():
                success_count += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("=" * 50)
    print(f"📊 Metadata Workflow Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All metadata tests passed!")
    else:
        print("⚠️ Some metadata tests failed. Check the logs above.")

# Update the main function to include metadata tests
def run_all_tests():
    """Run all API tests including metadata tests"""
    print("🧪 Starting comprehensive API tests...")
    print("=" * 60)
    
    # Original CSV tests
    test_health_endpoint()
    test_single_file_upload()
    test_multiple_file_upload()
    test_get_document()
    test_list_documents()
    test_update_description_status()
    
    print("\n" + "=" * 60)
    print("🔬 Starting Metadata & Knowledge Base Tests...")
    
    # New metadata tests
    test_metadata_workflow()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == "__main__":
    # You can run individual tests or all tests
    run_all_tests()
    
    # Or run specific metadata tests:
    # test_metadata_workflow()