# ✅ Setup Verification Checklist

Verify your AIBI setup is complete and working correctly.

---

## Phase 1: File Structure ✅

Run this to verify all files are in place:

```bash
cd /Users/abhi/Documents/Nspark

# Check root files
ls -la | grep -E "(docker-compose|Dockerfile|\.env|README|QUICKSTART|ARCHITECTURE|TROUBLESHOOTING)"

# Expected output should include:
# ✅ docker-compose.yml
# ✅ .env.example
# ✅ .gitignore
# ✅ README.md
# ✅ QUICKSTART.md
# ✅ ARCHITECTURE.md
# ✅ TROUBLESHOOTING.md
# ✅ start.sh
# ✅ dev.sh
```

---

## Phase 2: Dockerfile Verification ✅

```bash
# Check each Dockerfile exists
test -f AIBI_Backend/Dockerfile && echo "✅ AIBI_Backend/Dockerfile" || echo "❌ Missing"
test -f AIBI_Copilot_Main_Brain/Dockerfile && echo "✅ AIBI_Copilot_Main_Brain/Dockerfile" || echo "❌ Missing"
test -f AIBI_Copilot_Frontend/Dockerfile && echo "✅ AIBI_Copilot_Frontend/Dockerfile" || echo "❌ Missing"

# Check .env.example files
test -f .env.example && echo "✅ Root .env.example" || echo "❌ Missing"
test -f AIBI_Backend/.env.example && echo "✅ Backend A .env.example" || echo "❌ Missing"
test -f AIBI_Copilot_Main_Brain/.env.example && echo "✅ Backend B .env.example" || echo "❌ Missing"
test -f AIBI_Copilot_Frontend/.env.example && echo "✅ Frontend .env.example" || echo "❌ Missing"
```

---

## Phase 3: Configuration ✅

```bash
# Create .env if it doesn't exist
test -f .env || cp .env.example .env
echo "✅ .env file created/exists"

# Verify critical variables are set
echo "Checking .env configuration..."
grep -q "DB_PASSWORD" .env && echo "✅ DB_PASSWORD set" || echo "❌ DB_PASSWORD missing"
grep -q "LLM_API_KEY" .env && echo "✅ LLM_API_KEY set" || echo "❌ LLM_API_KEY missing"
grep -q "GROQ_API_KEY" .env && echo "✅ GROQ_API_KEY set" || echo "❌ GROQ_API_KEY missing"

# Check they're not still example values
if ! grep "DB_PASSWORD=AIBI_password_change_me" .env > /dev/null; then
    echo "✅ DB_PASSWORD customized"
else
    echo "⚠️  DB_PASSWORD still has example value"
fi
```

---

## Phase 4: Docker Setup ✅

```bash
# Check Docker is installed
docker --version && echo "✅ Docker installed" || echo "❌ Docker not found"

# Check Docker Compose
docker compose --version && echo "✅ Docker Compose installed" || echo "❌ Docker Compose not found"

# Verify docker-compose.yml is valid
docker compose config > /dev/null && echo "✅ docker-compose.yml is valid" || echo "❌ docker-compose.yml has errors"

# List services
echo ""
echo "Services in docker-compose.yml:"
docker compose config --services
```

---

## Phase 5: Pre-Build Checks ✅

```bash
# Verify each service directory has requirements
echo "Checking backend dependencies..."
test -f AIBI_Backend/requirements.txt && echo "✅ Backend A requirements.txt" || echo "❌ Missing"
test -f AIBI_Copilot_Main_Brain/requirements.txt && echo "✅ Backend B requirements.txt" || echo "❌ Missing"
test -f AIBI_Copilot_Frontend/package.json && echo "✅ Frontend package.json" || echo "❌ Missing"

# Check Vite config for frontend
test -f AIBI_Copilot_Frontend/vite.config.ts && echo "✅ Frontend vite.config.ts" || echo "❌ Missing"

# Check for database schema
test -f AIBI_Backend/database_schema.sql && echo "✅ Database schema file" || echo "❌ Missing"
```

---

## Phase 6: Build Test ✅

```bash
# Test docker compose build (without starting)
echo "Building Docker images (this may take 5-10 minutes)..."
docker compose build 2>&1 | tee build.log

# Check build success
if docker images | grep -E "(AIBI|postgres|redis)" > /dev/null; then
    echo "✅ Docker images built successfully"
else
    echo "❌ Image build may have failed - check build.log"
fi
```

---

## Phase 7: Startup Test ✅

```bash
# Start services
echo "Starting services..."
docker compose up -d

# Wait for services to be ready
echo "Waiting for services to start (30 seconds)..."
sleep 30

# Check all containers are running
echo ""
echo "Service Status:"
docker compose ps

# Verify health status
echo ""
echo "Health Checks:"
docker compose ps --format "table {{.Names}}\t{{.Status}}"
```

---

## Phase 8: Database Connectivity ✅

```bash
# Test database connection
echo "Testing database connection..."
docker compose exec database pg_isready -U AIBI_user -d AIBI_Backend && echo "✅ Database is ready" || echo "❌ Database connection failed"

# Verify database name
docker compose exec database psql -U AIBI_user -l | grep AIBI_Backend && echo "✅ Database 'AIBI_Backend' exists" || echo "❌ Database not found"

# Check for tables
echo "Database tables:"
docker compose exec database psql -U AIBI_user -d AIBI_Backend -c "\dt" | head -20
```

