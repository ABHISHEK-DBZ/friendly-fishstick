"""
Flask Web Application for AI Krishi Sahayak
Modern web interface for plant disease diagnosis
"""
import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import secrets

from main import KrishiSahayakCoordinator
from agents.memory_agent import MemoryAgent
from config import Config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = Config.UPLOADS_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
else:
    app.config['DEBUG'] = True

# Ensure upload directory exists
Config.UPLOADS_DIR.mkdir(exist_ok=True)

# Initialize coordinator and memory agent lazily
coordinator = None
memory_agent = None

def get_coordinator():
    global coordinator
    if coordinator is None:
        coordinator = KrishiSahayakCoordinator()
    return coordinator

def get_memory_agent():
    global memory_agent
    if memory_agent is None:
        memory_agent = MemoryAgent()
    return memory_agent

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        name = data.get('name')
        location = data.get('location')
        phone = data.get('phone', '')
        
        try:
            get_memory_agent().register_user(
                user_id=user_id,
                name=name,
                location=location,
                phone=phone
            )
            session['user_id'] = user_id
            session['name'] = name
            session['location'] = location
            return jsonify({'success': True, 'message': f'Welcome, {name}!'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        
        user_info = get_memory_agent().get_user_info(user_id)
        if user_info:
            session['user_id'] = user_info['user_id']
            session['name'] = user_info['name']
            session['location'] = user_info['location']
            return jsonify({'success': True, 'message': f'Welcome back, {user_info["name"]}!'})
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/diagnose', methods=['GET', 'POST'])
def diagnose():
    """Plant disease diagnosis"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{session['user_id']}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            location = request.form.get('location', session.get('location', ''))
            additional_info = request.form.get('additional_info', '')
            
            try:
                # Run diagnosis asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    get_coordinator().diagnose_plant(
                        image_path=filepath,
                        user_id=session['user_id'],
                        location=location,
                        additional_context=additional_info
                    )
                )
                loop.close()
                
                return jsonify({
                    'success': True,
                    'result': result
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        else:
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    
    return render_template('diagnose.html', user=session)

@app.route('/history')
def history():
    """View diagnosis history"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_history = get_memory_agent().get_user_history(session['user_id'])
    return render_template('history.html', history=user_history, user=session)

@app.route('/followup')
def followup():
    """View follow-up schedule"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    followups = get_memory_agent().get_pending_followups(session['user_id'])
    return render_template('followup.html', followups=followups, user=session)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/api/session/<session_id>')
def get_session(session_id):
    """Get session details API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    session_data = get_memory_agent().get_session_details(session_id)
    if session_data:
        return jsonify(session_data)
    else:
        return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
