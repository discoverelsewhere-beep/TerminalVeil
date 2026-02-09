"""
Terminal Veil - Web Edition (Sync version for Render)
Works on iPhone, Android, and Desktop browsers
"""
from flask import Flask, render_template, request, jsonify
import base64
import numpy as np
import cv2
from PIL import Image
import io
from datetime import datetime, timedelta

# Import your existing game files
from terminalveil.terminal import GameEngine
from terminalveil.camera_handler import CameraAnalyzer

app = Flask(__name__)

# Store games for each player (simple version)
games = {}
analyzers = {}
last_activity = {}  # Track last activity for session management

def get_or_create_session(session_id):
    """Get existing session or create new one"""
    if session_id not in games:
        games[session_id] = GameEngine()
        analyzers[session_id] = CameraAnalyzer()
    last_activity[session_id] = datetime.now()
    return games[session_id], analyzers[session_id]

def process_image(image_data, analyzer, mode='any'):
    """Process image data and return analysis result"""
    # Handle both base64 data URL and raw base64
    if ',' in image_data:
        image_data = image_data.split(',')[1]
    
    # Convert base64 to image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert to format OpenCV likes
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Analyze the image
    return analyzer.analyze_frame(image, mode)

@app.route('/')
def index():
    """Show the game page - create persistent session"""
    # Get existing session or create new
    session_id = request.cookies.get('session_id')
    
    if not session_id or session_id not in games:
        session_id = str(datetime.now().timestamp())
        games[session_id] = GameEngine()
        analyzers[session_id] = CameraAnalyzer()
    
    last_activity[session_id] = datetime.now()
    
    resp = app.make_response(render_template('index.html'))
    # Set cookie to expire in 7 days and persist across browser sessions
    resp.set_cookie('session_id', session_id, max_age=604800, httponly=True, samesite='Lax')
    return resp

@app.route('/command', methods=['POST'])
def command():
    """Handle typed commands"""
    session_id = request.cookies.get('session_id', 'default')
    engine, _ = get_or_create_session(session_id)
    
    data = request.json
    cmd = data.get('command', '')
    
    # Handle scan command specially
    if cmd.lower().startswith('scan'):
        return jsonify({
            'type': 'scan_request',
            'mode': cmd.lower().replace('scan', '').strip() or 'any'
        })
    
    # Process normal command
    response = engine.process_command(cmd)
    
    return jsonify({
        'type': 'text',
        'response': response,
        'level': engine.state['current_level'] + 1,
        'inventory': len(engine.state['inventory']),
        'victory': engine.check_victory()
    })

@app.route('/scan', methods=['POST'])
def scan():
    """Process camera image - auto-creates session if missing"""
    session_id = request.cookies.get('session_id', 'default')
    
    # Auto-create session if missing (instead of error)
    engine, analyzer = get_or_create_session(session_id)
    
    data = request.json
    image_data = data.get('image', '')
    mode = data.get('mode', 'any')
    
    if not image_data:
        return jsonify({'error': 'No image data received'})
    
    try:
        result = process_image(image_data, analyzer, mode)
        
        if 'error' in result:
            return jsonify({'error': result['error']})
        
        # Add to inventory
        result_text = engine.process_scan_result(result)
        
        # Check if it solves the puzzle
        success = engine.check_puzzle_solution(result)
        
        if success:
            advance_text = engine.advance_level()
            return jsonify({
                'success': True,
                'result': result_text,
                'advance': advance_text,
                'level': engine.state['current_level'] + 1,
                'total_levels': 13
            })
        else:
            # Get current level requirements for better feedback
            level = engine.get_current_level()
            req = level.get('requirement', {}) if level else {}
            
            # Build specific feedback message
            feedback_parts = ['Item archived.']
            
            if req.get('any'):
                feedback_parts.append('Calibration incomplete - scan again.')
            elif req.get('randomized'):
                feedback_parts.append('Does not match the required signature.')
            else:
                needs = []
                if 'color' in req:
                    needs.append(f"{req['color'].upper()} color")
                if 'qr_contains' in req:
                    needs.append(f"QR with '{req['qr_contains']}'")
                if 'shape' in req:
                    needs.append(f"{req['shape'].upper()} shape")
                if 'barcode' in req:
                    needs.append("barcode")
                
                if needs:
                    feedback_parts.append(f"Lock remains engaged. Need: {', '.join(needs)}")
            
            return jsonify({
                'success': False,
                'result': result_text,
                'hint': ' '.join(feedback_parts)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload for users who can't use camera"""
    session_id = request.cookies.get('session_id', 'default')
    
    # Auto-create session if missing
    engine, analyzer = get_or_create_session(session_id)
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'})
        
        file = request.files['file']
        mode = request.form.get('mode', 'any')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        # Read image from uploaded file
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Analyze
        result = analyzer.analyze_frame(image, mode)
        
        if 'error' in result:
            return jsonify({'error': result['error']})
        
        # Process result same as scan
        result_text = engine.process_scan_result(result)
        success = engine.check_puzzle_solution(result)
        
        if success:
            advance_text = engine.advance_level()
            return jsonify({
                'success': True,
                'result': result_text,
                'advance': advance_text,
                'level': engine.state['current_level'] + 1,
                'total_levels': 13
            })
        else:
            level = engine.get_current_level()
            req = level.get('requirement', {}) if level else {}
            
            feedback_parts = ['Item archived.']
            if req.get('any'):
                feedback_parts.append('Calibration incomplete - scan again.')
            elif req.get('randomized'):
                feedback_parts.append('Does not match the required signature.')
            else:
                needs = []
                if 'color' in req:
                    needs.append(f"{req['color'].upper()} color")
                if 'qr_contains' in req:
                    needs.append(f"QR with '{req['qr_contains']}'")
                if 'shape' in req:
                    needs.append(f"{req['shape'].upper()} shape")
                if 'barcode' in req:
                    needs.append("barcode")
                if needs:
                    feedback_parts.append(f"Lock remains engaged. Need: {', '.join(needs)}")
            
            return jsonify({
                'success': False,
                'result': result_text,
                'hint': ' '.join(feedback_parts)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/save', methods=['POST'])
def save():
    """Save game"""
    session_id = request.cookies.get('session_id', 'default')
    if session_id in games:
        success = games[session_id].save_manager.save(games[session_id].state)
        return jsonify({'saved': success})
    return jsonify({'saved': False})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(games),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Run on all network interfaces
    app.run(debug=True, host='0.0.0.0', port=10000)
