# 🚀 START HERE - AWS EC2 Deployment

## ✅ Your Project is Ready!

This backend is **100% ready** for AWS EC2 deployment with:
- ✅ CORS open to all origins (MVP configuration)
- ✅ Complete deployment documentation
- ✅ Automated deployment script
- ✅ Production-ready configuration

## 🎯 Three Simple Steps

### Step 1: Launch EC2 Instance (5 minutes)
1. Go to AWS Console → EC2 → Launch Instance
2. Choose: **Ubuntu 22.04 LTS**
3. Instance type: **t3.medium** (2 vCPU, 4GB RAM)
4. Storage: **30 GB**
5. Security groups: Allow ports **22, 80, 443, 8000**
6. Launch and note your **Public IP address**

### Step 2: Deploy Backend (25 minutes)
```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Clone and deploy
git clone YOUR_REPO_URL
cd YOUR_REPO
chmod +x QUICK_DEPLOY.sh
./QUICK_DEPLOY.sh

# Edit .env with your credentials
nano .env
```

### Step 3: Start Service (5 minutes)
```bash
# Create systemd service (see DEPLOYMENT_CHECKLIST.md)
sudo systemctl start chatbot-backend

# Test
curl http://YOUR_EC2_IP:8000/health
```

## 📚 Documentation Guide

**New to deployment?** → Read `DEPLOY_README.md` first (2 min)

**Want step-by-step?** → Follow `DEPLOYMENT_CHECKLIST.md` (40 min)

**Need complete guide?** → Read `AWS_EC2_DEPLOYMENT_GUIDE.md` (45 min)

**Need quick commands?** → Use `QUICK_REFERENCE.md` (reference card)

**Want to understand changes?** → See `DEPLOYMENT_CHANGES.md` (3 min)

**Ready to deploy?** → Check `DEPLOYMENT_READY.md` (summary)

## 🎯 Quick Deploy Command

```bash
# One-line deploy (after cloning repo)
chmod +x QUICK_DEPLOY.sh && ./QUICK_DEPLOY.sh
```

## 🧪 Test Your Deployment

```bash
# Health check
curl http://YOUR_IP:8000/health

# System status
curl http://YOUR_IP:8000/api/system/status

# Test query
curl -X POST http://YOUR_IP:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is our total capacity?","session_id":"test","user_id":"user"}'
```

## 💰 Cost Estimate

- **t3.medium**: ~$35-45/month (recommended)
- **t2.medium**: ~$30-35/month (minimum)

## ⏱️ Time Estimate

- **Quick Deploy**: 30 minutes
- **Manual Deploy**: 40-45 minutes

## 🔑 What You Need

- [ ] AWS account with EC2 access
- [ ] SSH key pair
- [ ] Database credentials (DB_USER, DB_PASSWORD)
- [ ] LLM API key (OpenRouter or OpenAI)
- [ ] 30-40 minutes of time

## 🎉 That's It!

Your backend will be live at: `http://YOUR_EC2_IP:8000`

Your frontend can connect from any domain (CORS is open).

## 📞 Need Help?

1. Check logs: `sudo journalctl -u chatbot-backend -f`
2. See troubleshooting: `AWS_EC2_DEPLOYMENT_GUIDE.md`
3. Quick commands: `QUICK_REFERENCE.md`

---

**Ready? Start with `DEPLOY_README.md` or run `QUICK_DEPLOY.sh`!** 🚀
