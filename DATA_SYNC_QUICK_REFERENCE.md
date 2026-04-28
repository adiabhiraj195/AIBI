# Data Sync Quick Reference Card

## 🚀 Getting Started (5 Minutes)

### Step 1: Run Migration
```bash
cd /Users/abhi/Documents/Nspark/Suzlon_Copilot_Main_Brain
python run_migration.py
```

### Step 2: Start Service
```bash
python main.py
```

### Step 3: Verify
```bash
curl http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state.status'
# Should output: "healthy"
```

**That's it!** Your sync system is running. 🎉

---

## 📊 API Quick Commands

### Check Sync Health
```bash
curl http://localhost:8000/api/v1/admin/sync/status | jq .
```

### See What's Pending
```bash
curl http://localhost:8000/api/v1/admin/sync/pending | jq .
```

### Manually Trigger Sync
```bash
curl -X POST http://localhost:8000/api/v1/admin/sync/trigger | jq .
```

### Check Sync State Only
```bash
curl http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state'
```

### Check Statistics Only
```bash
curl http://localhost:8000/api/v1/admin/sync/status | jq '.statistics'
```

### Count Pending Documents
```bash
curl http://localhost:8000/api/v1/admin/sync/pending | jq '.count'
```

---

## 🔍 Troubleshooting (Quick Answers)

### Q: Documents not syncing?
```bash
# 1. Check status
curl http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state.status'

# 2. Check error
curl http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state.error_message'

# 3. Trigger manually
curl -X POST http://localhost:8000/api/v1/admin/sync/trigger

# 4. View logs
tail -50 logs/suzlon-copilot-main-brain.log | grep -i sync
```

### Q: Service not starting?
```bash
# Check database connection
python -c "from database.connection import db_manager; print('OK')"

# Check if migration was run
psql -h localhost -d suzlon_copilot -c "\dt data_sync_state"

# If missing, run migration again
python run_migration.py
```

### Q: High CPU/Memory usage?
```bash
# Increase sync interval (less frequent checks)
# Edit: services/data_sync_manager.py
self.sync_interval = 600  # 5 min → 10 min

# Decrease batch size (process fewer docs)
# Edit: services/data_sync_manager.py
self.batch_size = 20  # 50 → 20

# Restart service
python main.py
```

### Q: Want faster syncing?
```bash
# Decrease sync interval
# Edit: services/data_sync_manager.py
self.sync_interval = 60  # 5 min → 1 min

# Increase batch size
# Edit: services/data_sync_manager.py
self.batch_size = 100  # 50 → 100

# Restart service
```

---

## 📁 File Locations

### Core Implementation Files
- **Service**: `Suzlon_Copilot_Main_Brain/services/data_sync_manager.py`
- **Integration**: `Suzlon_Copilot_Main_Brain/main.py` (lines ~1-70)
- **Migration**: `Suzlon_Copilot_Main_Brain/run_migration.py`

### Documentation Files
- **Full Guide**: `DATA_SYNC_IMPLEMENTATION_GUIDE.md`
- **Architecture**: `DATA_SYNC_ARCHITECTURE_DETAILS.md`
- **Summary**: `DATA_SYNC_IMPLEMENTATION_SUMMARY.md`
- **Deployment**: `DEPLOYMENT_CHECKLIST_DATA_SYNC.md`
- **Quick Start**: `QUICK_START_DATA_SYNC.sh` (executable)

### Test Files
- **Test Suite**: `Suzlon_Copilot_Main_Brain/test_data_sync.py`
- **Database Migration**: `Suzlon_Copilot_Main_Brain/migration_data_sync.sh` (executable)

---

## 🔧 Configuration Defaults

| Setting | Default | Location | How to Change |
|---------|---------|----------|---------------|
| Sync Interval | 300s (5 min) | `services/data_sync_manager.py` line 20 | `self.sync_interval = X` |
| Batch Size | 50 docs | `services/data_sync_manager.py` line 21 | `self.batch_size = X` |
| Service Name | "suzlon-copilot-main-brain" | `services/data_sync_manager.py` line 22 | `self.service_name = "X"` |
| Database | From `.env` | `config.py` | Update `.env` file |

---

## 📈 What's Happening Behind the Scenes

```
Timeline: CSV Upload → RAG Ready
═════════════════════════════════════════════════════

T=0s:    You upload CSV to backend
         └─ Stored in database, is_processed_by_rag = FALSE

T=0-300s: DataSyncManager waits (background task)

T=300s:  ⏰ Sync check triggered
         └─ Query: "Find all unprocessed documents"
         └─ Found your CSV!

T=300+:  Process your document
         └─ Calculate hash (to detect changes later)
         └─ UPDATE csv_documents:
            - is_processed_by_rag = TRUE
            - rag_processed_at = now()

T=301s:  ✅ RAG system detects it's ready
         └─ Generates embeddings
         └─ Updates indexes
         └─ ML models have access!

T=600s:  Next sync check (cycle repeats for any new uploads)
```

