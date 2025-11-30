# 🚀 Deployment Guide - AI Krishi Sahayak

## Deployment Options

### Option 1: Azure App Service (Recommended for Production)

#### Prerequisites
- Azure account with active subscription
- Azure CLI installed (`az` command)
- Git repository

#### Steps

1. **Prepare the application**
```powershell
# Create requirements.txt for production
pip freeze > requirements.txt

# Create Procfile for Azure
echo "web: gunicorn app:app" > Procfile

# Install gunicorn
pip install gunicorn
```

2. **Create Azure resources**
```bash
# Login to Azure
az login

# Create resource group
az group create --name ai-krishi-sahayak-rg --location eastus

# Create App Service plan
az appservice plan create --name ai-krishi-plan --resource-group ai-krishi-sahayak-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group ai-krishi-sahayak-rg --plan ai-krishi-plan --name ai-krishi-sahayak --runtime "PYTHON:3.11"
```

3. **Configure environment variables**
```bash
az webapp config appsettings set --resource-group ai-krishi-sahayak-rg --name ai-krishi-sahayak --settings \
    GEMINI_API_KEY="your_api_key" \
    FLASK_ENV="production" \
    SECRET_KEY="your_secret_key"
```

4. **Deploy from Git**
```bash
# Configure deployment from local Git
az webapp deployment source config-local-git --name ai-krishi-sahayak --resource-group ai-krishi-sahayak-rg

# Get deployment credentials
az webapp deployment list-publishing-credentials --name ai-krishi-sahayak --resource-group ai-krishi-sahayak-rg

# Push code
git remote add azure <GIT_URL>
git push azure main
```

---

### Option 2: Docker Deployment

#### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p data uploads logs

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "app:app"]
```

#### Build and run
```bash
# Build image
docker build -t ai-krishi-sahayak .

# Run container
docker run -d -p 5000:5000 \
  -e GEMINI_API_KEY="your_api_key" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/uploads \
  ai-krishi-sahayak
```

---

### Option 3: Azure Container Instances

```bash
# Create container registry
az acr create --resource-group ai-krishi-sahayak-rg --name aikrishiregistry --sku Basic

# Build and push image
az acr build --registry aikrishiregistry --image ai-krishi-sahayak:v1 .

# Deploy to ACI
az container create \
  --resource-group ai-krishi-sahayak-rg \
  --name ai-krishi-sahayak-container \
  --image aikrishiregistry.azurecr.io/ai-krishi-sahayak:v1 \
  --cpu 2 --memory 4 \
  --registry-login-server aikrishiregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label ai-krishi-sahayak \
  --ports 5000 \
  --environment-variables GEMINI_API_KEY=your_api_key
```

---

### Option 4: Heroku (Quick Deploy)

1. **Install Heroku CLI**
```bash
# Windows
choco install heroku-cli

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Create Heroku app**
```bash
heroku login
heroku create ai-krishi-sahayak

# Add buildpack
heroku buildpacks:set heroku/python
```

3. **Create Procfile**
```
web: gunicorn app:app
```

4. **Configure environment**
```bash
heroku config:set GEMINI_API_KEY=your_api_key
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your_secret_key
```

5. **Deploy**
```bash
git push heroku main
heroku open
```

---

### Option 5: Local Production Server

#### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 300 app:app
```

#### Using Waitress (Windows-friendly)
```powershell
# Install waitress
pip install waitress

# Run server
waitress-serve --host=0.0.0.0 --port=5000 --call app:app
```

---

## Production Configuration

### 1. Create production config file

**config_prod.py**
```python
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = '/app/uploads'
    
    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS
    CORS_ORIGINS = ['https://yourdomain.com']
```

### 2. Update app.py for production

```python
import os

# Load production config if in production
if os.environ.get('FLASK_ENV') == 'production':
    from config_prod import ProductionConfig
    app.config.from_object(ProductionConfig)