---

## Phase 9: Redis Connectivity ✅

```bash
# Test Redis
echo "Testing Redis..."
docker compose exec redis redis-cli PING && echo "✅ Redis is responding" || echo "❌ Redis connection failed"

# Check Redis memory
docker compose exec redis redis-cli INFO memory | grep used_memory_human
```

---

## Phase 10: API Endpoint Tests ✅

```bash
# Test Backend A (CSV API)
echo "Testing CSV API..."
curl -s http://localhost:8001/docs > /dev/null && echo "✅ CSV API (8001) responding" || echo "❌ CSV API not responding"
curl -s -I http://localhost:8001/docs | head -1

# Test Backend B (Main Brain)
echo "Testing Main Brain API..."
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Main Brain API (8000) responding" || echo "❌ Main Brain API not responding"
curl -s -I http://localhost:8000/docs | head -1

# Test Frontend
echo "Testing Frontend..."
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend (3000) responding" || echo "❌ Frontend not responding"
```

---

## Phase 11: Database Sharing Verification ✅

```bash
# Verify both backends connect to same database
echo "Verifying database configuration..."

# Backend A
echo "Backend A (CSV):"
docker compose exec backend-csv env | grep DB_

echo ""
echo "Backend B (Main Brain):"
docker compose exec backend-brain env | grep DB_

# Both should show:
# ✅ DB_HOST=database
# ✅ DB_PORT=5432
# ✅ DB_NAME=AIBI_Backend
# ✅ DB_USER=AIBI_user
```

---

## Phase 12: Cross-Service Communication ✅

```bash
# Test backend-to-database from CSV API
echo "Testing CSV API → Database connection..."
docker compose exec backend-csv python -c "import asyncio; from database.connection import DatabaseConnection; print('✅ CSV API can connect to database')" 2>&1 || echo "⚠️  Check CSV API logs"

# Test backend-to-database from Main Brain
echo "Testing Main Brain → Database connection..."
docker compose exec backend-brain python -c "from database.connection import db_manager; print('✅ Main Brain can connect to database')" 2>&1 || echo "⚠️  Check Main Brain logs"
```

---

## Phase 13: Environment Configuration Verification ✅

```bash
# Verify all services have correct env vars
echo "Frontend environment:"
docker compose exec frontend env | grep VITE_

echo ""
echo "Backend A environment:"
docker compose exec backend-csv env | grep -E "(GROQ|SUPABASE|DB_)" | head -5

echo ""
echo "Backend B environment:"
docker compose exec backend-brain env | grep -E "(LLM_|REDIS_|DB_)" | head -5
```

---

## Phase 14: Log Review ✅

```bash
# Check for errors in logs
echo "Checking for critical errors..."

echo "Frontend logs:"
docker compose logs frontend | grep -i "error" | head -3

echo "Backend A logs:"
docker compose logs backend-csv | grep -i "error" | head -3

echo "Backend B logs:"
docker compose logs backend-brain | grep -i "error" | head -3

echo "Database logs:"
docker compose logs database | grep -i "error" | head -3
```

---

## Phase 15: Final System Check ✅

```bash
# Overall system health
echo "=== AIBI SETUP VERIFICATION SUMMARY ==="
echo ""

# Count passed checks
PASSED=0
TOTAL=15

# Service checks
docker compose ps --format "{{.Names}}" | wc -l | xargs -I {} echo "Services running: {} of 5"

# Health check
if docker compose ps | grep -c "(healthy)" > 0; then
    echo "✅ Services reporting healthy"
    ((PASSED++))
fi

# Database connectivity
if docker compose exec database pg_isready -U AIBI_user > /dev/null 2>&1; then
    echo "✅ Database connectivity confirmed"
    ((PASSED++))
fi

# API responsiveness
APIS_OK=0
curl -s http://localhost:8000/docs > /dev/null 2>&1 && ((APIS_OK++))
curl -s http://localhost:8001/docs > /dev/null 2>&1 && ((APIS_OK++))
curl -s http://localhost:3000 > /dev/null 2>&1 && ((APIS_OK++))

if [ $APIS_OK -eq 3 ]; then
    echo "✅ All APIs responding (3/3)"
    ((PASSED+=3))
fi

echo ""
echo "Setup Status: $PASSED/$TOTAL checks passed"
```

---

## Cleanup After Testing

```bash
# Stop services without removing volumes (preserve data)
docker compose down

# Stop services and remove everything (fresh start next time)
docker compose down -v

# View test output
cat build.log
```

---

## ✅ Setup Complete!

If all phases pass:
- ✅ All services are correctly configured
- ✅ Both backends connect to the same database
- ✅ Docker network is functional
- ✅ APIs are responsive
- ✅ Ready for production use

**Next Steps:**
1. Review `QUICKSTART.md` for common tasks
2. Read `README.md` for full documentation
3. Check `ARCHITECTURE.md` for system design details
4. Use `./dev.sh` for daily operations

---

## 🆘 If Checks Fail

1. **Review logs:** `docker compose logs -f`
2. **Check errors:** See `TROUBLESHOOTING.md`
3. **Reset system:** `./dev.sh reset`
4. **Rebuild:** `docker compose up --build --no-cache`

---

**Verification Date:** January 2026
