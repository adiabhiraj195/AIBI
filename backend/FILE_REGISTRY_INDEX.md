# 📚 File Registry System - Documentation Index

## Quick Navigation

### 🚀 Getting Started
- **[FILE_REGISTRY_QUICK_START.md](FILE_REGISTRY_QUICK_START.md)** ⭐
  - One-page guide to use the feature
  - API endpoints with examples
  - Common queries and workflows
  - **Start here if you just want to use it**

### 📖 Complete Documentation
- **[FILE_REGISTRY_IMPLEMENTATION.md](FILE_REGISTRY_IMPLEMENTATION.md)**
  - Full system specification
  - Database tables explained
  - API endpoints with response examples
  - Flow diagrams
  - Testing instructions
  - **Start here for technical details**

### 💻 Implementation Details
- **[IMPLEMENTATION_SUMMARY_FILE_REGISTRY.md](IMPLEMENTATION_SUMMARY_FILE_REGISTRY.md)**
  - What was implemented
  - Code components overview
  - Files modified/created
  - How it works
  - **Start here to understand code changes**

### 🎯 System Overview
- **[COMPLETE_SYSTEM_SUMMARY.md](COMPLETE_SYSTEM_SUMMARY.md)**
  - High-level feature summary
  - End-to-end flow
  - Data flow diagrams
  - Setup instructions
  - **Start here for big picture**

---

## Feature Summary

**What it does:**
- ✅ Registers CSV files on upload
- ✅ Processes them with AI (LLM)
- ✅ Creates dynamic PostgreSQL tables with all data
- ✅ Tracks verification status (is_described flag)
- ✅ Provides central registry for tracking all files
- ✅ Enables filtering by category
- ✅ Maintains complete audit trail

---

## Files Added/Modified

### New Files Created (4)
1. `app/repositories/file_registry_repository.py` - Registry operations
2. `migrations_file_registry.sql` - Database migration
3. `test_file_registry.py` - Test script
4. Documentation files (4 markdown files)

### Files Modified (4)
1. `app/models/database_models.py` - Added FileRegistry ORM model
2. `app/repositories/csv_repository.py` - Auto-register on upload
3. `app/services/metadata_service.py` - Update registry after processing
4. `app/controllers/metadata_controller.py` - 4 new API endpoints

---

## Quick Command Reference

### Setup
```bash
# Create registry table
psql -U user -d db -f migrations_file_registry.sql

# Or automatic
python3 -c "from app.database.connection import DatabaseConnection; DatabaseConnection.init_db()"
```

### Test
```bash
python3 test_file_registry.py
```

### API Examples

**Get Statistics**
```bash
curl "http://localhost:8001/api/v1/metadata/registry/summary"
```

**List All Files**
```bash
curl "http://localhost:8001/api/v1/metadata/registry/files"
```

**Find Unverified**
```bash
curl "http://localhost:8001/api/v1/metadata/registry/files?verified_only=false"
```

**Filter by Category**
```bash
curl "http://localhost:8001/api/v1/metadata/registry/category/Financial"
```

**Get Specific File**
```bash
curl "http://localhost:8001/api/v1/metadata/registry/file/1"
```

---

## Database Overview

### FileRegistry Table
| Field | Type | Purpose |
|-------|------|---------|
| `id` | INTEGER | Primary key |
| `document_id` | INTEGER | FK to csv_documents |
| `filename` | VARCHAR(255) | File name (indexed) |
| `file_type` | VARCHAR(50) | csv, excel, json, etc. |
| `dynamic_table_name` | VARCHAR(255) | PostgreSQL table name |
| `data_category` | VARCHAR(255) | Category from LLM |
| `row_count` | INTEGER | Number of rows |
| `column_count` | INTEGER | Number of columns |
| `is_described` | BOOLEAN | User verified? (indexed) |
| `verified_at` | TIMESTAMP | When user verified |
| `upload_date` | TIMESTAMP | When uploaded (indexed) |
| `table_created_at` | TIMESTAMP | When table created |

---

## API Endpoints Added

### 4 New Endpoints for Registry

