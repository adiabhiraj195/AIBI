# Quick Reference Card - AWS EC2 Deployment

## 🚀 One-Command Deploy

```bash
git clone YOUR_REPO && cd YOUR_REPO && chmod +x QUICK_DEPLOY.sh && ./QUICK_DEPLOY.sh
```

## 📋 Essential Commands

### Service Management
```bash
# Start
sudo systemctl start chatbot-backend

# Stop
sudo systemctl stop chatbot-backend

# Restart
sudo systemctl restart chatbot-backend

# Status
sudo systemctl status chatbot-backend

# Enable on boot
sudo systemctl enable chatbot-backend
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u chatbot-backend -f

# Last 50 lines
sudo journalctl -u chatbot-backend -n 50

# Today's logs
sudo journalctl -u chatbot-backend --since today
```

### Update Application
```bash
cd YOUR_REPO
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart chatbot-backend
```

## 🧪 Test Endpoints

```bash
# Health check
curl http://YOUR_IP:8000/health

# System status
curl http://YOUR_IP:8000/api/system/status

# Database status
curl http://YOUR_IP:8000/api/system/database

# Test query
curl -X POST http://YOUR_IP:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is our total capacity?","session_id":"test","user_id":"user"}'
```

## 🔧 Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u chatbot-backend -n 50

# Test manually
cd YOUR_REPO
source venv/bin/activate
python main.py
```

### Database connection issues
```bash
# Test connection
telnet 23.22.202.15 5432

# Check credentials
grep DB_ .env
```

### Redis issues
```bash
# Check status
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Restart
sudo systemctl restart redis-server
```

### Port already in use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 PID
```

## 📊 EC2 Instance Specs

### Minimum
- Type: t2.medium
- vCPU: 2
- RAM: 4 GB
- Storage: 30 GB
- Cost: ~$30/month

### Recommended
- Type: t3.medium
- vCPU: 2
- RAM: 4 GB
- Storage: 50 GB
- Cost: ~$35/month

## 🔒 Security Groups

| Type | Port | Source |
|------|------|--------|
| SSH | 22 | Your IP |
| HTTP | 80 | 0.0.0.0/0 |
| HTTPS | 443 | 0.0.0.0/0 |
| Custom | 8000 | 0.0.0.0/0 |

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/system/status` | GET | System status |
| `/api/system/database` | GET | Database status |
| `/api/query` | POST | Process query |
| `/api/conversation/{id}` | GET | Get conversation |
| `/api/conversation/{id}` | DELETE | Clear conversation |
| `/api/memory/stats` | GET | Memory stats |

## 📝 Environment Variables

Required in `.env`:
```bash
DB_USER=your_username
DB_PASSWORD=your_password
LLM_API_KEY=your_api_key
SECRET_KEY=generate_random_key
DEBUG=false
ENVIRONMENT=production
```

Generate SECRET_KEY:
```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

## 🔄 Systemd Service File

Location: `/etc/systemd/system/chatbot-backend.service`

```ini
[Unit]
Description=Multi-Agent Chatbot Copilot Backend
After=network.target redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/YOUR_REPO
Environment="PATH=/home/ubuntu/YOUR_REPO/venv/bin"
ExecStart=/home/ubuntu/YOUR_REPO/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🌐 Nginx Config

Location: `/etc/nginx/sites-available/chatbot-backend`

```nginx
server {
    listen 80;
    server_name YOUR_IP;
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

## 📚 Documentation Files

- `QUICK_REFERENCE.md` - This file
- `DEPLOY_README.md` - Quick start
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step
- `AWS_EC2_DEPLOYMENT_GUIDE.md` - Complete guide
- `QUICK_DEPLOY.sh` - Automated script

## 🎯 Deployment Steps (Summary)

1. Launch EC2 (Ubuntu 22.04, t3.medium)
2. Configure security groups
3. SSH connect
4. Clone repo
5. Run `./QUICK_DEPLOY.sh`
6. Edit `.env`
7. Setup systemd service
8. Start service
9. Test endpoints
10. Done! ✅

## 💡 Pro Tips

- Always check logs first: `sudo journalctl -u chatbot-backend -f`
- Test manually before systemd: `source venv/bin/activate && python main.py`
- Keep .env secure: `chmod 600 .env`
- Monitor resources: `htop` or `top`
- Setup swap if needed: See AWS_EC2_DEPLOYMENT_GUIDE.md
- Use tmux/screen for long sessions
- Regular backups of .env file
- Document your EC2 IP address

## 🆘 Emergency Commands

```bash
# Stop everything
sudo systemctl stop chatbot-backend
sudo systemctl stop nginx
sudo systemctl stop redis-server

# Start everything
sudo systemctl start redis-server
sudo systemctl start chatbot-backend
sudo systemctl start nginx

# Check all services
sudo systemctl status chatbot-backend redis-server nginx

# Restart EC2 instance
sudo reboot
```

---

**Keep this file handy for quick reference during deployment and maintenance!**
