# Data Sync Deployment Checklist

Use this checklist to deploy and verify the data sync system in your environment.

## Pre-Deployment

- [ ] **Backup Database**
  ```bash
  pg_dump AIBI_copilot > backup_$(date +%s).sql
  ```
  - Backup location: `_backups/`
  - Date: _______________

- [ ] **Review Configuration**
  - [ ] Verify DB host in `.env`
  - [ ] Verify DB port in `.env`
  - [ ] Verify DB credentials work
  - [ ] Check sync interval preference (default: 300s)
  - [ ] Check batch size preference (default: 50 docs)

- [ ] **Verify Prerequisites**
  ```bash
  python --version  # Python 3.8+
  pip list | grep asyncpg  # Required
  ```

- [ ] **Git Commit** (if using version control)
  ```bash
  git add -A
  git commit -m "feat: implement data sync system"
  ```

## Database Migration

- [ ] **Method 1: Automated (Python)**
  ```bash
  cd AIBI_Copilot_Main_Brain
  python run_migration.py
  ```
  - Status: _______________
  - Timestamp: _______________

- [ ] **Method 2: Alternative (Bash)** (if needed)
  ```bash
  chmod +x migration_data_sync.sh
  ./migration_data_sync.sh
  ```
  - Status: _______________

- [ ] **Verify Migration**
  ```bash
  psql -h localhost -d AIBI_copilot -c "\dt data_sync_state"
  psql -h localhost -d AIBI_copilot -c "\d csv_documents" | grep is_processed_by_rag
  ```
  - Tables created: _______________
  - Columns added: _______________

## Testing & Verification

- [ ] **Run Test Suite**
  ```bash
  cd AIBI_Copilot_Main_Brain
  python test_data_sync.py
  ```
  - All tests passed: _______________
  - Failed tests: _______________

- [ ] **Start Services**
  - Terminal 1: Backend
    ```bash
    cd AIBI_backend && python main.py
    ```
    - Port: _____ (default: 8001)
    - Status: _______________
  
  - Terminal 2: Main Brain
    ```bash
    cd AIBI_Copilot_Main_Brain && python main.py
    ```
    - Port: _____ (default: 8000)
    - Status: _______________
    - Sync logs visible: _______________

- [ ] **API Health Check**
  ```bash
  curl http://localhost:8000/health | jq .
  ```
  - Status: _______________

- [ ] **Verify Sync Initialization**
  ```bash
  curl http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state.status'
  ```
  - Sync status: _______________
  - Should be: "healthy"

## Functional Testing

- [ ] **Test 1: Upload CSV**
  ```bash
  curl -X POST http://localhost:8001/api/v1/csv/upload \
    -F "file=@test_sample.csv" \
    -F "filename=test_sample.csv"
  ```
  - Upload successful: _______________
  - Response code: _______________

- [ ] **Test 2: Check Pending Documents**
  ```bash
  curl http://localhost:8000/api/v1/admin/sync/pending | jq '.count'
  ```
  - Pending count: _______________
  - Should be: 1 (your new upload)

- [ ] **Test 3: Wait for Auto-Sync**
  - Wait 5-10 minutes (default sync interval)
  - OR manually trigger:
  ```bash
  curl -X POST http://localhost:8000/api/v1/admin/sync/trigger | jq .
  ```
  - Sync triggered: _______________
  - Documents processed: _______________

- [ ] **Test 4: Verify Processing Complete**
  ```bash
  curl http://localhost:8000/api/v1/admin/sync/pending | jq '.count'
  ```
  - Pending count: _______________
  - Should be: 0 (all synced)

- [ ] **Test 5: Check Database State**
  ```bash
  psql -h localhost -d AIBI_copilot -c "
    SELECT filename, is_processed_by_rag, rag_processed_at 
    FROM csv_documents 
    ORDER BY created_at DESC LIMIT 1;"
  ```
  - is_processed_by_rag: _____ (should be true)
  - rag_processed_at: _____ (should have timestamp)

## Multiple Document Testing

- [ ] **Upload 3+ CSV files**
  ```bash
  for i in 1 2 3; do
    curl -X POST http://localhost:8001/api/v1/csv/upload \
      -F "file=@test_sample_${i}.csv" \
      -F "filename=test_sample_${i}.csv"
  done
  ```
  - All uploads successful: _______________