1. **GET** `/api/v1/metadata/registry/summary`
   - Get statistics: total files, verified, with tables
   - Used for dashboard/status page

2. **GET** `/api/v1/metadata/registry/files`
   - List all registered files with full details
   - Query params: limit, offset, verified_only

3. **GET** `/api/v1/metadata/registry/file/{document_id}`
   - Get specific file registry entry
   - Used for file detail page

4. **GET** `/api/v1/metadata/registry/category/{category}`
   - Get files by data category
   - Used for data discovery

---

## How to Use

### 1. Upload File
```bash
curl -X POST "http://localhost:8001/api/v1/csv/upload" \
  -F "file=@data.csv"
```
→ File registered with `is_described = false`

### 2. Save Metadata
```bash
curl -X POST "http://localhost:8001/api/v1/metadata/save/1" \
  -H "Content-Type: application/json" \
  -d '{"columns": [...]}'
```

### 3. Process File
```bash
curl -X POST "http://localhost:8001/api/v1/metadata/process/1"
```
→ Dynamic table created, registry updated

### 4. Track Files
```bash
curl "http://localhost:8001/api/v1/metadata/registry/summary"
```
→ See statistics

---

## File Organization

```
Suzlon_backend/
├── app/
│   ├── models/
│   │   └── database_models.py (MODIFIED - Added FileRegistry)
│   ├── repositories/
│   │   ├── csv_repository.py (MODIFIED - Register on upload)
│   │   └── file_registry_repository.py (NEW)
│   ├── services/
│   │   └── metadata_service.py (MODIFIED - Update registry)
│   └── controllers/
│       └── metadata_controller.py (MODIFIED - New endpoints)
│
├── Documentation/
│   ├── FILE_REGISTRY_QUICK_START.md (NEW)
│   ├── FILE_REGISTRY_IMPLEMENTATION.md (NEW)
│   ├── IMPLEMENTATION_SUMMARY_FILE_REGISTRY.md (NEW)
│   ├── COMPLETE_SYSTEM_SUMMARY.md (NEW)
│   └── FILE_REGISTRY_INDEX.md (this file)
│
├── Database/
│   └── migrations_file_registry.sql (NEW)
│
└── Tests/
    └── test_file_registry.py (NEW)
```

---

## Key Concepts

### is_described Flag
- `true` = User has reviewed metadata and file is processed
- `false` = File uploaded but awaiting user review
- Used to track verification progress

### Data Category
- Determined by LLM during processing
- Examples: Financial, Sales, Customer, Operations
- Enable data organization and discovery

### Dynamic Table Name
- PostgreSQL table created for each file
- Format: `{filename}_{document_id}`
- Stores all CSV rows for querying

### Timestamps
- `upload_date` - When file entered system
- `verified_at` - When user completed review
- `table_created_at` - When dynamic table created
- Complete audit trail

---

## Common Questions

**Q: Does this break existing functionality?**
A: No, 100% backward compatible. All existing endpoints unchanged.

**Q: Is it automatic or manual?**
A: Automatic. Files registered on upload, registry updated after processing.

**Q: What if registry fails?**
A: Upload succeeds. Warning logged. Non-blocking.

**Q: Can I query data across files?**
A: Yes, each file has a dynamic table. Join them as needed.

**Q: How do I filter unverified files?**
A: `GET /registry/files?verified_only=false`

**Q: How do I find all financial data?**
A: `GET /registry/category/Financial`

---

## Next Steps

1. ✅ Read **FILE_REGISTRY_QUICK_START.md** (5 min read)
2. ✅ Run migration to create table
3. ✅ Upload a test CSV
4. ✅ Check `/registry/summary` endpoint
5. ✅ Process file and verify registry updates
6. ✅ Read **FILE_REGISTRY_IMPLEMENTATION.md** for details

---

## Support

For issues or questions:
1. Check the appropriate documentation file above
2. Review test script: `test_file_registry.py`
3. Check server logs for errors
4. Verify table exists: `psql ... -c "SELECT * FROM file_registry;"`

---

**Status**: ✅ Complete and Production Ready
**Date**: January 15, 2026
**Version**: 1.0
