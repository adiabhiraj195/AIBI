# Data Sync Implementation Guide

## Overview

This implementation enables automatic synchronization of CSV files uploaded to the Suzlon Backend with the RAG system in Suzlon_Copilot_Main_Brain. Your ML models are now **always aware of new data** uploaded into the shared database.

## How It Works

```
┌─────────────────────────────┐
│   Suzlon_backend            │
│  (CSV File Upload)          │
└──────────────┬──────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Shared PostgreSQL   │
    │  csv_documents table │
    └──────────┬───────────┘
               │
               │ Polls every 5 minutes
               │
    ┌──────────▼───────────┐
    │ DataSyncManager      │
    │ (Main Brain Service) │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ RAG System Ready     │
    │ with New Embeddings  │
    └──────────────────────┘
```

## 1. Database Migration

### Option A: Using Python Script (Recommended)

```bash
cd /Users/abhi/Documents/Nspark/Suzlon_Copilot_Main_Brain

# Run migration
python run_migration.py
```

### Option B: Using Bash Script

```bash
chmod +x migration_data_sync.sh

# Set environment variables (if needed)
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=suzlon_copilot
export DB_USER=postgres

# Run migration
./migration_data_sync.sh
```

### Option C: Manual SQL

```bash
psql -h localhost -p 5432 -U postgres -d suzlon_copilot << 'EOF'

-- 1. Create data_sync_state table
CREATE TABLE IF NOT EXISTS data_sync_state (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL UNIQUE,
    last_sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_document_id BIGINT DEFAULT 0,
    total_documents_synced BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'healthy',
    error_message TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create index
CREATE INDEX IF NOT EXISTS idx_sync_state_service ON data_sync_state(service_name);

-- 3. Add columns to csv_documents
ALTER TABLE csv_documents
ADD COLUMN IF NOT EXISTS is_processed_by_rag BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS rag_processed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS embedding_version INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS data_hash VARCHAR(64);

-- 4. Create indexes
CREATE INDEX IF NOT EXISTS idx_csv_documents_processed 
ON csv_documents(is_processed_by_rag, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_csv_documents_hash 
ON csv_documents(data_hash);

-- 5. Initialize sync state
INSERT INTO data_sync_state (service_name, status) 
VALUES ('suzlon-copilot-main-brain', 'healthy')
ON CONFLICT (service_name) DO NOTHING;

EOF
```

## 2. What Was Implemented

### New Service: DataSyncManager
- **File**: `services/data_sync_manager.py`
- **Function**: Continuously monitors for new CSV files uploaded to the backend
- **Interval**: Checks every 5 minutes (configurable)
- **Batch Size**: Processes 50 documents at a time
- **Features**:
  - Automatic background sync
  - Change detection using data hashing
  - Error recovery with automatic retries
  - Comprehensive logging

### Updated Application Startup
- **File**: `main.py`
- **Changes**: 
  - Initializes DataSyncManager on startup
  - Gracefully shuts down on application close
  - Integrated into application lifespan

### New API Endpoints
All endpoints are protected and for admin/monitoring use:

#### 1. **Trigger Manual Sync**
```bash
POST /api/v1/admin/sync/trigger
```
Response:
```json
{
  "success": true,
  "message": "Manual sync triggered",
  "result": {
    "status": "success",
    "documents_processed": 5,
    "documents_failed": 0,
    "timestamp": "2024-01-10T10:30:45.123456"
  }
}
```

#### 2. **Get Sync Status**
```bash
GET /api/v1/admin/sync/status
```
Response:
```json
{
  "sync_state": {
    "service_name": "suzlon-copilot-main-brain",
    "status": "healthy",
    "last_sync_timestamp": "2024-01-10T10:30:45.123456",
    "error_message": null,
    "updated_at": "2024-01-10T10:30:45.123456"
  },
  "statistics": {
    "total_documents": 25,
    "processed_documents": 25,
    "pending_documents": 0,
    "latest_upload": "2024-01-10T09:15:00.000000",
    "latest_processed": "2024-01-10T10:30:00.000000"
  },
  "sync_health": "healthy"
}
```

