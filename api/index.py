# Vercel serverless function entry point
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set environment to production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('VERCEL', '1')  # Mark as Vercel environment

# Try to import and create app
_app = None
_error = None

try:
    from app import app as flask_app
    _app = flask_app
except Exception as e:
    _error = e
    import traceback
    _traceback = traceback.format_exc()

# Create WSGI application
if _app is not None:
    # Success - use the real app
    app = _app
    application = _app
else:
    # Failed - create error app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/health')
    @app.route('/')
    def health():
        return jsonify({
            'status': 'error',
            'error': str(_error),
            'type': type(_error).__name__,
            'traceback': _traceback,
            'message': 'Application failed to initialize'
        }), 500
    
    @app.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            'status': 'error',
            'error': str(_error),
            'type': type(_error).__name__,
            'traceback': _traceback,
            'path': path,
            'message': 'Application failed to initialize'
        }), 500
    
    application = app
