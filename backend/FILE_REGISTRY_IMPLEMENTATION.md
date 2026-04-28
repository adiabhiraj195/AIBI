# File Upload and Processing Pipeline - Complete Implementation

## Overview

This document describes the complete system for uploading CSV files, processing them through an LLM-based schema analyzer, creating dynamic PostgreSQL tables, and tracking all files in a central registry.

## System Architecture

### 1. **File Upload Flow**

```
CSV File Upload
    ↓
Parse & Store (csv_documents table)
    ↓
Register in File Registry
    ↓
LLM Analysis (generate schema)
    ↓
Create Dynamic Table (store data rows)
    ↓
Track in Registry (with is_described flag)
```

### 2. **Database Tables**

#### **csv_documents** (Source files)
- `id`: Document ID
- `filename`: Original file name
- `preview_data`: First N rows (JSON)
- `full_data`: All rows (JSON) - used for dynamic table insertion
- `row_count`: Number of data rows
- `column_count`: Number of columns
- `is_described`: User verified the metadata (Boolean)
- `upload_date`: When file was uploaded

#### **file_registry** (Central tracking) ⭐ **NEW**
- `id`: Registry entry ID
- `document_id`: FK to csv_documents
- `filename`: File name (indexed for quick lookup)
- `file_type`: Type (csv, excel, json, etc.)
- `dynamic_table_name`: Name of created PostgreSQL table
- `data_category`: Category from LLM analysis (Financial, Sales, etc.)
- `row_count`: Number of data rows
- `column_count`: Number of columns
- `is_described`: User verified? (Boolean, indexed)
- `verified_at`: When user verified (timestamp)
- `upload_date`: When uploaded (indexed, desc)
- `table_created_at`: When dynamic table was created

#### **knowledge_base** (LLM analysis results)
- Stores: summary, insights, use_cases, recommendations, column_analysis
- Linked to: csv_documents and file_registry via document_id

#### **Dynamic Tables** (Data storage)
- One table per uploaded file
- Named: `{filename_normalized}_{document_id}`
- Columns: id (PK), created_at, + columns from LLM schema
- All data rows from CSV inserted

## API Endpoints

### Upload & Register

**POST** `/api/v1/csv/upload`
- Uploads CSV file
- Stores in csv_documents
- Automatically registers in file_registry
- Returns document_id

### Metadata & Processing

**POST** `/api/v1/metadata/save/{document_id}`
- User provides column descriptions
- Saves to document_metadata

**POST** `/api/v1/metadata/process/{document_id}`
- Calls LLM to analyze and generate schema
- Stores analysis in knowledge_base
- Creates dynamic table with all CSV rows
- Updates file_registry:
  - Sets `dynamic_table_name`
  - Sets `data_category` (from LLM)
  - Sets `table_created_at`
  - Marks `is_described = True`

### File Registry - View/Track

**GET** `/api/v1/metadata/registry/summary`
- Returns: Total files, verified, with tables, unverified
```json
{
  "success": true,
  "summary": {
    "total_files": 15,
    "verified_files": 8,
    "with_dynamic_tables": 8,
    "unverified_files": 7,
    "without_tables": 7
  }
}
```

**GET** `/api/v1/metadata/registry/files?limit=20&offset=0&verified_only=false`
- Lists all registered files with full details
- Filter by verified_only if needed
```json
{
  "success": true,
  "count": 8,
  "files": [
    {
      "id": 1,
      "document_id": 1,
      "filename": "sales_2024.csv",
      "file_type": "csv",
      "dynamic_table_name": "sales_2024_1",
      "data_category": "Sales",
      "row_count": 1000,
      "column_count": 12,
      "is_described": true,
      "verified_at": "2025-01-15T10:30:00",
      "upload_date": "2025-01-15T09:00:00",
      "table_created_at": "2025-01-15T10:35:00"
    }
  ]
}
```

**GET** `/api/v1/metadata/registry/file/{document_id}`
- Get details for specific file

**GET** `/api/v1/metadata/registry/category/{category}`
- Get all files in a category (Financial, Sales, etc.)

## Complete Upload-to-Process Flow

### Step 1: Upload File
```bash
curl -X POST "http://localhost:8001/api/v1/csv/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sales_data.csv"
```
Response:
```json
{
  "success": true,
  "id": 5,
  "filename": "sales_data.csv",
  "preview": [
    {"Product": "Widget A", "Sales": 1000},
    {"Product": "Widget B", "Sales": 1500}
  ]
}
```

**What happens automatically:**
- File parsed and stored in `csv_documents` with full_data
- Entry created in `file_registry` with is_described = false
- No dynamic table yet (waiting for user review)

### Step 2: User Saves Metadata
```bash
curl -X POST "http://localhost:8001/api/v1/metadata/save/5" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": [
      {
        "column_name": "Product",
        "description": "Product name",
        "data_type": "string"
      },
      {
        "column_name": "Sales",
        "description": "Sales amount in dollars",
        "data_type": "float"
      }
    ]
  }'
```

**What happens:**
- Metadata saved to `document_metadata` table
- User review complete, system ready to process

### Step 3: Process with AI
```bash
curl -X POST "http://localhost:8001/api/v1/metadata/process/5"
```