- [ ] **Verify Batch Processing**
  ```bash
  curl http://localhost:8000/api/v1/admin/sync/status | jq '.statistics'
  ```
  - Total documents: _______________
  - Processed documents: _______________
  - Pending documents: _______________

## Monitoring Setup

- [ ] **Log Rotation** (if needed)
  - Log file location: `logs/AIBI-copilot-main-brain.log`
  - Size limit: _______________
  - Retention: _______________

- [ ] **Performance Baseline**
  - First sync time: _______________
  - Average sync time: _______________
  - CPU usage: _______________
  - Memory usage: _______________

- [ ] **Set Up Log Monitoring** (optional)
  ```bash
  tail -f logs/AIBI-copilot-main-brain.log | grep -E "🔄|✅|❌"
  ```
  - Logs being generated: _______________

## Configuration Adjustments (if needed)

- [ ] **Adjust Sync Interval** (if needed)
  - Current: 300 seconds (5 minutes)
  - Preferred: _____ seconds
  - File: `AIBI_Copilot_Main_Brain/services/data_sync_manager.py` (line ~20)
  - Change made: _______________

- [ ] **Adjust Batch Size** (if needed)
  - Current: 50 documents
  - Preferred: _____ documents
  - File: `AIBI_Copilot_Main_Brain/services/data_sync_manager.py` (line ~21)
  - Change made: _______________

- [ ] **Restart Service** (after any changes)
  ```bash
  # Stop and restart Main Brain service
  ```
  - Restart successful: _______________

## Production Checklist

- [ ] **Security Review**
  - [ ] API endpoints are admin-only
  - [ ] Database credentials secured in `.env`
  - [ ] No sensitive data in logs
  - [ ] Firewall rules configured

- [ ] **Error Handling**
  - [ ] Sync failure scenarios tested
  - [ ] Recovery mechanisms verified
  - [ ] Error messages are logged

- [ ] **Documentation**
  - [ ] Team informed about new endpoints
  - [ ] Runbooks updated
  - [ ] Emergency procedures documented

- [ ] **Monitoring & Alerts** (future)
  - [ ] Plan for sync failure alerts
  - [ ] Plan for performance metrics
  - [ ] Plan for audit logging

## Post-Deployment

- [ ] **Verify Continuous Operation**
  - Run for: _____ hours/days
  - Issues encountered: _______________
  - Status: ✅ HEALTHY / ⚠️  NEEDS ATTENTION

- [ ] **Performance Monitoring**
  - Monitor database query performance
  - Monitor service memory usage
  - Check error logs daily

- [ ] **Update Documentation**
  - [ ] README.md updated
  - [ ] Team wiki updated
  - [ ] Deployment guide updated

- [ ] **Schedule Review**
  - Sync working as expected: _______________
  - Any optimizations needed: _______________
  - Review date: _______________

## Rollback Plan (if needed)

If deployment fails, follow these steps:

1. **Stop Services**
   ```bash
   # Stop both services
   ```

2. **Restore Database Backup**
   ```bash
   psql AIBI_copilot < backup_XXXXXXXXX.sql
   ```

3. **Revert Code Changes**
   ```bash
   git revert <commit-hash>
   ```

4. **Restart Services**
   ```bash
   # Restart both services
   ```

- [ ] Rollback completed: _______________
- [ ] Services restored: _______________
- [ ] Data verified: _______________

## Deployment Sign-Off

- **Deployed By**: _______________
- **Deployment Date**: _______________
- **Deployment Time**: _______________
- **Status**: ☐ SUCCESS  ☐ PARTIAL  ☐ FAILED

**Notes**:
```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

## Quick Reference Commands

```bash
# Check sync status
curl http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state'

# See pending documents
curl http://localhost:8000/api/v1/admin/sync/pending | jq .

# Trigger manual sync
curl -X POST http://localhost:8000/api/v1/admin/sync/trigger | jq .

# View logs
tail -f logs/AIBI-copilot-main-brain.log | grep -i sync

# Check database
psql -h localhost -d AIBI_copilot -c "SELECT * FROM data_sync_state;"

# Count processed docs
psql -h localhost -d AIBI_copilot -c "
  SELECT COUNT(CASE WHEN is_processed_by_rag THEN 1 END) FROM csv_documents;"
```

---

**Deployment complete when all items are checked!** ✅
