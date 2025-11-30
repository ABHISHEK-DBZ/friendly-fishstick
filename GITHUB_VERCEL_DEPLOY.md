# 🚀 GitHub & Vercel Deployment Guide

## Step 1: Initialize Git Repository

```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Krishi Sahayak - Plant Disease Detection System"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-krishi-sahayak`
3. Description: `AI-powered plant disease detection system for farmers`
4. Keep it Public (for hackathon submission)
5. **Do NOT** initialize with README (we have one)
6. Click "Create repository"

## Step 3: Push to GitHub

```powershell
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ai-krishi-sahayak.git

# Push code
git branch -M main
git push -u origin main
```

## Step 4: Deploy to Vercel

### Option A: Using Vercel CLI (Recommended)

```powershell
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? ai-krishi-sahayak
# - Directory? ./
# - Override settings? No
```

### Option B: Using Vercel Dashboard

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository: `ai-krishi-sahayak`
4. Configure:
   - Framework Preset: **Other**
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

5. Add Environment Variables:
   ```
   GEMINI_API_KEY = your_gemini_api_key_here
   FLASK_ENV = production
   SECRET_KEY = your_generated_secret_key
   ```

6. Click "Deploy"

## Step 5: Configure Environment Variables

In Vercel Dashboard:
1. Go to Project Settings → Environment Variables
2. Add these variables:

```
GEMINI_API_KEY = AIzaSy...  (your API key)
FLASK_ENV = production
SECRET_KEY = (generate using: python -c "import secrets; print(secrets.token_hex(32))")
```

## Step 6: Test Deployment

Once deployed, Vercel will give you a URL like:
```
https://ai-krishi-sahayak.vercel.app
```

Test it:
```powershell
# Health check
curl https://ai-krishi-sahayak.vercel.app/health

# Should return: {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

## Automatic Deployments

Every time you push to GitHub, Vercel will automatically deploy:

```powershell
# Make changes
git add .
git commit -m "Add new feature"
git push origin main

# Vercel automatically deploys!
```

## Custom Domain (Optional)

1. In Vercel Dashboard → Domains
2. Add your domain: `krishi-sahayak.com`
3. Follow DNS configuration steps

## Troubleshooting

### Issue: Module not found
**Solution:** Ensure all dependencies in `requirements.txt`
```powershell
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Issue: Database not persisting
**Solution:** Vercel is serverless, use external database
- Upgrade to Vercel Pro for persistent storage
- Or use external PostgreSQL (Supabase, Neon, etc.)

### Issue: Large file upload errors
**Solution:** Vercel has 4.5MB request limit for free tier
- Compress images before upload
- Or upgrade to Pro for 50MB limit

### Issue: Cold starts (slow first load)
**Solution:** This is normal for serverless
- First request after idle: 3-5 seconds
- Subsequent requests: <1 second
- Upgrade to Pro for better performance

## Cost Estimate

### Vercel Free Tier:
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Unlimited deployments
- ✅ Custom domains
- ⚠️ 4.5MB request limit
- ⚠️ Cold starts

### Vercel Pro ($20/month):
- ✅ 1TB bandwidth
- ✅ 50MB request limit
- ✅ Better performance
- ✅ Priority support

## GitHub Actions (Optional - CI/CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## Files Created for Deployment:

- ✅ `vercel.json` - Vercel configuration
- ✅ `api/index.py` - Serverless function entry point
- ✅ `.gitignore` - Files to exclude from Git
- ✅ `uploads/.gitkeep` - Keep empty directory
- ✅ `logs/.gitkeep` - Keep empty directory

## Quick Commands Summary

```powershell
# 1. Commit and push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Deploy to Vercel
vercel --prod

# 3. Check deployment
curl https://your-app.vercel.app/health
```

## Success! 🎉

Your app is now live at:
- **GitHub:** https://github.com/YOUR_USERNAME/ai-krishi-sahayak
- **Vercel:** https://ai-krishi-sahayak.vercel.app

Share these links in your hackathon submission! 🌱