---

## 📊 Monitoring Dashboard

Copy this to check system health:

```bash
# All-in-one health check
echo "=== Sync Status ===" && \
curl -s http://localhost:8000/api/v1/admin/sync/status | jq '.sync_state' && \
echo "=== Documents ===" && \
curl -s http://localhost:8000/api/v1/admin/sync/status | jq '.statistics' && \
echo "=== Pending ===" && \
curl -s http://localhost:8000/api/v1/admin/sync/pending | jq '.count'
```

Or create a monitor script:
```bash
#!/bin/bash
while true; do
  clear
  echo "=== Suzlon Data Sync Monitor ==="
  curl -s http://localhost:8000/api/v1/admin/sync/status | jq '.statistics'
  sleep 5
done
```

---

## 🚨 Emergency Commands

### Force Immediate Sync
```bash
curl -X POST http://localhost:8000/api/v1/admin/sync/trigger
```

### Check if Service is Running
```bash
curl http://localhost:8000/health | jq '.status'
# Should return: "healthy"
```

### View Real-time Logs
```bash
tail -f logs/suzlon-copilot-main-brain.log | grep -E "🔄|✅|❌"
```

### Database Health Check
```bash
psql -h localhost -d suzlon_copilot -c "
  SELECT 
    (SELECT COUNT(*) FROM csv_documents) as total_docs,
    (SELECT COUNT(*) FROM csv_documents WHERE is_processed_by_rag) as processed,
    (SELECT COUNT(*) FROM data_sync_state) as sync_entries;"
```

---

## 📚 Documentation Map

| Need | File | Time |
|------|------|------|
| **Quick Start** | `QUICK_START_DATA_SYNC.sh` | 5 min |
| **Implementation** | `DATA_SYNC_IMPLEMENTATION_GUIDE.md` | 20 min |
| **Architecture** | `DATA_SYNC_ARCHITECTURE_DETAILS.md` | 15 min |
| **Deployment** | `DEPLOYMENT_CHECKLIST_DATA_SYNC.md` | 30 min |
| **Summary** | `DATA_SYNC_IMPLEMENTATION_SUMMARY.md` | 10 min |
| **This Card** | `DATA_SYNC_QUICK_REFERENCE.md` | 2 min |

---

## ✅ Verification Checklist

- [ ] Migration completed: `python run_migration.py`
- [ ] Service running: `curl http://localhost:8000/health`
- [ ] Sync healthy: `curl .../sync/status | grep healthy`
- [ ] Upload test CSV
- [ ] Check pending: `curl .../sync/pending`
- [ ] Wait 5 minutes or trigger: `curl -X POST .../sync/trigger`
- [ ] Verify processed: pending count = 0

---

## 🎯 Success Indicators

✅ **All Good If**:
- Sync status is "healthy"
- No pending documents after 5 minutes
- No error messages in logs
- New uploads automatically detected
- API endpoints respond with valid JSON

⚠️ **Check If**:
- Sync status is "error"
- Documents stuck in pending
- Error messages in logs
- High CPU/memory usage

---

## 🔗 Related Services

| Service | Port | Health | Docs |
|---------|------|--------|------|
| Main Brain (Sync) | 8000 | `/health` | Main docs |
| Backend (Upload) | 8001 | `/health` | Backend README |
| PostgreSQL | 5432 | Native | Schema docs |

---

## 💡 Pro Tips

1. **Batch Upload Testing**
   ```bash
   for file in *.csv; do
     curl -X POST http://localhost:8001/api/v1/csv/upload \
       -F "file=@$file" -F "filename=$file"
   done
   ```

2. **Monitor in Real-time**
   ```bash
   watch -n 5 'curl -s http://localhost:8000/api/v1/admin/sync/status | jq ".statistics"'
   ```

3. **Log Analysis**
   ```bash
   grep "Documents processed" logs/suzlon-copilot-main-brain.log | tail -10
   ```

4. **Database Cleanup** (if needed)
   ```bash
   psql -h localhost -d suzlon_copilot -c "
     DELETE FROM csv_documents WHERE created_at < NOW() - INTERVAL '30 days';"
   ```

---

## 📞 Support Resources

- **Issues?** Check `DATA_SYNC_IMPLEMENTATION_GUIDE.md` - Troubleshooting section
- **Configuration?** See `DATA_SYNC_ARCHITECTURE_DETAILS.md` - Configuration section
- **Deployment?** Follow `DEPLOYMENT_CHECKLIST_DATA_SYNC.md`
- **Error?** Check logs: `tail -100 logs/suzlon-copilot-main-brain.log`

---

**Keep this card handy for daily operations!** 📌
