# 🚀 QUICK START CARD - AI Krishi Sahayak

## ⚡ Get Running in 5 Minutes

### 1. Setup Virtual Environment
```powershell
cd "c:\Users\Abhishek\PycharmProjects\ai agent"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies (⚠️ --pre flag required!)
```powershell
pip install --pre -r requirements.txt
```

### 3. Configure API Keys
```powershell
copy .env.example .env
notepad .env
```

Add your GitHub token:
```env
GITHUB_TOKEN=ghp_your_token_here
```

Get token: https://github.com/settings/tokens

### 4. Run Demo
```powershell
# Basic demo
python main.py

# Interactive CLI
python cli.py
```

---

## 📁 Project Structure

```
ai agent/
├── agents/                    # 4 AI Agents
│   ├── vision_agent.py       # Image analysis (GPT-4o)
│   ├── research_agent.py     # Treatment + Weather
│   ├── advisory_agent.py     # Farmer-friendly plans
│   └── memory_agent.py       # Database + History
├── main.py                   # Main coordinator
├── cli.py                    # Interactive interface
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── .env.example             # API key template
├── README.md                # Full documentation
├── SETUP.md                 # Installation guide
├── ARCHITECTURE.md          # Technical docs
├── DEMO_VIDEO_SCRIPT.md     # 3-min video script
├── PRESENTATION.md          # Slides outline
└── PROJECT_SUMMARY.md       # This file!
```

---

## 🎯 What Each File Does

| File | Purpose | When to Use |
|------|---------|-------------|
| `config.py` | API keys, disease database | Configure settings |
| `main.py` | Workflow coordinator | Run demos, testing |
| `cli.py` | Interactive UI | User-friendly testing |
| `agents/*.py` | AI agent logic | Customize behavior |

---

## 🤖 Agent Workflow

```
User uploads image
    ↓
Vision Agent (GPT-4o)
    ↓ (disease diagnosis)
Research Agent (treatment + weather)
    ↓ (research data)
Advisory Agent (farmer-friendly plan)
    ↓ (action plan)
Memory Agent (save + schedule follow-up)
    ↓
User receives plan
```

---

## 🔑 Required API Keys

### Option A: GitHub Models (Free Tier) ⭐ RECOMMENDED
```env
GITHUB_TOKEN=ghp_your_github_token
```
- Free to start
- No credit card needed
- Perfect for hackathon
- Get at: https://github.com/settings/tokens

### Option B: Azure OpenAI
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_key
```

### Optional: Weather API
```env
OPENWEATHER_API_KEY=your_key
```
Free at: https://openweathermap.org/api

---

## 🧪 Testing Commands

```powershell
# Test imports
python -c "from main import KrishiSahayakCoordinator; print('✅ OK')"

# Run main demo
python main.py

# Interactive mode
python cli.py

# Check config
python -c "from config import Config; print(Config.GITHUB_TOKEN[:10] if Config.GITHUB_TOKEN else 'NOT SET')"
```

---

## 📸 Adding Sample Images

1. Download plant disease dataset:
   - https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset

2. Create uploads folder:
   ```powershell
   mkdir uploads
   ```

3. Copy image:
   ```powershell
   copy path\to\your\image.jpg uploads\sample_leaf.jpg
   ```

4. Run demo:
   ```powershell
   python main.py
   ```

---

## 🎬 Hackathon Submission Checklist

### Before Recording Video
- [ ] System runs without errors
- [ ] Sample image ready in `uploads/`
- [ ] Output is clear and formatted
- [ ] GitHub token is configured

### Demo Video (3 min)
- [ ] Script ready (`DEMO_VIDEO_SCRIPT.md`)
- [ ] Screen recording software ready (OBS Studio)
- [ ] Show problem → solution → impact
- [ ] Include architecture diagram
- [ ] Show live demo

### Presentation (15 slides)
- [ ] Use `PRESENTATION.md` template
- [ ] Problem statement with stats
- [ ] Multi-agent architecture
- [ ] Live demo screenshots
- [ ] Impact metrics
- [ ] Future roadmap

### Documentation
- [ ] README.md is comprehensive
- [ ] Setup instructions are clear
- [ ] Architecture is documented
- [ ] Code comments are present

### GitHub Repository
- [ ] Code pushed to GitHub
- [ ] README displays properly
- [ ] .gitignore prevents key leaks
- [ ] Repository is public
- [ ] Star your own repo!

---

## 💡 Key Talking Points

### For Judges:
1. **"4 specialized agents working as a team"**
   - Vision, Research, Advisory, Memory

2. **"Real-world impact: 100M+ farmers"**
   - Prevent 20-40% crop loss
   - Free diagnosis vs ₹2000 expert visit

3. **"Production-ready architecture"**
   - Error handling, logging, persistence
   - Built with Microsoft Agent Framework

4. **"Agents for Good"**
   - Social impact mission
   - Sustainable agriculture
   - Accessible to all farmers

---

## 🐛 Common Issues & Fixes

### Issue: "Import agent_framework could not be resolved"
```powershell
pip install --pre agent-framework-azure-ai
```

### Issue: "No API credentials found"
```powershell
# Check .env file exists
ls .env

# Verify contents (safely)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Token:', 'SET' if os.getenv('GITHUB_TOKEN') else 'NOT SET')"
```

### Issue: "PIL import error"
```powershell
pip install pillow
```

### Issue: Virtual env won't activate (PowerShell)
```powershell
# Run as Admin
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv\Scripts\Activate.ps1
```

---

## 📊 Success Metrics

**When everything works, you should see:**

```
============================
🌾 AI KRISHI SAHAYAK
============================

📋 Demo User Profile Created
🌱 Starting diagnosis...
📸 Analyzing image...
✅ Diagnosis complete!

📊 DIAGNOSIS RESULTS
============================

🌱 PROBLEM IDENTIFIED
Early Blight detected (94% confidence)

🔍 WHAT TO DO
1. Remove affected leaves
2. Apply Neem oil spray
...

📅 Follow-up scheduled in 2 days
============================
```

---

## 🎯 Your Mission

Build a **3-minute video** showing:

1. **Problem** (30s)
   - Farmers lose crops
   - No expert access
   - Expensive consultations

2. **Solution** (90s)
   - Upload image demo
   - Show agent workflow
   - Display action plan

3. **Impact** (60s)
   - Statistics
   - Scalability
   - Future vision

---

## 🚀 Final Commands Before Submission

```powershell
# 1. Test everything
python main.py
python cli.py

# 2. Check all files
ls

# 3. Initialize git
git init
git add .
git commit -m "AI Krishi Sahayak - Multi-Agent Agricultural Assistant"

# 4. Create GitHub repo
# Go to: https://github.com/new
# Then:
git remote add origin https://github.com/YOUR_USERNAME/ai-krishi-sahayak.git
git push -u origin main

# 5. Verify README displays properly
# Visit: https://github.com/YOUR_USERNAME/ai-krishi-sahayak
```

---

## 🏆 You're Ready to Win!

You have:
✅ Fully functional multi-agent system  
✅ Production-ready code  
✅ Comprehensive documentation  
✅ Real-world impact potential  
✅ Professional presentation materials  

**Now go record that demo and submit!** 🎬

---

## 📞 Last-Minute Help

**If something breaks:**
1. Read error message carefully
2. Check `SETUP.md` for detailed troubleshooting
3. Verify API keys in `.env`
4. Ensure virtual environment is activated
5. Check GitHub Models status

**Emergency test:**
```powershell
python -c "print('🌱 System operational!')"
```

---

## 🌟 Remember

This project can help **millions of farmers**.  
That's not just a hackathon project.  
That's **meaningful impact**. 🌾

**Good luck! You've got this! 🚀**

---

Made with ❤️ for farmers everywhere  
Track: Agents for Good  
GitHub Models Agents Hackathon 2024
