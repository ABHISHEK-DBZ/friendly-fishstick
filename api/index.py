# Vercel serverless function entry point
import sys
from pathlib import Path

# Add parent directory to path to import app
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import app

# Export the Flask app for Vercel
app = app
