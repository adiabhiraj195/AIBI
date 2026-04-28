# Troubleshooting Guide 🔧

Quick solutions to common issues when running AIBI services.

---

## ✅ Initial Setup Issues

### Issue: `.env` file not found

**Error:**
```
ERROR: .env file not found
```

**Solution:**
```bash
cd /Users/abhi/Documents/Nspark
cp .env.example .env
# Edit .env with your credentials
nano .env
```

---

### Issue: Docker not running

**Error:**
```
Cannot connect to Docker daemon
```

**Solution:**
```bash
# macOS
open /Applications/Docker.app

# Then try again
docker ps
```

---

### Issue: Port already in use

**Error:**
```
Address already in use: 0.0.0.0:8000
```

**Solution:**
```bash
# Find which process is using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change the port in docker-compose.yml
# From: "8000:8000"
# To:   "8002:8000"
```

---

## 🔌 Database Connection Issues

### Issue: Backend can't connect to database

**Error:**
```
ConnectionRefusedError: connect() failed: [Errno 61] Connection refused
```

**Symptoms:**
- Backend service keeps restarting
- Logs show "Failed to connect to database"
- `docker compose ps` shows database is unhealthy

**Solutions:**

1. **Check database is running:**
```bash
docker compose ps database
# Should show "Up" and "(healthy)"
```

2. **Check database logs:**
```bash
docker compose logs database
```

3. **Reset database:**
```bash
docker compose down -v
docker compose up --build
```

4. **Verify .env variables:**
```bash
# Check DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
cat .env | grep DB_
```

5. **Test connection from host:**
```bash
# From your Mac (requires psql installed)
psql -h localhost -U AIBI_user -d AIBI_Backend

# If psql not installed, use Docker:
docker compose exec database psql -U AIBI_user -d AIBI_Backend
```

---

### Issue: Both backends connect to different databases

**Symptom:**
- One backend has data, other doesn't
- Tables missing in one database

**Solution:**
```bash
# Verify both use same DB_NAME
docker compose exec backend-csv env | grep DB_NAME
docker compose exec backend-brain env | grep DB_NAME

# Both should output: DB_NAME=AIBI_Backend
```

---

## 🎨 Frontend Issues

### Issue: Frontend can't reach backend API

**Error in browser console:**
```
Failed to fetch http://localhost:8000/api/...
```

**Solutions:**

1. **Verify backend is running:**
```bash
curl http://localhost:8000/docs
# Should return HTML (API docs page)
```

2. **Check frontend .env:**
```bash
# VITE_API_URL should point to backend
cat AIBI_Copilot_Frontend/.env | grep VITE_API_URL
```

3. **Clear browser cache:**
- Open DevTools → Application → Storage
- Clear all cache/cookies
- Refresh page

4. **Check CORS:**
```bash
# Backend should allow CORS from frontend origin
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     http://localhost:8000/api/
```

---

### Issue: Frontend builds but shows blank page

**Symptoms:**
- Blank white page
- No errors in console
- Network requests successful

**Solutions:**

1. **Check build output:**
```bash
docker compose logs frontend | tail -50
```

2. **Rebuild frontend:**
```bash
docker compose up --build --no-cache frontend
```

3. **Clear Docker cache:**
```bash
docker system prune
docker compose up --build --no-cache
```

---

## 🧠 Backend Brain (RAG) Issues

### Issue: LLM API calls failing

**Error:**
```
LLMError: Failed to generate response
```

**Solutions:**

1. **Verify API key:**
```bash
# Check LLM_API_KEY is set
docker compose exec backend-brain env | grep LLM_API_KEY
```

2. **Test API directly:**
```bash
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}]}'
```

3. **Check API usage/limits:**
- Log into your LLM provider dashboard
- Verify API key is active
- Check usage quota

---

### Issue: Redis connection errors

**Error:**
```
ConnectionError: Error -1 connecting to redis:6379
```

**Solutions:**

1. **Check Redis is running:**
```bash
docker compose logs redis
```

2. **Test Redis connection:**
```bash
docker compose exec redis redis-cli ping
# Should output: PONG
```

3. **Restart Redis:**
```bash
docker compose restart redis
```

---

### Issue: Vector embeddings not working

**Error:**
```
pgvector extension not found
```

**Solutions:**

1. **Check pgvector is installed:**
```bash
docker compose exec database psql -U AIBI_user -d AIBI_Backend \
  -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

2. **Install pgvector extension:**
```bash
docker compose exec database psql -U AIBI_user -d AIBI_Backend \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

3. **Reset database with proper schema:**
```bash
docker compose down -v
# Ensure database_schema.sql includes vector extension
docker compose up --build
```

---

## 📄 CSV API Issues

