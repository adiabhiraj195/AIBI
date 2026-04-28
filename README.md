# Suzlon Multi-Service Architecture 🏗️

Complete, production-ready setup for running three services with shared database architecture.

## 📋 Project Overview

This repository contains:

1. **Frontend**: React + Vite SPA (Port 3000)
   - CFO Financial Intelligence Dashboard
   - Real-time conversation interface
   - Visualization and analytics

2. **Backend A**: Suzlon_Backend (Port 8001)
   - FastAPI CSV Upload & Processing API
   - File management and preview
   - Knowledge base management
   - Groq AI integration for CSV analysis

3. **Backend B**: Suzlon_Copilot_Main_Brain (Port 8000)
   - FastAPI Multi-Agent RAG System
   - CFO-grade financial insights
   - LangChain + LlamaIndex orchestration
   - Redis conversation memory
   - pgvector embeddings

4. **Database**: PostgreSQL (Port 5432)
   - Single shared database: `Suzlon_Backend`
   - Both backends connect to the same instance
   - pgvector extension for embeddings

5. **Cache**: Redis (Port 6379)
   - Conversation memory for Main Brain
   - Session management

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (v2.0+)
- 4GB RAM minimum
- 2 CPU cores minimum

### One-Command Startup

```bash
# From the root directory (/Users/abhi/Documents/Nspark)
docker compose up --build
```

That's it! All services will start in order:
1. Database initializes
2. Redis starts
3. Backend services connect to database
4. Frontend builds and starts

---

## 🏗️ Architecture

### Service Communication

```
┌─────────────────────────────────────────────────────┐
│                Frontend (3000)                      │
│              React + Vite Dashboard                 │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│  Main Brain      │    │   CSV Backend    │
│  Port 8000       │    │   Port 8001      │
│  (FastAPI)       │    │   (FastAPI)      │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         │   ┌───────────────────┘
         │   │
         ▼   ▼
   ┌──────────────────┐
   │  PostgreSQL      │
   │  Suzlon_Backend  │
   │  (Shared DB)     │
   └──────────────────┘
         ▲
         │
         ▼
   ┌──────────────────┐
   │  Redis           │
   │  (Cache/Memory)  │
   └──────────────────┘
```

### Shared Database Design

Both backend services connect to the **same PostgreSQL instance** with database name `Suzlon_Backend`.

**Configuration:**
```
Host: database (Docker) or localhost (Local Development)
Port: 5432
Database: Suzlon_Backend
User: suzlon_user (configurable via .env)
Password: (set via .env)
```

---

## 📝 Environment Configuration

### Root Level: `.env` File

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key variables:
```dotenv
# Shared database credentials
DB_USER=suzlon_user
DB_PASSWORD=your_secure_password

# LLM API (for Main Brain)
LLM_API_KEY=your_llm_key
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free

# Groq API (for CSV processing)
GROQ_API_KEY=your_groq_key

# Debug mode
DEBUG=false
```

### Service-Specific Configuration

Each service has its own `.env.example`:

1. **Suzlon_Backend/.env.example** - CSV API config
2. **Suzlon_Copilot_Main_Brain/.env.example** - Main Brain config
3. **Suzlon_Copilot_Frontend/.env.example** - Frontend API URLs

When using Docker Compose, these are pulled from the root `.env` automatically.

---

## 🔧 Commands Reference

### Start All Services
```bash
docker compose up --build
```

### Stop All Services
```bash
docker compose down
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend-brain
docker compose logs -f backend-csv
docker compose logs -f frontend
docker compose logs -f database
docker compose logs -f redis
```

### Access Interactive Shell
```bash
# Backend Brain
docker compose exec backend-brain bash

# Backend CSV
docker compose exec backend-csv bash

# Database
docker compose exec database psql -U suzlon_user -d Suzlon_Backend
```

### Reset Database
```bash
# Remove database volume and recreate
docker compose down -v
docker compose up --build
```

---

## 📊 Service Details

