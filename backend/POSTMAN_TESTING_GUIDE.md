# Postman Testing Guide

Complete guide for testing the CSV Knowledge Base API using the provided Postman collection.

## 📦 Files Included

- `CSV_Knowledge_Base_API.postman_collection.json` - Complete API collection
- `CSV_Knowledge_Base_API.postman_environment.json` - Environment variables
- `POSTMAN_TESTING_GUIDE.md` - This guide

## 🚀 Quick Setup

### 1. Import Collection & Environment

1. **Open Postman**
2. **Import Collection**: 
   - Click "Import" → Select `CSV_Knowledge_Base_API.postman_collection.json`
3. **Import Environment**: 
   - Click "Import" → Select `CSV_Knowledge_Base_API.postman_environment.json`
4. **Select Environment**: 
   - Choose "CSV Knowledge Base API - Local" from the environment dropdown

### 2. Start the API Server

```bash
# Ensure your environment is configured
python validate_config.py

# Start the server
python main.py
```

### 3. Prepare Test Data

Create a sample CSV file for testing (e.g., `sample_data.csv`):
```csv
date,amount,category,description
2024-01-01,1000.50,sales,Product A sale
2024-01-02,750.25,sales,Product B sale
2024-01-03,1200.00,sales,Product C sale
```

## 🧪 Testing Workflow

### Phase 1: System Health
1. **Health Check** - Verify API is running
2. **Root Endpoint** - Check API information

### Phase 2: CSV Upload
3. **Upload Single CSV File** - Upload your test CSV
   - 📝 **Action Required**: Select your CSV file in the request body
   - ✅ **Auto-saves**: `document_id` for subsequent requests

### Phase 3: Metadata Management
4. **Extract Column Info for Form** - Get column structure
   - ✅ **Auto-saves**: Column information for metadata form
5. **Save Complete Metadata** - Add descriptions and metadata
   - 📝 **Action Required**: Update request body with your column descriptions
6. **Get Saved Metadata** - Verify metadata was saved

### Phase 4: AI Processing
7. **Process with AI** - Generate knowledge base entry
   - ⏱️ **Note**: This may take 10-30 seconds
   - ✅ **Auto-saves**: `knowledge_base_id`
8. **Get Knowledge Base Entry** - View AI analysis results

### Phase 5: Discovery & Management
9. **List Knowledge Base Entries** - Browse all entries
10. **Search Knowledge Base** - Test search functionality
11. **List All Documents** - View uploaded documents

## 📋 Collection Structure

### 🏥 Health & System
- **Health Check**: `/health`
- **Root Endpoint**: `/`

### 📁 CSV Upload & Management
- **Upload Single CSV File**: `POST /api/v1/upload-single`
- **Upload Multiple CSV Files**: `POST /api/v1/upload-multiple`
- **Get Document by ID**: `GET /api/v1/document`
- **Get Document with Full Data**: `GET /api/v1/document` (with full data)
- **List All Documents**: `GET /api/v1/documents`
- **Update Description Status**: `PATCH /api/v1/document/{id}/description-status`
- **Delete Document**: `DELETE /api/v1/document/{id}`

### 🧠 Metadata & Knowledge Base
- **Extract Column Info for Form**: `GET /api/v1/metadata/extract/{id}`
- **Save Complete Metadata**: `POST /api/v1/metadata/save`
- **Get Saved Metadata**: `GET /api/v1/metadata/document/{id}`
- **Process with AI**: `POST /api/v1/metadata/process/{id}`
- **Get Knowledge Base Entry**: `GET /api/v1/metadata/knowledge-base/{id}`
- **List Knowledge Base Entries**: `GET /api/v1/metadata/knowledge-base`
- **Search Knowledge Base**: `GET /api/v1/metadata/knowledge-base/search`
- **Delete Knowledge Base Entry**: `DELETE /api/v1/metadata/knowledge-base/{id}`

### 🔄 Legacy Endpoints
- Deprecated endpoints for backward compatibility testing

