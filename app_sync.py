"""
Terminal Veil - Web Edition with Extreme Difficulty Support
"""
from flask import Flask, render_template, request, jsonify
import base64
import numpy as np
import cv2
from PIL import Image
import io
from datetime import datetime, timedelta

from terminalveil.terminal import GameEngine
from terminalveil.camera_handler import CameraAnalyzer

app = Flask(__name__)

games = {}
analyzers = {}
last_activity = {}

def get_or_create_session(session_id):
    if session_id not in games:
        games[session_id] = GameEngine()
        analyzers[session_id] = CameraAnalyzer()
    last_activity[session_id] = datetime.now()
    return games[session_id], analyzers[session_id]

@app.route('/')
def index():
    session_id = request.cookies.get('session_id')
    if not session_id or session_id not in games:
        session_id = str(datetime.now().timestamp())
        games[session_id] = GameEngine()
        analyzers[session_id] = CameraAnalyzer()
    
    last_activity[session_id] = datetime.now()
    
    resp = app.make_response(render_template('index.html'))
    resp.set_cookie('session_id', session_id, max_age=604800, httponly=True, samesite='Lax')
    return resp

@app.route('/command', methods=['POST'])
def command():
    session_id = request.cookies.get('session_id', 'default')
    engine, _ = get_or_create_session(session_id)
    
    data = request.json
    cmd = data.get('command', '')
    
    if cmd.lower().startswith('scan'):
        return jsonify({
            'type': 'scan_request',
            'mode': cmd.lower().replace('scan', '').strip() or 'any'
        })
    
    response = engine.process_command(cmd)
    
    return jsonify({
        'type': 'text',
        'response': response,
        'level': engine.state['current_level'] + 1,
        'inventory': len(engine.state['inventory']),
        'victory': engine.check_victory()
    })

def process_scan_common(engine, analyzer, image_data, mode='any'):
    """Common scan processing for both camera and upload"""
    if ',' in image_data:
        image_data = image_data.split(',')[1]
    
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # For simultaneous detection (Level 11), try to detect multiple things
    level = engine.get_current_level()
    req = level.get('requirement', {}) if level else {}
    
    if req.get('simultaneous'):
        # Try to detect both required items
        result = analyzer.analyze_frame_simultaneous(image, req['simultaneous'])
    else:
        result = analyzer.analyze_frame(image, mode)
    
    return result

@app.route('/scan', methods=['POST'])
def scan():
    session_id = request.cookies.get('session_id', 'default')
    engine, analyzer = get_or_create_session(session_id)
    
    data = request.json
    image_data = data.get('image', '')
    mode = data.get('mode', 'any')
    
    if not image_data:
        return jsonify({'error': 'No image data'})
    
    try:
        result = process_scan_common(engine, analyzer, image_data, mode)
        
        if 'error' in result:
            return jsonify({'error': result['error']})
        
        success = engine.check_puzzle_solution(result)
        result_text = engine.process_scan_result(result, add_to_inventory=success)
        
        if success:
            advance_text = engine.advance_level()
            return jsonify({
                'success': True,
                'result': result_text,
                'advance': advance_text,
                'level': engine.state['current_level'] + 1,
                'total_levels': 13,
                'reset': False
            })
        else:
            level = engine.get_current_level()
            req = level.get('requirement', {}) if level else {}
            
            # Check if sequence was reset
            was_reset = len(engine.state['scans_this_level']) == 0 and (
                req.get('sequence') or req.get('complex_sequence')
            ) and engine.state['attempts_count'].get(engine.state['current_level'], 0) > 0
            
            if was_reset:
                feedback = "[RESET] Sequence broken! Starting over."
            else:
                feedback = "Analysis complete. "
                if req.get('sequence'):
                    progress = engine.state['scans_this_level']
                    target = req['sequence']
                    feedback += f"Progress: {len(progress)}/{len(target)}"
                elif req.get('complex_sequence'):
                    progress = engine.state['scans_this_level']
                    target = req['complex_sequence']
                    feedback += f"Progress: {len(progress)}/{len(target)}"
                elif req.get('simultaneous'):
                    items = req['simultaneous']
                    feedback += f"Need BOTH: {items[0].upper()} + {items[1].upper()} in ONE frame!"
                else:
                    needs = []
                    if 'color' in req:
                        needs.append(f"{req['color'].upper()} color")
                    if 'qr_contains' in req:
                        needs.append(f"QR '{req['qr_contains']}'")
                    if 'shape' in req:
                        needs.append(f"{req['shape'].upper()} shape")
                    if 'barcode' in req:
                        needs.append("barcode")
                    if needs:
                        feedback += f"Lock engaged. Need: {', '.join(needs)}"
            
            return jsonify({
                'success': False,
                'result': result_text,
                'hint': feedback,
                'reset': was_reset
            })
            
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/upload', methods=['POST'])
def upload():
    session_id = request.cookies.get('session_id', 'default')
    engine, analyzer = get_or_create_session(session_id)
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'})
        
        file = request.files['file']
        mode = request.form.get('mode', 'any')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        level = engine.get_current_level()
        req = level.get('requirement', {}) if level else {}
        
        if req.get('simultaneous'):
            result = analyzer.analyze_frame_simultaneous(image, req['simultaneous'])
        else:
            result = analyzer.analyze_frame(image, mode)
        
        if 'error' in result:
            return jsonify({'error': result['error']})
        
        success = engine.check_puzzle_solution(result)
        result_text = engine.process_scan_result(result, add_to_inventory=success)
        
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
            
            was_reset = len(engine.state['scans_this_level']) == 0 and (
                req.get('sequence') or req.get('complex_sequence')
            ) and engine.state['attempts_count'].get(engine.state['current_level'], 0) > 0
            
            if was_reset:
                feedback = "[RESET] Sequence broken! Starting over."
            else:
                feedback = "Analysis complete."
                if req.get('sequence'):
                    progress = engine.state['scans_this_level']
                    target = req['sequence']
                    feedback += f" Progress: {len(progress)}/{len(target)}"
                elif req.get('complex_sequence'):
                    progress = engine.state['scans_this_level']
                    target = req['complex_sequence']
                    feedback += f" Progress: {len(progress)}/{len(target)}"
                elif req.get('simultaneous'):
                    items = req['simultaneous']
                    feedback += f" Need BOTH: {items[0].upper()} + {items[1].upper()} in ONE frame!"
                else:
                    needs = []
                    if 'color' in req:
                        needs.append(f"{req['color'].upper()} color")
                    if 'qr_contains' in req:
                        needs.append(f"QR '{req['qr_contains']}'")
                    if 'shape' in req:
                        needs.append(f"{req['shape'].upper()} shape")
                    if 'barcode' in req:
                        needs.append("barcode")
                    if needs:
                        feedback += f" Lock engaged. Need: {', '.join(needs)}"
            
            return jsonify({
                'success': False,
                'result': result_text,
                'hint': feedback
            })
            
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/save', methods=['POST'])
def save():
    session_id = request.cookies.get('session_id', 'default')
    if session_id in games:
        success = games[session_id].save_manager.save(games[session_id].state)
        return jsonify({'saved': success})
    return jsonify({'saved': False})

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(games),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