### Frontend (React + Vite)

**Location:** `Suzlon_Copilot_Frontend/`

**Port:** 3000

**Build Process:**
- Multi-stage build with Node.js
- Vite bundles the React app
- Serve.js hosts the static SPA

**Environment Variables:**
```
VITE_API_URL=http://localhost:8000
VITE_CSV_API_URL=http://localhost:8001
```

**Health Check:**
```
GET http://localhost:3000
```

---

### Backend A: CSV API (FastAPI)

**Location:** `Suzlon_Backend/`

**Port:** 8001

**Features:**
- CSV file upload and processing
- File preview and validation
- Groq AI-powered analysis
- Knowledge base management
- Supabase integration (optional)

**Database:** Suzlon_Backend (shared)

**Key Dependencies:**
- FastAPI
- Pandas
- Groq API
- Supabase

**Environment Variables:**
- Database connection (`DB_HOST`, `DB_USER`, etc.)
- GROQ API key
- Supabase credentials (optional)

**Health Check:**
```
GET http://localhost:8001/docs
```

---

### Backend B: Multi-Agent RAG (FastAPI)

**Location:** `Suzlon_Copilot_Main_Brain/`

**Port:** 8000

**Features:**
- Multi-agent orchestration (LangChain)
- RAG system (LlamaIndex)
- Conversation memory (Redis)
- Vector embeddings (pgvector)
- CFO financial insights
- Feedback system

**Database:** Suzlon_Backend (shared)

**Redis:** For conversation memory

**Key Dependencies:**
- FastAPI
- LangChain
- LlamaIndex
- pgvector
- Redis
- Transformers

**Environment Variables:**
- Database connection
- Redis connection
- LLM API credentials
- Embedding model configuration

**Health Check:**
```
GET http://localhost:8000/docs
```

---

### PostgreSQL Database

**Service:** `database`

**Port:** 5432

**Database Name:** `Suzlon_Backend`

**Features:**
- Alpine Linux image (lightweight)
- pgvector extension for embeddings
- Persistent volume: `postgres_data`
- Auto-initializes with `database_schema.sql`

**Connection String:**
```
postgresql://suzlon_user:password@database:5432/Suzlon_Backend
```

**Health Check:**
```
pg_isready -U suzlon_user
```

---

### Redis Cache

**Service:** `redis`

**Port:** 6379

**Features:**
- Alpine Linux image
- Persistent storage with AOF
- Used by Main Brain for conversation memory

**Health Check:**
```
redis-cli ping
```

---

## 🔗 How Services Communicate

### Frontend → Backend

```
Frontend (3000)
    │
    ├─→ GET/POST http://backend-brain:8000/api/...
    │                  (Main Brain API)
    │
    └─→ GET/POST http://backend-csv:8001/api/...
                      (CSV API)
```

In Docker, services communicate via service names on the shared `suzlon-network`.

### Backends → Database

```
Backend A (8001)
    └─→ postgresql://database:5432/Suzlon_Backend

Backend B (8000)
    └─→ postgresql://database:5432/Suzlon_Backend
```

Both connect to the same database and table schema.

### Backend B → Redis

```
Backend Brain (8000)
    └─→ redis://redis:6379
```

---

## 🐛 Debugging & Troubleshooting

### Check Service Status
```bash
docker compose ps
```

Expected output:
```
NAME                 IMAGE              STATUS           PORTS
suzlon-database      postgres:16-alpine Up (healthy)     0.0.0.0:5432->5432/tcp
suzlon-redis         redis:7-alpine     Up (healthy)     0.0.0.0:6379->6379/tcp
suzlon-backend-csv   suzlon-backend-csv:latest Up       0.0.0.0:8001->8001/tcp
suzlon-backend-brain suzlon-backend-brain:latest Up     0.0.0.0:8000->8000/tcp
suzlon-frontend      suzlon-frontend:latest Up           0.0.0.0:3000->3000/tcp
```

### Common Issues

#### **Issue: Backends can't connect to database**

