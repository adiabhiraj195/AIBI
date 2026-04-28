# 🚀 Quick Start Guide

Get Suzlon running in 5 minutes.

---

## Step 1: Prepare Environment (1 min)

```bash
cd /Users/abhi/Documents/Nspark

# Copy environment template
cp .env.example .env

# Edit with your credentials (API keys, passwords)
nano .env
```

**Must set:**
- `DB_PASSWORD` - PostgreSQL password (change from default)
- `LLM_API_KEY` - Your LLM provider API key (OpenRouter, OpenAI, etc.)
- `GROQ_API_KEY` - Your Groq API key (for CSV analysis)

---

## Step 2: Start Everything (2 min)

```bash
# One command to start all services
docker compose up --build
```

This will:
1. ✅ Build all Docker images
2. ✅ Start PostgreSQL database
3. ✅ Start Redis cache
4. ✅ Start Backend A (CSV API) - Port 8001
5. ✅ Start Backend B (Main Brain) - Port 8000
6. ✅ Start Frontend - Port 3000

**Wait for all services to show "Up" and "healthy"** (takes ~2 minutes)

---

## Step 3: Access Services (1 min)

Once everything is running:

```
Frontend Dashboard:    http://localhost:3000
API Documentation:     http://localhost:8000/docs  (Brain)
                       http://localhost:8001/docs  (CSV)
```

---

## Step 4: Test (1 min)

**Option A: Use helper script**
```bash
./dev.sh test-api
```

**Option B: Manual test**
```bash
# Test Main Brain API
curl http://localhost:8000/docs

# Test CSV API
curl http://localhost:8001/docs

# Test Frontend
curl http://localhost:3000
```

---

## ✅ You're Done!

Both backends are now connected to the same database (`Suzlon_Backend`) and ready to use.

---

## 🆘 Troubleshooting

**Services won't start?**
```bash
# Reset everything
docker compose down -v
docker compose up --build
```

**Can't connect to API?**
```bash
# Check if services are running
docker compose ps

# View logs
docker compose logs backend-brain
docker compose logs backend-csv
```

**Database connection errors?**
- Verify `.env` has correct `DB_PASSWORD`
- Check database is healthy: `docker compose logs database`

---

## 📚 More Info

- Full documentation: `README.md`
- Architecture details: `ARCHITECTURE.md`
- Troubleshooting: `TROUBLESHOOTING.md`
- Helper commands: `./dev.sh help`

---

## 🛠️ Common Commands

```bash
# View logs
./dev.sh logs

# Stop services
./dev.sh stop

# Access database
./dev.sh db

# Access Redis
./dev.sh redis

# Service status
./dev.sh status

# Reset everything
./dev.sh reset

# Full help
./dev.sh help
```

---

**Happy coding!** 🎉