## 🔧 Environment Variables

The collection uses these environment variables:

| Variable | Description | Auto-Set |
|----------|-------------|----------|
| `base_url` | API base URL | ✅ |
| `document_id` | Uploaded document ID | ✅ |
| `knowledge_base_id` | Knowledge base entry ID | ✅ |
| `filename` | Uploaded filename | ✅ |
| `column_info` | Extracted column data | ✅ |

## 📝 Manual Configuration Required

### 1. Upload Single CSV File
- **File Selection**: Choose your CSV file in the form-data body
- **Result**: Sets `document_id` automatically

### 2. Save Complete Metadata
Update the request body with your actual column data:

```json
{
  "document_id": {{document_id}},
  "columns": [
    {
      "column_name": "date",
      "data_type": "date",
      "connection_key": "date_key",
      "alias": "transaction_date",
      "description": "Date when the transaction occurred, used for temporal analysis"
    },
    {
      "column_name": "amount",
      "data_type": "float",
      "connection_key": null,
      "alias": "transaction_amount",
      "description": "Monetary value in USD, critical for financial analysis"
    }
  ]
}
```

## 🧪 Test Scripts Included

The collection includes automated test scripts:

### Response Validation
- Status code verification
- Response structure validation
- Response time checks

### Variable Management
- Auto-extraction of IDs from responses
- Environment variable updates
- Error logging for debugging

## 🚨 Troubleshooting

### Common Issues

1. **Server Not Running**
   ```
   Error: connect ECONNREFUSED 127.0.0.1:8000
   ```
   **Solution**: Start the API server with `python main.py`

2. **Missing Environment Variables**
   ```
   Error: GROQ_API_KEY environment variable is required
   ```
   **Solution**: Configure your `.env` file and restart the server

3. **File Upload Fails**
   ```
   Status: 400 Bad Request
   ```
   **Solution**: Ensure you've selected a valid CSV file in the request

4. **AI Processing Timeout**
   ```
   Status: 504 Gateway Timeout
   ```
   **Solution**: Check your Groq API key and try again

### Debug Tips

1. **Check Console**: View Postman console for detailed error logs
2. **Verify Environment**: Ensure correct environment is selected
3. **Check Variables**: Verify `document_id` is set after upload
4. **API Documentation**: Visit `http://localhost:8000/docs` for interactive testing

## 🔄 Complete Test Sequence

Run requests in this order for full workflow testing:

1. ✅ **Health Check**
2. 📤 **Upload Single CSV File** (select your CSV)
3. 🔍 **Extract Column Info for Form**
4. 💾 **Save Complete Metadata** (update request body)
5. 🤖 **Process with AI** (wait for completion)
6. 📖 **Get Knowledge Base Entry**
7. 📋 **List Knowledge Base Entries**
8. 🔎 **Search Knowledge Base**

## 📊 Expected Results

### Successful Upload
```json
{
  "success": true,
  "data": [{
    "id": 123,
    "filename": "sample_data.csv",
    "preview": [...],
    "row_count": 3,
    "column_count": 4
  }]
}
```

### AI Analysis Result
```json
{
  "id": 456,
  "summary": "Sales transaction data with temporal and categorical analysis",
  "data_category": "sales",
  "insights": ["Consistent daily sales patterns", "..."],
  "data_quality_score": 92.5,
  "recommendations": ["Consider adding customer segmentation", "..."]
}
```

## 🎯 Pro Tips

1. **Use Runner**: Use Postman's Collection Runner for automated testing
2. **Save Responses**: Save successful responses as examples
3. **Environment Switching**: Create separate environments for dev/staging/prod
4. **Monitor**: Use Postman Monitor for continuous API health checks
5. **Documentation**: Generate API documentation from the collection

## 🤝 Support

If you encounter issues:
1. Check the API server logs
2. Verify your `.env` configuration
3. Test individual endpoints in the browser at `/docs`
4. Review the collection's test scripts for debugging info