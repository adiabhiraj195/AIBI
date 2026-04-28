# 🚀 Quick Start - AWS EC2 Deployment

Deploy this Multi-Agent Chatbot Copilot backend to AWS EC2 in 30 minutes.

## ✅ What's Ready

This project is **production-ready** with:
- ✅ CORS open to all origins (MVP configuration)
- ✅ FastAPI backend with multi-agent orchestration
- ✅ PostgreSQL + Redis integration
- ✅ Comprehensive error handling
- ✅ Health check endpoints
- ✅ Systemd service configuration
- ✅ Nginx reverse proxy support

## 📋 What You Need

1. **AWS Account** with EC2 access
2. **SSH Key Pair** for EC2 instance
3. **Database Credentials** (DB_USER, DB_PASSWORD)
4. **LLM API Key** (OpenRouter or OpenAI)

## 🎯 Three Ways to Deploy

### Option 1: Quick Deploy Script (Recommended)
```bash
# On your EC2 instance
git clone YOUR_REPO_URL
cd YOUR_REPO
chmod +x QUICK_DEPLOY.sh
./QUICK_DEPLOY.sh
```

### Option 2: Follow Checklist
See `DEPLOYMENT_CHECKLIST.md` for step-by-step checklist

### Option 3: Full Manual Guide
See `AWS_EC2_DEPLOYMENT_GUIDE.md` for complete documentation

## ⚡ Super Quick Start

1. **Launch EC2**: Ubuntu 22.04, t3.medium, 30GB storage
2. **Security Groups**: Allow ports 22, 80, 443, 8000
3. **SSH Connect**: `ssh -i your-key.pem ubuntu@YOUR_IP`
4. **Clone & Deploy**: Run the quick deploy script above
5. **Configure**: Edit `.env` with your credentials
6. **Start Service**: Setup systemd service (see checklist)
7. **Test**: `curl http://YOUR_IP:8000/health`

## 🌐 API Endpoints

Once deployed, your backend will be available at:

```
http://YOUR_EC2_PUBLIC_IP:8000
```

Key endpoints:
- `GET /health` - Health check
- `GET /api/system/status` - System status
- `POST /api/query` - Main query processing
- `GET /api/conversation/{session_id}` - Conversation history

## 🔧 Configuration

The CORS policy is already set to allow all origins:

```python
allow_origins=["*"]  # Open to all for MVP
```

Your frontend can connect from any domain without CORS issues.

## 📊 Resource Requirements

**Minimum**: t2.medium (2 vCPU, 4GB RAM, 30GB storage) - ~$30/month
**Recommended**: t3.medium (2 vCPU, 4GB RAM, 50GB storage) - ~$35/month

## 🧪 Test Your Deployment

```bash
# Health check
curl http://YOUR_IP:8000/health

# System status
curl http://YOUR_IP:8000/api/system/status

# Test query
curl -X POST http://YOUR_IP:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is our total portfolio capacity?",
    "session_id": "test-123",
    "user_id": "test-user"
  }'
```

## 📚 Documentation Files

- `DEPLOY_README.md` (this file) - Quick start overview
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `AWS_EC2_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `QUICK_DEPLOY.sh` - Automated deployment script
- `README.md` - Project documentation

## 🎉 That's It!

Your backend is ready to deploy. Choose your preferred method above and follow the instructions.

**Questions?** Check the troubleshooting section in `AWS_EC2_DEPLOYMENT_GUIDE.md`

---

**Deployment Time**: 30-40 minutes
**Cost**: $35-45/month (t3.medium)
**Difficulty**: Easy (automated script provided)
