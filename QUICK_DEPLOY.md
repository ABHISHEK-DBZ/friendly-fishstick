# 🚀 Quick Deployment Guide

## Deploy in 5 Minutes!

### Option 1: Local Production Server (Recommended for Testing)

**Windows:**
```powershell
.\deploy.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

Your app will be running at: **http://localhost:5000**

---

### Option 2: Docker (Best for Cloud Deployment)

```bash
# Build image
docker build -t ai-krishi-sahayak .

# Run container
docker run -d -p 5000:5000 \
  -e GEMINI_API_KEY="your_api_key_here" \
  --name krishi-app \
  ai-krishi-sahayak

# Check logs
docker logs -f krishi-app

# Stop
docker stop krishi-app
```

Access at: **http://localhost:5000**

---

### Option 3: Azure App Service (Production Ready)

```bash
# Install Azure CLI
# Windows: choco install azure-cli
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name ai-krishi-rg --location eastus

# Create app service
az webapp up --name ai-krishi-sahayak-app --resource-group ai-krishi-rg --runtime "PYTHON:3.11"

# Set environment variables
az webapp config appsettings set \
  --resource-group ai-krishi-rg \
  --name ai-krishi-sahayak-app \
  --settings GEMINI_API_KEY="your_api_key_here" FLASK_ENV="production"
```

Your app will be at: **https://ai-krishi-sahayak-app.azurewebsites.net**

---

### Option 4: Heroku (Easiest Cloud Deploy)

```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create ai-krishi-sahayak

# Add Python buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set GEMINI_API_KEY=your_api_key_here
heroku config:set FLASK_ENV=production

# Deploy
git add .
git commit -m "Ready for deployment"
git push heroku main

# Open app
heroku open
```

---

## Environment Variables Required

Create a `.env` file or set these in your deployment platform:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=generate_random_secret_key
FLASK_ENV=production
```

Generate SECRET_KEY:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Verify Deployment

Test your deployment:

```bash
# Health check
curl http://your-app-url/health

# Should return:
# {"status":"healthy","timestamp":"2025-11-30T...","version":"1.0.0"}
```

---

## What's Included

✅ **Procfile** - For Heroku deployment
✅ **Dockerfile** - For Docker/container deployment  
✅ **deploy.ps1** - Windows production server script
✅ **deploy.sh** - Linux/Mac production server script
✅ **requirements.txt** - All dependencies including gunicorn
✅ **Health endpoint** - `/health` for monitoring
✅ **Production config** - Secure cookies, proper secrets

---

## Scaling

### For Small Traffic (100-1000 users/day):
- Use Option 1 (Local) or Option 4 (Heroku Free Tier)
- 1 worker, 512MB RAM

### For Medium Traffic (1000-10000 users/day):
- Use Option 3 (Azure App Service B1)
- 2 workers, 1.75GB RAM
- Cost: ~$13/month

### For High Traffic (10000+ users/day):
- Azure App Service S1 with auto-scaling
- 4+ workers, load balancer
- PostgreSQL database
- Cost: ~$70-150/month

---

## Troubleshooting

**Import errors:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
```bash
# Change port in deploy script from 5000 to 8080
```

**Database errors:**
```bash
# Ensure data/ directory exists
mkdir data
```

**API key errors:**
```bash
# Verify .env file has GEMINI_API_KEY
cat .env | grep GEMINI_API_KEY
```

---

## Next Steps

1. ✅ Deploy using one of the options above
2. 📱 Test with plant images
3. 🔒 Set up SSL certificate (automatic with Azure/Heroku)
4. 📊 Configure monitoring and logging
5. 🚀 Share with farmers!

---

## Support

- 📖 Full guide: See `DEPLOYMENT.md`
- 🐛 Issues: Open on GitHub
- 💬 Questions: Check documentation

**Happy Deploying! 🌱**