else:
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['DEBUG'] = True
```

---

## Environment Variables Required

Create these in your deployment environment:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=generate_random_secret_key
FLASK_ENV=production
DATABASE_URL=sqlite:///data/farm_memory.db  # Or PostgreSQL URL
UPLOAD_FOLDER=/app/uploads
MAX_UPLOAD_SIZE=16777216
```

---

## Security Checklist

- [ ] Set strong SECRET_KEY (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Set DEBUG=False in production
- [ ] Use HTTPS (enable SSL certificates)
- [ ] Configure CORS properly
- [ ] Set secure cookie flags
- [ ] Implement rate limiting
- [ ] Add authentication middleware
- [ ] Sanitize file uploads
- [ ] Use environment variables for secrets
- [ ] Enable logging and monitoring
- [ ] Set up backup for database
- [ ] Configure firewall rules
- [ ] Implement API key rotation

---

## Performance Optimization

### 1. Add Redis caching
```bash
pip install redis flask-caching

# In app.py
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})
```

### 2. Enable CDN for static files
```python
# Serve static files from Azure Blob Storage or AWS S3
app.config['STATIC_URL'] = 'https://cdn.yourdomain.com/static/'
```

### 3. Database optimization
```python
# Use PostgreSQL instead of SQLite for production
# DATABASE_URL=postgresql://user:pass@host/dbname
```

---

## Monitoring & Logging

### Azure Application Insights
```python
from applicationinsights.flask.ext import AppInsights

app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = os.environ.get('APPINSIGHTS_KEY')
appinsights = AppInsights(app)
```

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200
```

---

## Scaling Recommendations

### For 100-1000 users/day:
- Azure App Service B1 tier
- 1 instance, 2 workers
- SQLite database

### For 1000-10000 users/day:
- Azure App Service S1 tier
- 2-3 instances with load balancer
- PostgreSQL database
- Redis cache

### For 10000+ users/day:
- Azure App Service P1V2 tier
- Auto-scaling (3-10 instances)
- Azure Database for PostgreSQL
- Redis cache cluster
- CDN for static files
- Azure Storage for uploads

---

## Post-Deployment Testing

```bash
# Test health endpoint
curl https://your-app.azurewebsites.net/health

# Test registration
curl -X POST https://your-app.azurewebsites.net/register \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test001","name":"Test User","location":"Mumbai"}'

# Test diagnosis endpoint
curl -X POST https://your-app.azurewebsites.net/diagnose \
  -F "image=@test_leaf.jpg" \
  -F "location=Mumbai"
```

---

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies in requirements.txt
2. **Database locked**: Switch to PostgreSQL for production
3. **Timeout errors**: Increase worker timeout in gunicorn
4. **Memory issues**: Scale up instance size or add workers
5. **API rate limits**: Implement request queuing

### Debug commands
```bash
# Check logs (Azure)
az webapp log tail --name ai-krishi-sahayak --resource-group ai-krishi-sahayak-rg

# Check logs (Heroku)
heroku logs --tail --app ai-krishi-sahayak

# SSH into container (Azure)
az webapp ssh --name ai-krishi-sahayak --resource-group ai-krishi-sahayak-rg
```

---

## CI/CD Pipeline

### GitHub Actions Example

**.github/workflows/deploy.yml**
```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/
    
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: ai-krishi-sahayak
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

---

## Cost Estimation (Azure)

| Tier | Monthly Cost | Capacity |
|------|-------------|----------|
| Free (F1) | $0 | 60 CPU min/day, 1GB RAM |
| Basic (B1) | ~$13 | 100 ACU, 1.75GB RAM |
| Standard (S1) | ~$70 | 100 ACU, 1.75GB RAM, Auto-scale |
| Premium (P1V2) | ~$150 | 210 ACU, 3.5GB RAM, Advanced features |

Additional costs:
- PostgreSQL: $5-50/month
- Redis Cache: $15-100/month
- Storage: $1-5/month
- Bandwidth: $0.05/GB

---

## Support

For deployment issues:
- Check [Azure Documentation](https://docs.microsoft.com/azure)
- Review [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- Open issue on GitHub

**Deployed successfully? Share your deployment at**: https://github.com/yourusername/ai-krishi-sahayak
