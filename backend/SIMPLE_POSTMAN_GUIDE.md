# Simple Postman Testing Guide

Quick and easy guide to test the CSV Knowledge Base API with Postman.

## 📦 Import Files

1. **Import Collection**: `CSV_API_Collection.postman_collection.json`
2. **Import Environment**: `CSV_API_Environment.postman_environment.json`
3. **Select Environment**: Choose "CSV API - Local" from dropdown

## 🚀 Start API Server

```bash
python main.py
```

## 🧪 Test Sequence

### 1. Health Check
- **Request**: `GET /health`
- **Expected**: Status 200, health info

### 2. Upload CSV File
- **Request**: `POST /api/v1/upload-single`
- **Action**: Select a CSV file in the form-data
- **Expected**: Status 200, document info with ID
- **Note**: Remember the `id` from response for next steps

### 3. Extract Column Info
- **Request**: `GET /api/v1/metadata/extract/{id}`
- **Action**: Replace `1` with your document ID
- **Expected**: Column names and data types

### 4. Save Metadata
- **Request**: `POST /api/v1/metadata/save`
- **Action**: Update the JSON body with your actual columns
- **Expected**: Status 200, saved metadata

### 5. Process with AI
- **Request**: `POST /api/v1/metadata/process/{id}`
- **Action**: Replace `1` with your document ID
- **Expected**: Status 200, knowledge base created
- **Note**: This takes 10-30 seconds

### 6. Get Knowledge Base Entry
- **Request**: `GET /api/v1/metadata/knowledge-base/{id}`
- **Action**: Replace `1` with your document ID
- **Expected**: AI analysis results

### 7. List All Entries
- **Request**: `GET /api/v1/metadata/knowledge-base`
- **Expected**: List of all knowledge base entries

### 8. Search Entries
- **Request**: `GET /api/v1/metadata/knowledge-base/search`
- **Action**: Change query parameter as needed
- **Expected**: Filtered search results

## 📝 Sample CSV File

Create `test_data.csv`:
```csv
date,amount,category,description
2024-01-01,1000.50,sales,Product A
2024-01-02,750.25,sales,Product B
2024-01-03,1200.00,sales,Product C
```

## 🔧 Update Request Bodies

### Save Metadata Request
Update the JSON body in "Save Complete Metadata" request:

```json
{
  "document_id": YOUR_DOCUMENT_ID,
  "columns": [
    {
      "column_name": "date",
      "data_type": "date",
      "connection_key": "date_key",
      "alias": "transaction_date",
      "description": "Date when the transaction occurred"
    },
    {
      "column_name": "amount",
      "data_type": "float",
      "connection_key": null,
      "alias": "transaction_amount",
      "description": "Monetary value in USD"
    },
    {
      "column_name": "category",
      "data_type": "string",
      "connection_key": null,
      "alias": "sales_category",
      "description": "Category of the transaction"
    },
    {
      "column_name": "description",
      "data_type": "string",
      "connection_key": null,
      "alias": "item_description",
      "description": "Description of the item sold"
    }
  ]
}
```

## 🚨 Troubleshooting

### Connection Refused
- **Problem**: `Error: connect ECONNREFUSED`
- **Solution**: Start the API server with `python main.py`

### 404 Not Found
- **Problem**: Endpoint not found
- **Solution**: Check the API is running on `http://localhost:8000`

### 400 Bad Request on Upload
- **Problem**: File upload fails
- **Solution**: Select a valid CSV file in the request body

### 500 Internal Server Error
- **Problem**: Server error
- **Solution**: Check server logs and ensure `.env` is configured

## 📊 Expected Responses

### Upload Success
```json
{
  "success": true,
  "data": [{
    "id": 1,
    "filename": "test_data.csv",
    "preview": [...],
    "row_count": 3,
    "column_count": 4
  }]
}
```

### Knowledge Base Entry
```json
{
  "id": 1,
  "document_id": 1,
  "filename": "test_data.csv",
  "summary": "Sales transaction data...",
  "data_category": "sales",
  "insights": ["..."],
  "data_quality_score": 92.5
}
```

## 🎯 Quick Tips

1. **Replace IDs**: Update `1` in URLs with actual document IDs
2. **File Selection**: Always select a file for upload requests
3. **JSON Body**: Update metadata request with your column info
4. **Wait for AI**: AI processing takes time, be patient
5. **Check Logs**: Look at server console for error details

## 📚 All Endpoints Included

- ✅ Health Check
- ✅ Upload Single/Multiple CSV
- ✅ Get/List/Delete Documents
- ✅ Extract Column Info
- ✅ Save/Get Metadata
- ✅ AI Processing
- ✅ Knowledge Base Operations
- ✅ Search Functionality

This simplified collection should work reliably in Postman without loading issues!