#### 3. **Get Pending Documents**
```bash
GET /api/v1/admin/sync/pending?limit=20
```
Response:
```json
{
  "count": 3,
  "pending_documents": [
    {
      "id": 101,
      "filename": "sales_data.csv",
      "created_at": "2024-01-10T10:35:00",
      "row_count": 1500,
      "column_count": 8,
      "status": "pending"
    }
  ]
}
```

## 3. Database Schema Changes

### New Table: `data_sync_state`
Tracks synchronization status between backend and main brain:

| Column | Type | Purpose |
|--------|------|---------|
| `id` | SERIAL | Primary key |
| `service_name` | VARCHAR(50) | Service identifier (e.g., "suzlon-copilot-main-brain") |
| `last_sync_timestamp` | TIMESTAMP | When the last sync occurred |
| `last_synced_document_id` | BIGINT | Last document ID processed |
| `total_documents_synced` | BIGINT | Cumulative documents processed |
| `status` | VARCHAR(20) | healthy, syncing, error |
| `error_message` | TEXT | Last error message if failed |
| `updated_at` | TIMESTAMP | Last state update time |

### Updated Table: `csv_documents`
Added columns for RAG processing tracking:

| Column | Type | Purpose |
|--------|------|---------|
| `is_processed_by_rag` | BOOLEAN | Whether document is ready for RAG |
| `rag_processed_at` | TIMESTAMP | When RAG processing completed |
| `embedding_version` | INT | Version of embeddings used |
| `data_hash` | VARCHAR(64) | SHA256 hash for change detection |

### Optional Table: `sync_history`
Audit trail for all sync operations (future enhancement):

| Column | Type | Purpose |
|--------|------|---------|
| `id` | SERIAL | Primary key |
| `service_name` | VARCHAR(50) | Which service performed sync |
| `documents_processed` | INT | Count of successfully processed docs |
| `documents_failed` | INT | Count of failed docs |
| `sync_start_time` | TIMESTAMP | When sync started |
| `sync_end_time` | TIMESTAMP | When sync completed |
| `duration_seconds` | INT | Total duration |
| `status` | VARCHAR(20) | success, partial, failed |
| `error_message` | TEXT | Error details if failed |
| `created_at` | TIMESTAMP | Record creation time |

## 4. Starting the Services

### Start Everything
```bash
cd /Users/abhi/Documents/Nspark

# Using docker-compose (if available)
docker-compose up

# Or start manually
cd Suzlon_backend && python main.py &
cd ../Suzlon_Copilot_Main_Brain && python main.py &
```

### Verify Sync Manager is Running
```bash
# Check logs for sync initialization
tail -f logs/suzlon-copilot-main-brain.log | grep -i "sync\|data"

# Check sync status
curl http://localhost:8000/api/v1/admin/sync/status | jq .
```

## 5. Testing the Data Sync

### Test 1: Upload a CSV and Verify Automatic Sync

```bash
# 1. Upload a CSV file via Suzlon_backend
curl -X POST http://localhost:8001/api/v1/csv/upload \
  -F "file=@test_data.csv" \
  -F "filename=test_data.csv"

# Wait 5-10 seconds (default sync interval is 5 minutes, but can trigger manually)

# 2. Check sync status
curl http://localhost:8000/api/v1/admin/sync/status | jq '.statistics'

# Expected output shows pending_documents decreasing
{
  "total_documents": 1,
  "processed_documents": 1,
  "pending_documents": 0,
  "latest_upload": "2024-01-10T10:35:00",
  "latest_processed": "2024-01-10T10:35:02"
}
```

### Test 2: Trigger Manual Sync
```bash
# Manually trigger sync (useful for testing)
curl -X POST http://localhost:8000/api/v1/admin/sync/trigger | jq .

# Response shows documents processed
{
  "success": true,
  "message": "Manual sync triggered",
  "result": {
    "status": "success",
    "documents_processed": 3,
    "documents_failed": 0,
    "timestamp": "2024-01-10T10:40:12.123456"
  }
}
```

