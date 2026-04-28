# File Registry - Quick Start Guide

## What This Does

When you upload a CSV file, the system:
1. ✅ Stores the file in the database
2. ✅ **Registers it in a central tracking table** (NEW)
3. ✅ Processes it through AI to generate schema
4. ✅ Creates a dynamic table with all data rows
5. ✅ **Updates the registry with table name and category** (NEW)
6. ✅ Marks it as verified/described by user

## Setup (One Time)

### Create the Registry Table

```bash
# Option 1: Run SQL migration
psql -U your_user -d your_db -f migrations_file_registry.sql

# Option 2: Automatic (no manual SQL needed)
python3 -c "from app.database.connection import DatabaseConnection; DatabaseConnection.init_db()"
```

## Complete Upload → Process → Track Flow

### 1️⃣ Upload CSV File

```bash
curl -X POST "http://localhost:8001/api/v1/csv/upload" \
  -F "file=@data.csv"
```

**What happens automatically:**
- ✅ File stored in database
- ✅ **Registered in file_registry table**
- ✅ `is_described = false` (waiting for review)

### 2️⃣ User Reviews & Saves Metadata

```bash
curl -X POST "http://localhost:8001/api/v1/metadata/save/1" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": [
      {
        "column_name": "Product",
        "description": "Product name",
        "data_type": "string"
      }
    ]
  }'
```

**What happens:**
- ✅ Metadata saved

### 3️⃣ Process File with AI

```bash
curl -X POST "http://localhost:8001/api/v1/metadata/process/1"
```

**What happens automatically:**
- ✅ LLM analyzes data and schema
- ✅ Determines data category (Financial, Sales, etc.)
- ✅ Creates dynamic table (e.g., `data_1`)
- ✅ **Inserts all CSV rows into dynamic table**
- ✅ **Updates file_registry:**
  - `dynamic_table_name` = "data_1"
  - `data_category` = "Financial" 
  - `is_described` = true
  - `table_created_at` = timestamp
  - `verified_at` = timestamp

## Track Your Files

### See Status of All Files

```bash
curl "http://localhost:8001/api/v1/metadata/registry/summary"
```

Response:
```json
{
  "success": true,
  "summary": {
    "total_files": 10,
    "verified_files": 7,
    "with_dynamic_tables": 7,
    "unverified_files": 3,
    "without_tables": 3
  }
}
```

### List All Files

```bash
curl "http://localhost:8001/api/v1/metadata/registry/files"
```

Shows each file with:
- Filename
- Dynamic table name (if created)
- Data category
- is_described status
- Upload date
- Table creation date

### Find Unverified Files (Waiting for User Review)

```bash
curl "http://localhost:8001/api/v1/metadata/registry/files?verified_only=false"
```

### Find Files by Category

```bash
curl "http://localhost:8001/api/v1/metadata/registry/category/Financial"
curl "http://localhost:8001/api/v1/metadata/registry/category/Sales"
curl "http://localhost:8001/api/v1/metadata/registry/category/Customer"
```

### Get Details for One File

```bash
curl "http://localhost:8001/api/v1/metadata/registry/file/1"
```

Response:
```json
{
  "success": true,
  "file": {
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
}
```

## Understanding the Fields

| Field | Meaning |
|-------|---------|
| `filename` | Original CSV file name |
| `file_type` | Type: csv, excel, json, etc. |
| `dynamic_table_name` | PostgreSQL table where data is stored |
| `data_category` | Type of data (Financial, Sales, Customer, etc.) - determined by AI |
| `row_count` | Number of data rows in file |
| `column_count` | Number of columns |
| `is_described` | ✅ true = user verified metadata, ❌ false = waiting for review |
| `upload_date` | When file was uploaded |
| `verified_at` | When user verified/processed the file |
| `table_created_at` | When the dynamic table was created |

## Example: Sales Data Workflow

```
1. Upload sales_2024.csv
   ↓ file_registry entry created:
     - is_described = false
     - dynamic_table_name = NULL
   
2. User reviews preview & saves column descriptions
   
3. Process file
   ↓ LLM analysis:
     - Detects category: "Sales"
     - Creates schema for sales metrics
   ↓ Dynamic table "sales_2024_1" created
   ↓ file_registry updated:
     - dynamic_table_name = "sales_2024_1"
     - data_category = "Sales"
     - is_described = true
     - table_created_at = timestamp
   
4. Query registry:
   curl "http://localhost:8001/api/v1/metadata/registry/category/Sales"
   → Returns all sales files including this one
```

## SQL Queries (Direct Database)

### Summary Statistics

```sql
SELECT 
  COUNT(*) as total_files,
  SUM(CASE WHEN is_described THEN 1 ELSE 0 END) as verified,
  SUM(CASE WHEN dynamic_table_name IS NOT NULL THEN 1 ELSE 0 END) as with_tables
FROM file_registry;
```

### Find All Financial Files

```sql
SELECT filename, dynamic_table_name, is_described, upload_date
FROM file_registry
WHERE data_category = 'Financial'
ORDER BY upload_date DESC;
```

### Find Unverified Files

```sql
SELECT filename, row_count, column_count, upload_date
FROM file_registry
WHERE is_described = false
ORDER BY upload_date DESC;
```

### Files Ready to Use (Verified + Tables Created)

```sql
SELECT filename, dynamic_table_name, row_count, data_category
FROM file_registry
WHERE is_described = true AND dynamic_table_name IS NOT NULL
ORDER BY verified_at DESC;
```

## Automatic Behavior

### File Upload
- Registry entry created automatically
- `is_described = false` by default
- No manual registration needed

### File Processing
- After dynamic table created
- Registry automatically updated with:
  - Table name
  - Data category (from LLM)
  - Verification timestamp
  - `is_described = true`

## Important Notes

✅ **All automatic** - No manual database updates needed
✅ **Backward compatible** - All existing endpoints still work
✅ **Non-blocking** - If registry fails, upload still succeeds (logged as warning)
✅ **Indexed** - Fast queries on is_described, category, upload_date
✅ **Audit trail** - Complete history via timestamps

## Troubleshooting

### Registry table doesn't exist
```bash
# Create it:
psql -U your_user -d your_db -f migrations_file_registry.sql
```

### File uploaded but not in registry
```bash
# Check logs - should show warning if registration failed
# Try uploading again
```

### Registry not updating after processing
```bash
# Check if processing succeeded (check knowledge_base table)
# Check logs for errors in FileRegistryRepository
```

## Next Steps

1. ✅ Run migration to create table
2. ✅ Upload a CSV file
3. ✅ Process it
4. ✅ Check `/api/v1/metadata/registry/summary`
5. ✅ Use new endpoints to track files

---

**For complete documentation**: See `FILE_REGISTRY_IMPLEMENTATION.md`
