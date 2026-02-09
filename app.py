"""
Terminal Veil - Web Edition (Async)
Works on iPhone, Android, and Desktop browsers
"""
import asyncio
import base64
import io
from datetime import datetime

import cv2
import numpy as np
from PIL import Image
from flask import Flask, jsonify, render_template, request

# Import your existing game files
from terminalveil.terminal import GameEngine
from terminalveil.camera_handler import CameraAnalyzer

app = Flask(__name__)

# Store games for each player (simple version)
games = {}
analyzers = {}


async def get_or_create_game(session_id: str) -> GameEngine:
    """Async helper to get or create a game session."""
    if session_id not in games:
        # Simulate async initialization (e.g., database lookup)
        await asyncio.sleep(0)
        games[session_id] = GameEngine()
    return games[session_id]


async def get_or_create_analyzer(session_id: str) -> CameraAnalyzer:
    """Async helper to get or create a camera analyzer."""
    if session_id not in analyzers:
        await asyncio.sleep(0)
        analyzers[session_id] = CameraAnalyzer()
    return analyzers[session_id]


@app.route('/')
async def index():
    """Show the game page (async version)."""
    # Create new game instance for this browser
    session_id = str(datetime.now().timestamp())
    
    # Async initialization
    games[session_id] = GameEngine()
    analyzers[session_id] = CameraAnalyzer()
    
    resp = app.make_response(render_template('index.html'))
    resp.set_cookie('session_id', session_id)
    return resp


@app.route('/command', methods=['POST'])
async def command():
    """Handle typed commands (async version)."""
    session_id = request.cookies.get('session_id', 'default')
    
    # Get or create game asynchronously
    engine = await get_or_create_game(session_id)
    
    data = request.json
    cmd = data.get('command', '')
    
    # Handle scan command specially
    if cmd.lower().startswith('scan'):
        return jsonify({
            'type': 'scan_request',
            'mode': cmd.lower().replace('scan', '').strip() or 'any'
        })
    
    # Process normal command
    # Run CPU-bound work in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, engine.process_command, cmd)
    
    return jsonify({
        'type': 'text',
        'response': response,
        'level': engine.state['current_level'] + 1,
        'inventory': len(engine.state['inventory']),
        'victory': engine.check_victory()
    })


@app.route('/scan', methods=['POST'])
async def scan():
    """Process camera image (async version)."""
    session_id = request.cookies.get('session_id', 'default')
    
    engine = await get_or_create_game(session_id)
    analyzer = await get_or_create_analyzer(session_id)
    
    data = request.json
    image_data = data.get('image', '')
    mode = data.get('mode', 'any')
    
    try:
        # Remove the "data:image/png;base64," prefix
        image_data = image_data.split(',')[1]
        # Convert base64 to image
        image_bytes = base64.b64decode(image_data)
        
        # Run image processing in thread pool (CPU-bound)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            _process_image, 
            image_bytes, 
            analyzer, 
            mode
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']})
        
        # Process scan result
        result_text = await loop.run_in_executor(
            None,
            engine.process_scan_result,
            result
        )
        
        # Check if it solves the puzzle
        success = await loop.run_in_executor(
            None,
            engine.check_puzzle_solution,
            result
        )
        
        if success:
            advance_text = await loop.run_in_executor(
                None,
                engine.advance_level
            )
            return jsonify({
                'success': True,
                'result': result_text,
                'advance': advance_text,
                'level': engine.state['current_level'] + 1
            })
        else:
            return jsonify({
                'success': False,
                'result': result_text,
                'hint': 'Item saved to inventory. Puzzle not solved yet.'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)})


def _process_image(image_bytes: bytes, analyzer: CameraAnalyzer, mode: str) -> dict:
    """Synchronous helper for image processing (runs in thread pool)."""
    image = Image.open(io.BytesIO(image_bytes))
    # Convert to format OpenCV likes
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # Analyze the image
    return analyzer.analyze_frame(image, mode)


@app.route('/save', methods=['POST'])
async def save():
    """Save game (async version)."""
    session_id = request.cookies.get('session_id', 'default')
    if session_id in games:
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None,
            games[session_id].save_manager.save,
            games[session_id].state
        )
        return jsonify({'saved': success})
    return jsonify({'saved': False})


@app.route('/health')
async def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(games),
        'timestamp': datetime.now().isoformat()
    })


async def cleanup_inactive_sessions():
    """Background task to cleanup old sessions (runs periodically)."""
    while True:
        await asyncio.sleep(3600)  # Run every hour
        # In production, you'd check last activity timestamp
        # and remove sessions inactive for X minutes
        app.logger.info(f"Active sessions: {len(games)}")


if __name__ == '__main__':
    # Run on all network interfaces so iPhone can connect
    # Note: For production async server, use hypercorn or uvicorn with asgiref
    app.run(debug=True, host='0.0.0.0', port=5495, threaded=True)