### Issue: File upload fails

**Error:**
```
413 Payload Too Large
```

**Solutions:**

1. **Check file size:**
```bash
# Max size is 200MB (set in .env)
ls -lh your_file.csv

# Increase limit if needed:
# MAX_FILE_SIZE=209715200  # bytes
```

2. **Check allowed extensions:**
```bash
# Only .csv allowed
# Verify in .env: ALLOWED_EXTENSIONS=.csv
```

3. **Test upload manually:**
```bash
curl -X POST http://localhost:8001/api/files/upload \
  -F "file=@test.csv" \
  -F "name=Test CSV"
```

---

### Issue: Supabase connection errors

**Error:**
```
ConnectionError: Could not reach Supabase
```

**Solutions:**

1. **Verify Supabase credentials:**
```bash
cat .env | grep SUPABASE
# Should have SUPABASE_URL and SUPABASE_SERVICE_KEY
```

2. **Test Supabase connection:**
```bash
# Use Supabase CLI or test endpoint
curl https://your-project.supabase.co/rest/v1/
  -H "Authorization: Bearer YOUR_SERVICE_KEY"
```

3. **If not using Supabase:**
- Leave SUPABASE_* variables empty
- CSV API will use PostgreSQL directly

---

## 🔄 Restart & Reset Procedures

### Restart single service
```bash
docker compose restart backend-brain
docker compose restart backend-csv
docker compose restart frontend
docker compose restart database
docker compose restart redis
```

### Restart all services
```bash
docker compose down
docker compose up --build
```

### Full reset (delete all data)
```bash
docker compose down -v
# This removes:
# - All containers
# - All volumes (database and Redis data)
# - All networks

docker compose up --build
# Rebuilds from scratch
```

### Partial reset (keep database)
```bash
docker compose down
# Database volume persists
docker compose up --build
```

---

## 📊 Monitoring & Debugging

### Check all container health
```bash
docker compose ps
```

Expected output:
```
NAME                 STATUS           HEALTH
AIBI-database      Up               (healthy)
AIBI-redis         Up               (healthy)
AIBI-backend-csv   Up 2m            (healthy)
AIBI-backend-brain Up 2m            (healthy)
AIBI-frontend      Up 1m            (healthy)
```

### View real-time logs
```bash
# All services
docker compose logs -f

# Specific service with timestamps
docker compose logs -f -t backend-brain

# Last 100 lines
docker compose logs --tail=100 backend-csv
```

### Check resource usage
```bash
docker stats
# Shows CPU, memory, network usage
```

### Access service databases

**PostgreSQL:**
```bash
docker compose exec database psql -U AIBI_user -d AIBI_Backend
```

**Redis:**
```bash
docker compose exec redis redis-cli
> KEYS *              # List all keys
> GET key_name        # Get value
> FLUSHDB             # Clear database
```

---

## 🧪 API Testing

### Health checks
```bash
# Frontend
curl http://localhost:3000

# Backend A (CSV)
curl http://localhost:8001/docs

# Backend B (Brain)
curl http://localhost:8000/docs

# Database
docker compose exec database pg_isready -U AIBI_user

# Redis
docker compose exec redis redis-cli PING
```

### Test Main Brain endpoint
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is your status?"}'
```

### Test CSV upload
```bash
curl -X POST http://localhost:8001/api/files/upload \
  -F "file=@sample.csv" \
  -F "name=Sample Data"
```

---

## 💾 Database Backup & Recovery

### Backup database
```bash
docker compose exec database pg_dump \
  -U AIBI_user \
  AIBI_Backend > backup.sql
```

### Restore database
```bash
docker compose exec -T database psql \
  -U AIBI_user \
  AIBI_Backend < backup.sql
```

### Check database size
```bash
docker compose exec database psql \
  -U AIBI_user \
  -d AIBI_Backend \
  -c "SELECT pg_size_pretty(pg_database_size('AIBI_Backend'))"
```

---

## 🚨 Still Having Issues?

### Collect debug information
```bash
# Create debug log
./dev.sh status > debug.log
./dev.sh logs >> debug.log
docker compose ps >> debug.log
docker stats --no-stream >> debug.log
```

### Check individual logs
```bash
# Database errors
docker compose logs database | grep -i error

# Backend errors
docker compose logs backend-brain | grep -i error
docker compose logs backend-csv | grep -i error

# Frontend errors
docker compose logs frontend | grep -i error
```

### Common fixes (in order)
1. Restart services: `docker compose restart`
2. Reset all: `docker compose down -v && docker compose up --build`
3. Update .env with correct credentials
4. Check Docker resource limits
5. Update Docker Desktop to latest version

---

**Need more help?** Check the main README.md or individual service READMEs.
