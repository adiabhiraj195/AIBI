# AWS EC2 Deployment Guide - CFO Chatbot Frontend

Complete step-by-step guide to deploy this React frontend on AWS EC2.

## 📋 Prerequisites

- AWS Account
- Basic knowledge of SSH and Linux commands
- Your backend API URL (if you have one running)

## 🚀 Quick Deployment (5 Steps)

### Step 1: Launch EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance

2. **Configure Instance:**
   - **Name:** `cfo-chatbot-frontend`
   - **AMI:** Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type:** t2.micro (Free tier) or t2.small (recommended)
   - **Key Pair:** Create new or use existing (download .pem file)
   - **Network Settings:**
     - ✅ Allow SSH (port 22) from your IP
     - ✅ Allow HTTP (port 80) from anywhere (0.0.0.0/0)
     - ✅ Allow HTTPS (port 443) from anywhere (0.0.0.0/0) - optional
   - **Storage:** 8 GB (default is fine)

3. **Launch Instance** and wait for it to start

4. **Note your Public IP:** Find it in the EC2 dashboard (e.g., 54.123.45.67)

### Step 2: Connect to Your EC2 Instance

```bash
# Make your key file secure (first time only)
chmod 400 your-key.pem

# Connect via SSH (replace with your IP and key file)
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Clone and Deploy

Once connected to your EC2 instance:

```bash
# Update system
sudo apt-get update

# Install git
sudo apt-get install -y git

# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Make deploy script executable
chmod +x deploy.sh

# Run deployment script
sudo ./deploy.sh
```

The script will automatically:
- ✅ Install Node.js and npm
- ✅ Install Nginx web server
- ✅ Install dependencies
- ✅ Build the production bundle
- ✅ Configure Nginx with CORS enabled
- ✅ Start the web server

### Step 4: Configure Backend URL

```bash
# Edit production environment file
nano .env.production

# Update this line with your actual backend URL:
# VITE_API_URL=http://your-backend-url:8000
# Or if backend is on same server:
# VITE_API_URL=http://localhost:8000

# Save: Ctrl+X, then Y, then Enter

# Rebuild with new configuration
npm run build

# Restart Nginx
sudo systemctl restart nginx
```

### Step 5: Access Your Application

Open your browser and go to:
```
http://YOUR_EC2_PUBLIC_IP
```

🎉 **Done!** Your frontend is now live!

---

## 🔧 Manual Deployment (Alternative)

If you prefer manual control or the script fails:

### 1. Install Dependencies

```bash
# Update system
sudo apt-get update

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx
sudo apt-get install -y nginx

# Verify installations
node --version  # Should show v18.x.x
npm --version   # Should show 9.x.x or higher
```

### 2. Clone and Build

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Install dependencies
npm install

# Configure environment
cp .env.production .env
nano .env  # Edit VITE_API_URL

# Build production bundle
npm run build
```

### 3. Configure Nginx

```bash
# Create application directory
sudo mkdir -p /var/www/cfo-chatbot

# Copy build files
sudo cp -r build/* /var/www/cfo-chatbot/

# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/cfo-chatbot

# Enable site
sudo ln -s /etc/nginx/sites-available/cfo-chatbot /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 4. Verify Deployment

```bash
# Check Nginx status
sudo systemctl status nginx

# Check if site is accessible
curl http://localhost

# View Nginx logs if issues
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 Security Considerations

### For Production (Beyond MVP):

1. **Enable HTTPS:**
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com
```

2. **Restrict CORS:**
   - Edit `nginx.conf`
   - Change `'*'` to your specific domain
   - Rebuild and restart

3. **Set up Firewall:**
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

4. **Regular Updates:**
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

---

## 🔄 Updating Your Deployment

When you make changes to your code:

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Navigate to project
cd YOUR_REPO

# Pull latest changes
git pull origin main

# Rebuild
npm install  # If dependencies changed
npm run build

# Copy new build
sudo cp -r build/* /var/www/cfo-chatbot/

# Restart Nginx
sudo systemctl restart nginx
```

---

## 🐛 Troubleshooting

### Application not loading?

```bash
# Check Nginx status
sudo systemctl status nginx

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

### Can't connect to backend?

1. Check `.env` file has correct `VITE_API_URL`
2. Verify backend is running and accessible
3. Check browser console for CORS errors
4. Ensure backend has CORS enabled

### Build fails?

```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Port 80 already in use?

```bash
# Check what's using port 80
sudo lsof -i :80

# Stop conflicting service
sudo systemctl stop apache2  # If Apache is running
```

---

## 📊 Monitoring

### Check Application Status

```bash
# Nginx status
sudo systemctl status nginx

# View access logs
sudo tail -f /var/log/nginx/access.log

# View error logs
sudo tail -f /var/log/nginx/error.log

# Check disk space
df -h

# Check memory usage
free -h
```

### Set up Auto-restart (Optional)

```bash
# Nginx auto-restarts by default
# Verify it's enabled
sudo systemctl is-enabled nginx
```

---

## 💰 Cost Optimization

- **t2.micro** (Free tier): Good for testing, may be slow
- **t2.small**: Recommended for MVP ($0.023/hour ≈ $17/month)
- **t2.medium**: Better performance ($0.046/hour ≈ $34/month)

### Stop instance when not in use:
```bash
# From AWS Console: EC2 → Instances → Stop
# Restart when needed (IP may change)
```

---

## 🎯 Quick Reference

### Important Files
- `/var/www/cfo-chatbot/` - Application files
- `/etc/nginx/sites-available/cfo-chatbot` - Nginx config
- `.env.production` - Environment variables

### Important Commands
```bash
# Restart Nginx
sudo systemctl restart nginx

# View logs
sudo tail -f /var/log/nginx/error.log

# Rebuild app
npm run build && sudo cp -r build/* /var/www/cfo-chatbot/

# Check Nginx config
sudo nginx -t
```

---

## 📞 Need Help?

Common issues:
1. **502 Bad Gateway** → Backend not running or wrong URL
2. **404 Not Found** → Nginx config issue or build files missing
3. **CORS errors** → Backend CORS not configured
4. **Blank page** → Check browser console for errors

---

## ✅ Deployment Checklist

- [ ] EC2 instance launched with correct security groups
- [ ] SSH access working
- [ ] Repository cloned
- [ ] Dependencies installed (Node.js, Nginx)
- [ ] `.env.production` configured with backend URL
- [ ] Application built successfully
- [ ] Nginx configured and running
- [ ] Application accessible via browser
- [ ] Backend connection working
- [ ] CORS configured (open for MVP)

---

**🎉 Congratulations!** Your CFO Chatbot frontend is now deployed on AWS EC2!

For production use, remember to:
- Set up a domain name
- Enable HTTPS
- Restrict CORS to specific domains
- Set up monitoring and backups
