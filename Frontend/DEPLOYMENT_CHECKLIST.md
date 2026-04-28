# ✅ AWS EC2 Deployment Checklist

## Pre-Deployment

- [ ] AWS account created and accessible
- [ ] SSH key pair (.pem file) downloaded
- [ ] Backend API URL ready (or will configure later)
- [ ] Repository accessible (GitHub/GitLab)

## EC2 Setup

- [ ] EC2 instance launched (Ubuntu 22.04 LTS)
- [ ] Instance type selected (t2.small recommended)
- [ ] Security groups configured:
  - [ ] SSH (port 22) - Your IP
  - [ ] HTTP (port 80) - 0.0.0.0/0
  - [ ] HTTPS (port 443) - 0.0.0.0/0 (optional)
- [ ] Public IP noted down
- [ ] SSH connection tested

## Deployment

- [ ] Connected to EC2 via SSH
- [ ] Repository cloned
- [ ] deploy.sh made executable (`chmod +x deploy.sh`)
- [ ] Deployment script run (`sudo ./deploy.sh`)
- [ ] No errors during deployment

## Configuration

- [ ] `.env.production` updated with backend URL
- [ ] Application rebuilt (`npm run build`)
- [ ] Build files copied to `/var/www/cfo-chatbot/`
- [ ] Nginx restarted (`sudo systemctl restart nginx`)

## Verification

- [ ] Application accessible at `http://YOUR_EC2_IP`
- [ ] Page loads without errors
- [ ] Browser console checked (F12)
- [ ] Backend connection working (if backend is running)
- [ ] CORS working (no CORS errors in console)

## Post-Deployment (Optional)

- [ ] Domain name configured (if applicable)
- [ ] HTTPS/SSL certificate installed (for production)
- [ ] Firewall configured (`ufw`)
- [ ] Monitoring set up
- [ ] Backup strategy planned

## Files Created

✅ **nginx.conf** - Nginx configuration with CORS enabled
✅ **deploy.sh** - Automated deployment script
✅ **.env.example** - Environment template
✅ **.env.production** - Production environment config
✅ **AWS_DEPLOYMENT_GUIDE.md** - Complete deployment guide
✅ **DEPLOYMENT_QUICKSTART.md** - Quick 5-minute guide
✅ **DEPLOYMENT_CHECKLIST.md** - This checklist

## CORS Configuration

✅ CORS is configured in `nginx.conf` to allow all origins (`*`)
✅ Suitable for MVP/testing
⚠️  For production, restrict to specific domains

## Quick Commands Reference

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Deploy
sudo ./deploy.sh

# Update backend URL
nano .env.production
npm run build
sudo cp -r build/* /var/www/cfo-chatbot/
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx

# View logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

## Support

- Full guide: [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md)
- Quick guide: [DEPLOYMENT_QUICKSTART.md](./DEPLOYMENT_QUICKSTART.md)
- Troubleshooting section in AWS_DEPLOYMENT_GUIDE.md

---

**Ready to deploy?** Start with [DEPLOYMENT_QUICKSTART.md](./DEPLOYMENT_QUICKSTART.md)!
