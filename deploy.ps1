# 🚀 Quick Deploy Script
# Run this to start the production server locally

Write-Host "🌱 AI Krishi Sahayak - Production Deployment" -ForegroundColor Green
Write-Host ""

# Check if gunicorn is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    & .\venv\Scripts\python.exe -c "import waitress" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing waitress (Windows production server)..." -ForegroundColor Yellow
        pip install waitress
    }
} catch {
    Write-Host "Installing waitress (Windows production server)..." -ForegroundColor Yellow
    pip install waitress
}

# Check environment variables
Write-Host ""
Write-Host "Checking environment variables..." -ForegroundColor Yellow
if (-not $env:GEMINI_API_KEY) {
    Write-Host "⚠️  GEMINI_API_KEY not set in environment!" -ForegroundColor Red
    Write-Host "Loading from .env file..." -ForegroundColor Yellow
    
    if (Test-Path .env) {
        Get-Content .env | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }
    } else {
        Write-Host "❌ .env file not found!" -ForegroundColor Red
        Write-Host "Please create .env file with GEMINI_API_KEY" -ForegroundColor Red
        exit 1
    }
}

# Set production environment
$env:FLASK_ENV = "production"

Write-Host ""
Write-Host "✅ Environment configured" -ForegroundColor Green
Write-Host ""
Write-Host "Starting production server (Waitress)..." -ForegroundColor Yellow
Write-Host "Server will run on: http://0.0.0.0:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start waitress (Windows-compatible production server)
& .\venv\Scripts\waitress-serve.exe --host=0.0.0.0 --port=5000 --threads=4 app:app
