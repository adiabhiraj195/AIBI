# 🚀 Quick Deployment Guide

## Deploy to AWS EC2 in 5 Minutes

### Prerequisites
- AWS Account
- SSH key pair (.pem file)

### Step-by-Step

#### 1. Launch EC2 Instance
- Go to AWS Console → EC2 → Launch Instance
- Choose: Ubuntu Server 22.04 LTS
- Instance type: t2.small (recommended) or t2.micro (free tier)
- Security groups: Allow HTTP (80), HTTPS (443), SSH (22)
- Download your key pair (.pem file)

#### 2. Connect to EC2
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

#### 3. Deploy
```bash
# Clone repository
git clone YOUR_REPO_URL
cd YOUR_REPO

# Run deployment script
chmod +x deploy.sh
sudo ./deploy.sh
```

#### 4. Configure Backend URL
```bash
nano .env.production
# Update: VITE_API_URL=http://your-backend-url:8000

npm run build
sudo cp -r build/* /var/www/cfo-chatbot/
sudo systemctl restart nginx
```

#### 5. Access Your App
```
http://YOUR_EC2_IP
```

### ✅ CORS is Already Configured
The nginx.conf file has CORS set to allow all origins (`*`) for MVP purposes.

### 📖 Full Documentation
See [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md) for detailed instructions.

### 🔄 Update Deployment
```bash
cd YOUR_REPO
git pull
npm run build
sudo cp -r build/* /var/www/cfo-chatbot/
sudo systemctl restart nginx
```

### 🐛 Troubleshooting
```bash
# Check Nginx status
sudo systemctl status nginx

# View logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

That's it! 🎉
