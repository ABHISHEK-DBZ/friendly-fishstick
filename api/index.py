# Vercel serverless function entry point
import sys
import os
from pathlib import Path

# Add parent directory to path to import app
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set environment to production
os.environ.setdefault('FLASK_ENV', 'production')

try:
    # Import Flask app
    from app import app
    
    # Export the Flask app for Vercel
    # Vercel expects either 'app' or 'handler'
    application = app
    
except Exception as e:
    # Fallback error handler
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return jsonify({
            'error': 'Application failed to initialize',
            'message': str(e),
            'type': type(e).__name__
        }), 500
    
    @app.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            'error': 'Application failed to initialize',
            'message': str(e),
            'type': type(e).__name__,
            'path': path
        }), 500
    
    application = app