Response:
```json
{
  "success": true,
  "knowledge_base_id": 5,
  "message": "Document processed successfully with AI and data table created",
  "summary": "This is a sales transactions dataset..."
}
```

**What happens automatically:**
1. ✅ LLM analyzes data and schema
2. ✅ Knowledge base entry created with insights
3. ✅ Dynamic table `sales_data_5` created
4. ✅ All CSV rows (from full_data) inserted into table
5. ✅ File registry updated:
   - `dynamic_table_name` = "sales_data_5"
   - `data_category` = "Sales" (from LLM)
   - `table_created_at` = current timestamp
   - `is_described` = true
   - `verified_at` = current timestamp

## Key Features

### ✅ Automatic Registration
Files are registered immediately upon upload, making them trackable before processing.

### ✅ Complete Data Storage
- `full_data` in csv_documents ensures all rows available
- Dynamic tables created with all rows inserted
- No data loss in the process

### ✅ Verification Tracking
- `is_described` flag shows user review status
- `verified_at` timestamp tracks when user completed review
- Registry provides overview of verification progress

### ✅ Category Tracking
- LLM determines data category (Financial, Sales, Customer, etc.)
- Users can filter files by category
- Enables data discovery and organization

### ✅ Table Lifecycle Tracking
- `upload_date`: When file entered system
- `table_created_at`: When dynamic table was created
- Complete audit trail

### ✅ Indexed Queries
- Fast lookup by is_described (for pending reviews)
- Fast lookup by category (for data discovery)
- Fast lookup by upload_date (for recent files)

## Code Components

### File Registry Repository
[File: `app/repositories/file_registry_repository.py`]
- `register_file()`: Called on upload
- `update_dynamic_table()`: Called after dynamic table creation
- `mark_as_described()`: Called when metadata processed
- `get_registry_entry()`: Retrieve file details
- `list_all_files()`: List with filtering
- `get_files_by_category()`: Filter by category
- `get_registry_summary()`: Statistics

### CSV Repository (Updated)
[File: `app/repositories/csv_repository.py`]
- `create_document()`: Now also calls `FileRegistryRepository.register_file()`

### Metadata Service (Updated)
[File: `app/services/metadata_service.py`]
- `process_document_with_ai()`: Now updates file_registry after table creation
- `_generate_and_create_table()`: Returns (table_name, rows_inserted)

### Metadata Controller (New Endpoints)
[File: `app/controllers/metadata_controller.py`]
- `/registry/summary`: Registry statistics
- `/registry/files`: List all registered files
- `/registry/file/{id}`: Get specific file details
- `/registry/category/{cat}`: Filter by category

### Database Model (Updated)
[File: `app/models/database_models.py`]
- `FileRegistry`: New ORM model with all tracking fields

## Migration

Run migration to create file_registry table:
```bash
psql postgresql://user:password@localhost:5432/db < migrations_file_registry.sql
```

Or execute in Python:
```python
from app.database.connection import DatabaseConnection
DatabaseConnection.init_db()  # Auto-creates all tables
```

## Status Monitoring

### View Summary
```bash
curl "http://localhost:8001/api/v1/metadata/registry/summary"
```

### Check Unverified Files
```bash
curl "http://localhost:8001/api/v1/metadata/registry/files?verified_only=false"
```

### Find Files by Category
```bash
curl "http://localhost:8001/api/v1/metadata/registry/category/Financial"
```

## Error Handling

### Upload Fails
- User sees error, file not stored

### Registration Fails
- File uploaded but registry entry not created (rare)
- Warning logged but doesn't block upload

### Dynamic Table Creation Fails
- File stays unverified (is_described = false)
- User can retry from process step

### Already Registered
- Updating existing document skips re-registration
- Prevents duplicate entries

## Backward Compatibility

✅ All existing endpoints work without changes
✅ file_registry is optional tracking layer
✅ Can be adopted gradually

## Performance Considerations

### Indexes
- `is_described`: Fast queries for pending reviews
- `filename`: Fast file lookup
- `upload_date DESC`: Recent files query
- `data_category`: Category filtering

### Query Examples
```sql
-- Find unverified files
SELECT * FROM file_registry WHERE is_described = false;

-- Find all financial files
SELECT * FROM file_registry WHERE data_category = 'Financial';

-- Recent uploads
SELECT * FROM file_registry ORDER BY upload_date DESC LIMIT 10;

-- Summary statistics
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN is_described THEN 1 ELSE 0 END) as verified,
  SUM(CASE WHEN dynamic_table_name IS NOT NULL THEN 1 ELSE 0 END) as with_tables
FROM file_registry;
```

## Testing

### Test Complete Flow
1. Upload file → Check registry
2. Save metadata → Check registry
3. Process file → Check registry (table created, is_described = true)
4. Query category → Get file from category

### Check Data Integrity
```python
# Verify rows in dynamic table
SELECT COUNT(*) FROM sales_data_5;
# Should match: file_registry.row_count
```

## Summary

The new File Registry system provides:
- ✅ Central tracking of all uploaded files
- ✅ Verification status monitoring
- ✅ Dynamic table lifecycle tracking
- ✅ Data category organization
- ✅ Quick status queries
- ✅ Complete audit trail
