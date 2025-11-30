#!/bin/bash
# 🚀 Quick Deploy Script for Linux/Mac
# Run this to start the production server locally

echo "🌱 AI Krishi Sahayak - Production Deployment"
echo ""

# Check if gunicorn is installed
echo "Checking dependencies..."
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Check environment variables
echo ""
echo "Checking environment variables..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set in environment!"
    echo "Loading from .env file..."
    
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo "❌ .env file not found!"
        echo "Please create .env file with GEMINI_API_KEY"
        exit 1
    fi
fi

# Set production environment
export FLASK_ENV=production

echo ""
echo "✅ Environment configured"
echo ""
echo "Starting production server..."
echo "Server will run on: http://0.0.0.0:5000"
echo "Press Ctrl+C to stop"
echo ""

# Start gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 --log-level info app:app