**Symptoms:** `ConnectionRefusedError` or `no such host`

**Solution:**
1. Check database is running: `docker compose logs database`
2. Verify `.env` has correct credentials
3. Ensure database is healthy: `docker compose ps`
4. Reset and rebuild: `docker compose down -v && docker compose up --build`

#### **Issue: Port already in use**

**Symptoms:** `Address already in use` error

**Solution:**
```bash
# Find process using port (e.g., 8000)
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
# Change "8000:8000" to "8002:8000"
```

#### **Issue: Frontend can't reach backend API**

**Symptoms:** Network errors in browser console

**Solution:**
1. Check backend is running: `docker compose logs backend-brain`
2. Verify API URL in `.env`: `VITE_API_URL=http://localhost:8000`
3. Open http://localhost:8000/docs in browser (should see API docs)

#### **Issue: Out of memory during build**

**Symptoms:** Build process crashes or freezes

**Solution:**
```bash
# Increase Docker memory limit and rebuild
docker compose down
docker compose up --build
```

### View API Documentation

Each FastAPI service exposes interactive docs:

- Main Brain API: http://localhost:8000/docs
- CSV API: http://localhost:8001/docs

---

## 📦 Database Schema

The database initializes automatically using `Suzlon_Backend/database_schema.sql`.

**Key Tables** (Both backends use these):
- CSV metadata tables (Backend A)
- RAG embeddings table (Backend B)
- Conversation history
- User sessions
- Feedback records

---

## 🚢 Production Deployment

### Docker Hub Images

Build and push images:

```bash
# Backend A
docker build -t your-registry/suzlon-backend:1.0 ./Suzlon_Backend
docker push your-registry/suzlon-backend:1.0

# Backend B
docker build -t your-registry/suzlon-brain:1.0 ./Suzlon_Copilot_Main_Brain
docker push your-registry/suzlon-brain:1.0

# Frontend
docker build -t your-registry/suzlon-frontend:1.0 ./Suzlon_Copilot_Frontend
docker push your-registry/suzlon-frontend:1.0
```

### AWS EC2 / Kubernetes

Refer to:
- `Suzlon_Backend/SETUP_GUIDE.md`
- `Suzlon_Copilot_Main_Brain/AWS_EC2_DEPLOYMENT_GUIDE.md`
- `Suzlon_Copilot_Frontend/AWS_DEPLOYMENT_GUIDE.md`

### Environment Variables (Production)

Set via:
- `.env` file
- Docker secrets
- Container orchestration platform (K8s secrets, ECS task definitions)

**Critical:** Never hardcode secrets in images!

---

## 📈 Monitoring & Logs

### Docker Compose Logging

```bash
# Real-time logs for all services
docker compose logs -f

# Logs for specific service
docker compose logs -f backend-brain

# Last 100 lines
docker compose logs --tail=100

# With timestamps
docker compose logs -f -t
```

### Health Checks

Each service has a health check endpoint:

```bash
# Frontend
curl http://localhost:3000

# CSV API
curl http://localhost:8001/docs

# Main Brain
curl http://localhost:8000/docs

# Database
docker compose exec database pg_isready -U suzlon_user

# Redis
docker compose exec redis redis-cli ping
```

---

## 🔐 Security Notes

1. **Credentials:** Update default passwords in `.env` before production use
2. **SSL/TLS:** In production, use HTTPS and `DB_SSL_MODE=require`
3. **API Keys:** Never commit `.env` to version control (it's in `.gitignore`)
4. **Database:** Use strong passwords, limit network access
5. **Secrets:** Use container orchestration secrets in production

---

## 📄 License

[Your License Here]

---

## 🤝 Support

For issues, refer to individual service READMEs:
- `Suzlon_Backend/README.md`
- `Suzlon_Copilot_Main_Brain/README.md`
- `Suzlon_Copilot_Frontend/README.md`

---

**Last Updated:** January 2026

**Maintained by:** [Your Team]
