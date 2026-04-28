# AWS EC2 Deployment Checklist

Quick reference checklist for deploying the Multi-Agent Chatbot Copilot backend.

## 🎯 Pre-Deployment

- [ ] AWS account with EC2 access
- [ ] SSH key pair created/downloaded
- [ ] Database credentials ready (DB_USER, DB_PASSWORD)
- [ ] LLM API key ready (OpenRouter or OpenAI)

## 🚀 EC2 Setup (5 minutes)

- [ ] Launch EC2 instance (Ubuntu 22.04, t3.medium, 30GB storage)
- [ ] Configure Security Groups:
  - [ ] SSH (22) - Your IP only
  - [ ] HTTP (80) - 0.0.0.0/0
  - [ ] HTTPS (443) - 0.0.0.0/0
  - [ ] Custom TCP (8000) - 0.0.0.0/0
- [ ] Note Public IP address: `_________________`
- [ ] Connect via SSH: `ssh -i your-key.pem ubuntu@YOUR_IP`

## 📦 Installation (10-15 minutes)

```bash
# Clone repository
git clone YOUR_REPO_URL
cd YOUR_REPO

# Run quick deploy script
chmod +x QUICK_DEPLOY.sh
./QUICK_DEPLOY.sh
```

The script will:
- [ ] Update system packages
- [ ] Install Python 3.11, Redis, Git, Nginx
- [ ] Create virtual environment
- [ ] Install Python dependencies
- [ ] Create .env file

## ⚙️ Configuration (5 minutes)

Edit `.env` file with your credentials:

```bash
nano .env
```

Required changes:
- [ ] `DB_USER=your_actual_username`
- [ ] `DB_PASSWORD=your_actual_password`
- [ ] `LLM_API_KEY=your_actual_api_key`
- [ ] `SECRET_KEY=` (generate with: `python3 -c 'import secrets; print(secrets.token_urlsafe(32))'`)
- [ ] `DEBUG=false`
- [ ] `ENVIRONMENT=production`

## 🔧 Systemd Service Setup (5 minutes)

```bash
# Create service file
sudo nano /etc/systemd/system/chatbot-backend.service
```

Paste this (replace YOUR_REPO with actual folder name):

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

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable chatbot-backend
sudo systemctl start chatbot-backend
sudo systemctl status chatbot-backend
```

- [ ] Service created
- [ ] Service enabled
- [ ] Service started
- [ ] Service status shows "active (running)"

## 🌐 Nginx Setup (Optional, 5 minutes)

```bash
sudo nano /etc/nginx/sites-available/chatbot-backend
```

Paste this (replace YOUR_EC2_PUBLIC_IP):

```nginx
server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP;
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/chatbot-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

- [ ] Nginx configured
- [ ] Configuration tested
- [ ] Nginx restarted

## 🧪 Testing (5 minutes)

From your local machine:

```bash
# Test health endpoint
curl http://YOUR_EC2_PUBLIC_IP:8000/health

# Test system status
curl http://YOUR_EC2_PUBLIC_IP:8000/api/system/status

# Test query endpoint
curl -X POST http://YOUR_EC2_PUBLIC_IP:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is our total portfolio capacity?",
    "session_id": "test-123",
    "user_id": "test-user"
  }'
```

- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] System status returns agent information
- [ ] Query endpoint returns response with data

## 🔒 Security (5 minutes)

```bash
# Setup firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

- [ ] Firewall configured
- [ ] Security group restricted SSH to your IP only

## 📝 Final Steps

- [ ] Document your EC2 Public IP: `_________________`
- [ ] Update frontend `.env` with backend URL
- [ ] Test frontend connection to backend
- [ ] Monitor logs: `sudo journalctl -u chatbot-backend -f`

## 🎉 Deployment Complete!

Your backend is now live at:
- **Direct**: `http://YOUR_EC2_PUBLIC_IP:8000`
- **Via Nginx**: `http://YOUR_EC2_PUBLIC_IP`

## 📊 Quick Commands

```bash
# View logs
sudo journalctl -u chatbot-backend -f

# Restart service
sudo systemctl restart chatbot-backend

# Check status
sudo systemctl status chatbot-backend

# Update code
cd YOUR_REPO && git pull && sudo systemctl restart chatbot-backend
```

## 🐛 Troubleshooting

If something doesn't work:

1. **Check logs**: `sudo journalctl -u chatbot-backend -n 50`
2. **Check service status**: `sudo systemctl status chatbot-backend`
3. **Test manually**: `source venv/bin/activate && python main.py`
4. **Check .env file**: `cat .env` (verify credentials)
5. **Check Redis**: `sudo systemctl status redis-server`

## 📚 Full Documentation

For detailed information, see:
- `AWS_EC2_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `README.md` - Project documentation
- `FRONTEND_INTEGRATION_GUIDE.md` - Frontend integration

---

**Total Deployment Time**: ~30-40 minutes

**Estimated Monthly Cost**: $35-45 (t3.medium instance)
