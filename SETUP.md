# Quick Setup Guide

## ⚡ Fast Track (5 Minutes)

### 1. Install Python Dependencies

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install packages (--pre flag is REQUIRED for Agent Framework)
pip install --pre -r requirements.txt
```

### 2. Configure API Keys

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your favorite editor
notepad .env
```

**Required API Keys:**

#### Option A: GitHub Models (Recommended - Free Tier)
```env
GITHUB_TOKEN=ghp_your_github_personal_access_token
```
Get your token: https://github.com/settings/tokens

#### Option B: Azure OpenAI
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_azure_key
```

#### Weather API (Optional but Recommended)
```env
OPENWEATHER_API_KEY=your_api_key
```
Sign up free: https://openweathermap.org/api

### 3. Test Installation

```powershell
# Run the demo
python main.py
```

### 4. Use Interactive CLI

```powershell
# Start interactive interface
python cli.py
```

---

## 🎓 Detailed Setup

### Prerequisites Check

```powershell
# Check Python version (must be 3.9+)
python --version

# Check pip
pip --version

# Check git (optional)
git --version
```

### Virtual Environment Setup

**Why?** Isolates project dependencies from your system Python.

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# You should see (venv) in your prompt
# (venv) PS C:\Users\Abhishek\PycharmProjects\ai agent>
```

**Deactivate later:**
```powershell
deactivate
```

### Install Dependencies Explained

The `requirements.txt` includes:

| Package | Purpose |
|---------|---------|
| `agent-framework-azure-ai` | Core multi-agent framework |
| `openai` | OpenAI SDK compatibility |
| `azure-ai-inference` | Azure AI integration |
| `pillow`, `opencv-python` | Image processing |
| `requests`, `beautifulsoup4` | Web scraping & APIs |
| `python-dotenv` | Environment variable management |
| `rich` | Beautiful CLI formatting |

**Install:**
```powershell
pip install --pre -r requirements.txt
```

⚠️ **Important:** The `--pre` flag is **required** because Agent Framework is in preview.

### API Keys Setup

#### GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `read:user`
   - ✅ `user:email`
4. Copy token (starts with `ghp_...`)
5. Paste into `.env`:
   ```env
   GITHUB_TOKEN=ghp_your_token_here
   ```

#### Azure OpenAI (Alternative)

1. Create Azure OpenAI resource in Azure Portal
2. Deploy `gpt-4o` model
3. Get endpoint and key from Azure Portal
4. Add to `.env`:
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your_key_here
   ```

#### OpenWeatherMap API

1. Sign up: https://openweathermap.org/appid
2. Get free API key
3. Add to `.env`:
   ```env
   OPENWEATHER_API_KEY=your_key_here
   ```

### Verify Setup

```powershell
# Check if config loads properly
python -c "from config import Config; print('Config loaded:', Config.GITHUB_TOKEN is not None)"

# Should print: Config loaded: True
```

---

## 🧪 Testing

### Basic Test

```powershell
python main.py
```

Expected output:
```
============================
🌾 AI KRISHI SAHAYAK
============================

📋 Demo User Profile Created
   User ID: farmer001
   ...
```

### Interactive Test

```powershell
python cli.py
```

Follow the menu:
1. Register new user
2. Upload an image
3. Get diagnosis

### With Sample Image

1. Download a plant disease image:
   - Visit: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
   - Or use any tomato/potato leaf image

2. Place it in `uploads/`:
   ```powershell
   # Create uploads directory if needed
   mkdir uploads
   
   # Copy your image
   copy C:\path\to\your\image.jpg uploads\sample_leaf.jpg
   ```

3. Run:
   ```powershell
   python main.py
   ```

---

## 🐛 Troubleshooting

### Issue: "Import agent_framework could not be resolved"

**Solution:**
```powershell
# Make sure you used --pre flag
pip install --pre agent-framework-azure-ai

# Verify installation
pip show agent-framework-azure-ai
```

### Issue: "No API credentials found"

**Solution:**
Check your `.env` file:
```powershell
# View .env contents (without exposing secrets)
python -c "from config import Config; print('GITHUB_TOKEN:', 'SET' if Config.GITHUB_TOKEN else 'NOT SET')"
```

### Issue: "ModuleNotFoundError: No module named 'PIL'"

**Solution:**
```powershell
pip install pillow
```

### Issue: Virtual environment not activating

**Solution (PowerShell execution policy):**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\Activate.ps1
```

### Issue: "Weather API error"

**Solution:**
- Weather is optional for demo
- System will continue without weather data
- Get free key at: https://openweathermap.org/api

---

## 📊 Verify Everything Works

### Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed with `--pre` flag
- [ ] `.env` file configured with API keys
- [ ] GitHub token or Azure OpenAI credentials set
- [ ] `python main.py` runs without errors
- [ ] `python cli.py` starts interactive interface

### Full System Test

```powershell
# Run all components
python -c "
from config import Config
from main import KrishiSahayakCoordinator
print('✅ Config loaded')
coordinator = KrishiSahayakCoordinator()
print('✅ Coordinator initialized')
print('✅ All agents ready')
print('✅ System is operational!')
"
```

---

## 🚀 Next Steps

1. **Get Sample Images**: Download plant disease datasets
2. **Customize Agents**: Modify agent instructions in agent files
3. **Add More Diseases**: Extend `Config.DISEASE_KNOWLEDGE_BASE`
4. **Build UI**: Create web interface with Flask/FastAPI
5. **Deploy**: Consider Azure App Service or AWS

---

## 📚 Additional Resources

- **Agent Framework Docs**: https://github.com/microsoft/agent-framework
- **GitHub Models**: https://github.com/marketplace/models
- **OpenAI API**: https://platform.openai.com/docs
- **Plant Disease Images**: https://www.kaggle.com/datasets

---

## 💡 Pro Tips

1. **Use GitHub Models First**: Free tier is perfect for testing
2. **Start with CLI**: Easier to test than building UI first
3. **Check Logs**: Errors are logged to `logs/` directory
4. **Monitor Costs**: If using Azure, track API usage
5. **Version Control**: Commit your changes regularly

---

## 🆘 Getting Help

**If you're stuck:**

1. Check error messages in terminal
2. Review `logs/` directory for detailed errors
3. Verify API keys are correct
4. Ensure all dependencies installed
5. Check GitHub Issues for similar problems

**For hackathon support:**
- GitHub Models Discord
- Hackathon Slack channel

---

## ✅ You're Ready!

Once all checks pass, you're ready to:
- Demo the system
- Record your video
- Submit to the hackathon

**Good luck! 🌾🚀**
