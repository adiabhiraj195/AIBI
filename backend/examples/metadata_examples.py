"""
Frontend-focused example usage of the CSV Knowledge Base API.

This demonstrates the complete workflow optimized for frontend applications:
1. Upload CSV file
2. Extract column info for form
3. Save complete metadata with user inputs
4. Process with AI
5. View knowledge base results
"""

import requests
import json
from typing import Dict, Any, List

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

class FrontendAPIExample:
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
    
    def upload_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Step 1: Upload CSV file"""
        print(f"📤 Uploading CSV file: {file_path}")
        
        with open(file_path, 'rb') as file:
            files = {'file': (file_path, file, 'text/csv')}
            response = requests.post(f"{self.base_url}/upload-single", files=files)
        
        if response.status_code == 200:
            result = response.json()
            document_id = result['data'][0]['id']
            print(f"✅ File uploaded! Document ID: {document_id}")
            return result['data'][0]
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
    
    def get_column_info_for_form(self, document_id: int) -> Dict[str, Any]:
        """Step 2: Get column info for frontend form"""
        print(f"📋 Getting column info for form (Document ID: {document_id})")
        
        response = requests.get(f"{self.base_url}/metadata/extract/{document_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved info for {result['total_columns']} columns")
            print("📊 Sample data preview:")
            for i, row in enumerate(result['sample_data'][:2]):
                print(f"  Row {i+1}: {row}")
            return result
        else:
            print(f"❌ Failed to get column info: {response.text}")
            return None
    
    def save_complete_metadata(self, document_id: int, column_info: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Save complete metadata with user inputs"""
        print(f"💾 Saving complete metadata for document {document_id}")
        
        # Simulate user filling out the form
        enriched_columns = []
        for i, col in enumerate(column_info['columns']):
            enriched_col = {
                "column_name": col["column_name"],
                "data_type": col["data_type"],
                "connection_key": f"conn_key_{i+1}" if i % 2 == 0 else None,  # Some have connection keys
                "alias": f"alias_{col['column_name'].lower().replace(' ', '_')}",
                "description": f"This column represents {col['column_name'].lower()} data with {col['data_type']} values. Used for business analysis and reporting."
            }
            enriched_columns.append(enriched_col)
        
        payload = {
            "document_id": document_id,
            "columns": enriched_columns
        }
        
        response = requests.post(f"{self.base_url}/metadata/save", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Metadata saved successfully!")
            print(f"  📝 Saved {len(result['columns'])} column descriptions")
            return result
        else:
            print(f"❌ Failed to save metadata: {response.text}")
            return None
    
    def process_with_ai(self, document_id: int) -> Dict[str, Any]:
        """Step 4: Process with AI"""
        print(f"🤖 Processing document {document_id} with AI...")
        
        response = requests.post(f"{self.base_url}/metadata/process/{document_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI processing completed!")
            print(f"📊 Knowledge Base ID: {result['knowledge_base_id']}")
            print(f"📝 Summary: {result['summary'][:100]}...")
            return result
        else:
            print(f"❌ AI processing failed: {response.text}")
            return None
    
    def get_knowledge_base_entry(self, document_id: int) -> Dict[str, Any]:
        """Step 5: Get complete knowledge base entry"""
        print(f"📖 Fetching knowledge base entry for document {document_id}")
        
        response = requests.get(f"{self.base_url}/metadata/knowledge-base/{document_id}")
        
        if response.status_code == 200:
            entry = response.json()
            print("✅ Knowledge base entry retrieved!")
            print(f"📊 Data Category: {entry['data_category']}")
            print(f"🎯 Quality Score: {entry['data_quality_score']}/100")
            print(f"💡 Insights: {len(entry['insights'])} key insights")
            print(f"🔧 Use Cases: {len(entry['use_cases'])} potential uses")
            return entry
        else:
            print(f"❌ Failed to get knowledge base entry: {response.text}")
            return None
    
    def list_knowledge_base_summaries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get knowledge base summaries for frontend display"""
        print(f"📋 Listing knowledge base summaries (limit: {limit})")
        
        response = requests.get(f"{self.base_url}/metadata/knowledge-base?limit={limit}")
        
        if response.status_code == 200:
            entries = response.json()
            print(f"✅ Found {len(entries)} knowledge base entries:")
            for entry in entries:
                print(f"  📄 {entry['filename']} - {entry['data_category']} (Score: {entry['data_quality_score']})")
            return entries
        else:
            print(f"❌ Failed to list entries: {response.text}")
            return []
    
    def search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge base for frontend"""
        print(f"🔎 Searching knowledge base for: '{query}'")
        
        response = requests.get(f"{self.base_url}/metadata/knowledge-base/search?query={query}&limit=10")
        
        if response.status_code == 200:
            entries = response.json()
            print(f"✅ Found {len(entries)} matching entries:")
            for entry in entries:
                print(f"  📄 {entry['filename']} - {entry['summary'][:50]}...")
            return entries
        else:
            print(f"❌ Search failed: {response.text}")
            return []
    
    def complete_frontend_workflow(self, csv_file_path: str):
        """Complete workflow optimized for frontend applications"""
        print("🚀 Starting Frontend-Optimized CSV Knowledge Base Workflow")
        print("=" * 70)
        
        # Step 1: Upload CSV
        document = self.upload_csv_file(csv_file_path)
        if not document:
            return
        
        document_id = document['id']
        print()
        
        # Step 2: Get column info for form
        column_info = self.get_column_info_for_form(document_id)
        if not column_info:
            return
        print()
        
        # Step 3: Save complete metadata (simulating user form submission)
        saved_metadata = self.save_complete_metadata(document_id, column_info)
        if not saved_metadata:
            return
        print()
        
        # Step 4: Process with AI
        ai_result = self.process_with_ai(document_id)
        if not ai_result:
            return
        print()
        
        # Step 5: Get complete knowledge base entry
        kb_entry = self.get_knowledge_base_entry(document_id)
        if kb_entry:
            print("\n🎯 AI Analysis Results:")
            print(f"  📊 Category: {kb_entry['data_category']}")
            print(f"  🏆 Quality Score: {kb_entry['data_quality_score']}/100")
            print(f"  💡 Key Insights:")
            for insight in kb_entry['insights'][:3]:
                print(f"    • {insight}")
            print(f"  🔧 Use Cases:")
            for use_case in kb_entry['use_cases'][:3]:
                print(f"    • {use_case}")
        print()
        
        # Step 6: Show knowledge base listing
        self.list_knowledge_base_summaries(5)
        print()
        
        print("✅ Complete frontend workflow finished successfully!")
        print("🎉 Your CSV is now part of the AI-powered knowledge base!")
        print("=" * 70)

def frontend_api_examples():
    """Demonstrate frontend-focused API usage"""
    api = FrontendAPIExample()
    
    print("🌐 Frontend-Focused CSV Knowledge Base API Examples")
    print("=" * 60)
    
    # Example 1: List existing knowledge base (for dashboard)
    print("\n📊 Dashboard View - Knowledge Base Overview:")
    api.list_knowledge_base_summaries(5)
    
    # Example 2: Search functionality
    print("\n🔍 Search Functionality:")
    api.search_knowledge_base("csv")
    
    print("\n💡 Frontend Integration Tips:")
    print("1. Use /metadata/extract/{id} to populate your metadata form")
    print("2. Validate required fields (description is mandatory)")
    print("3. Use /metadata/save to store complete user inputs")
    print("4. Process with /metadata/process/{id} for AI analysis")
    print("5. Display results from /metadata/knowledge-base/{id}")
    print("6. Use search and list endpoints for dashboard views")
    
    print("\n🚀 To test complete workflow:")
    print("1. Create a sample CSV file")
    print("2. Update the file path in complete_frontend_workflow()")
    print("3. Run the workflow to see the full process")

def main():
    """Main example function"""
    api = FrontendAPIExample()
    
    # Uncomment to run complete workflow with your CSV file
    # api.complete_frontend_workflow("path/to/your/sample.csv")
    
    # Run frontend examples
    frontend_api_examples()

if __name__ == "__main__":
    main()