### Test 3: Monitor Pending Documents
```bash
# See which documents are waiting to be synced
curl http://localhost:8000/api/v1/admin/sync/pending?limit=10 | jq .

# Shows details of pending documents
{
  "count": 2,
  "pending_documents": [
    {
      "id": 105,
      "filename": "inventory.csv",
      "created_at": "2024-01-10T11:00:00",
      "row_count": 2000,
      "column_count": 12,
      "status": "pending"
    }
  ]
}
```

## 6. Configuration

### Adjust Sync Interval
Edit `services/data_sync_manager.py`:

```python
def __init__(self):
    self.sync_interval = 300  # Change to your preferred interval in seconds
    # 60 = 1 minute
    # 300 = 5 minutes (default)
    # 600 = 10 minutes
    # 3600 = 1 hour
```

### Adjust Batch Size
Edit `services/data_sync_manager.py`:

```python
def __init__(self):
    self.batch_size = 50  # Change to process more/fewer documents per sync
```

## 7. Monitoring

### Check Sync Logs
```bash
# View recent sync activity
tail -100 logs/suzlon-copilot-main-brain.log | grep -i "sync\|processing"

# Watch real-time sync
tail -f logs/suzlon-copilot-main-brain.log | grep -E "🔄|✅|❌"
```

### Database Monitoring
```bash
# Check sync state in database
psql -h localhost -d suzlon_copilot -c "SELECT * FROM data_sync_state;"

# Check processed documents
psql -h localhost -d suzlon_copilot -c "
  SELECT filename, is_processed_by_rag, created_at, rag_processed_at 
  FROM csv_documents 
  ORDER BY created_at DESC LIMIT 5;"

# Check pending documents count
psql -h localhost -d suzlon_copilot -c "
  SELECT COUNT(*) as pending 
  FROM csv_documents 
  WHERE is_processed_by_rag = FALSE;"
```

## 8. Troubleshooting

### Issue: Documents not being synced
```bash
# 1. Check sync status
curl http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state.status'

# 2. If status is "error", check the error message
curl http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state.error_message'

# 3. Trigger manual sync
curl -X POST http://localhost:8000/api/v1/admin/sync/trigger

# 4. Check logs
tail -50 logs/suzlon-copilot-main-brain.log
```

### Issue: Sync Manager not starting
```bash
# Check if service initialized properly
grep "Data Sync Manager" logs/suzlon-copilot-main-brain.log

# Verify database connection
python -c "from database.connection import db_manager; print('DB OK')"

# Check if sync table exists
psql -h localhost -d suzlon_copilot -c "\dt data_sync_state"
```

### Issue: High database load
```bash
# 1. Increase sync interval (less frequent checks)
# Edit services/data_sync_manager.py: self.sync_interval = 600  # 10 minutes

# 2. Decrease batch size (process fewer docs per sync)
# Edit services/data_sync_manager.py: self.batch_size = 20

# 3. Restart service
```

## 9. Performance Considerations

| Metric | Default | Recommendation |
|--------|---------|-----------------|
| **Sync Interval** | 5 minutes | Adjust based on upload frequency |
| **Batch Size** | 50 documents | Increase if documents are small |
| **Retry Delay** | 10 minutes | Double the interval on failure |
| **Database Connections** | 2-10 pool | Increase if many sync ops needed |

## 10. Next Steps

1. ✅ **Run migration script** - Create database schema
2. ✅ **Restart Main Brain service** - Initialize sync manager
3. ✅ **Verify sync status** - Check API endpoint
4. ✅ **Test with file upload** - Verify end-to-end flow
5. ⭐ **Monitor logs** - Watch for any issues
6. 📊 **Setup alerts** - Notify on sync failures (future)
7. 🔄 **Tune settings** - Optimize for your workload

## 11. Endpoints Summary

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/health` | GET | Basic health check | Always available |
| `/api/v1/admin/sync/status` | GET | Get current sync status | Check `pending_documents` |
| `/api/v1/admin/sync/trigger` | POST | Manually start sync | Useful for testing |
| `/api/v1/admin/sync/pending` | GET | List pending documents | See what needs processing |

---

**Your ML models are now automatically aware of new data uploads!** 🚀
