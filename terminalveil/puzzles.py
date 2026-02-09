"""
Terminal Veil - Level Definitions
13 Sectors - Progressive difficulty with immersive storytelling
"""
import random

LEVELS = [
    {
        'id': 0,
        'name': 'Calibration',
        'intro': 'Welcome to Terminal Veil.\nYour neural interface requires calibration.\nScan any object to synchronize.',
        'requirement': {'any': True},
        'hint': 'Use SCAN button. Show camera any object.',
        'reward': 'Calibration Chip',
        'lore': 'The system awakens. You are the first to breach the outer layers.'
    },
    {
        'id': 1,
        'name': 'The Crimson Gate',
        'intro': 'The firewall demands warmth.\nA RED chromatic signature is required.',
        'requirement': {'color': 'red'},
        'hint': 'Find something red: apple, book, or draw red on paper.',
        'reward': 'Crimson Key',
        'lore': 'Blood-colored data streams flow through this sector. The machine recognizes sacrifice.'
    },
    {
        'id': 2,
        'name': 'Encoded Transmission',
        'intro': 'Static fills the screen.\nLocate QR code containing "VEIL-42".',
        'requirement': {'qr_contains': 'VEIL-42'},
        'hint': 'Generate QR with text "VEIL-42"',
        'reward': 'Decryption Module',
        'lore': 'Ancient transmissions pulse through the void. Someone left messages for those who would follow.'
    },
    {
        'id': 3,
        'name': 'Geometric Lock',
        'intro': 'Ancient machine responds to perfect geometry.\nPresent CIRCULAR form.',
        'requirement': {'shape': 'circle'},
        'hint': 'Show a coin, lid, or draw a circle.',
        'reward': 'Circular Token',
        'lore': 'The architects valued infinity. No beginning, no end - only the eternal cycle.'
    },
    {
        'id': 4,
        'name': 'Dual Authentication',
        'intro': 'Final security layer:\n1. BLUE chromatic data\n2. QR containing "END"',
        'requirement': {'color': 'blue', 'qr_contains': 'END'},
        'hint': 'Place blue object behind QR code with "END".',
        'reward': 'Master Key',
        'lore': 'Two truths must align. The sky meets the termination point.'
    },
    {
        'id': 5,
        'name': 'Commercial District',
        'intro': 'Corporate archives locked.\nScan BARCODE to access inventory.',
        'requirement': {'barcode': True},
        'hint': 'Scan any product barcode: cereal box, book, or can.',
        'reward': 'Corporate Pass',
        'lore': 'The old world left its marks on everything. Even commerce became control.'
    },
    {
        'id': 6,
        'name': 'Triangular Paradox',
        'intro': 'Three sides, three corners.\nTRIANGULAR form required.',
        'requirement': {'shape': 'triangle'},
        'hint': 'Hold up pizza slice, pyramid, or draw triangle.',
        'reward': 'Delta Code',
        'lore': 'Three points create stability, yet this structure defies logic. The paradox deepens.'
    },
    {
        'id': 7,
        'name': 'The Final Veil',
        'intro': 'Ultimate challenge: Match the random signature.',
        'requirement': {'randomized': True},
        'hint': 'Scan anything. System will tell you what it wants.',
        'reward': 'Reality Key',
        'lore': 'Chaos and order dance. The system chooses its champion.'
    },
    # NEW SECTORS 8-12 (Expanding to 13 total)
    {
        'id': 8,
        'name': 'The Chromatic Cascade',
        'intro': 'Security escalates.\nScan GREEN object to continue.',
        'requirement': {'color': 'green'},
        'hint': 'Find something green: plant, marker, or clothing.',
        'reward': 'Emerald Pass',
        'lore': 'Life persists even in the machine. Green data pulses with organic rhythm.'
    },
    {
        'id': 9,
        'name': 'The Data Convergence',
        'intro': 'Multiple data streams detected.\nQR code "SYNC-9" AND yellow chromatic signature required.',
        'requirement': {'qr_contains': 'SYNC-9', 'color': 'yellow'},
        'hint': 'Place yellow object near QR with "SYNC-9". Two signals must converge.',
        'reward': 'Convergence Chip',
        'lore': 'Streams merge. The yellow sun illuminates the synchronization point.'
    },
    {
        'id': 10,
        'name': 'The Geometric Trial',
        'intro': 'Perfect symmetry demands SQUARE form.\nThe machine recognizes balance.',
        'requirement': {'shape': 'square'},
        'hint': 'Show a square object: sticky note, tile, coaster, or draw a square.',
        'reward': 'Quadratic Seal',
        'lore': 'Four equal sides, four right angles. Perfection is rare but required.'
    },
    {
        'id': 11,
        'name': 'The Synaptic Firewall',
        'intro': '[CRITICAL SECURITY LAYER]\nBarcode signature AND triangular form required.\nThe system fights back.',
        'requirement': {'barcode': True, 'shape': 'triangle'},
        'hint': 'Hold triangle-shaped object near any barcode. Both must be visible.',
        'reward': 'Synaptic Key',
        'lore': 'The firewall has teeth. Only those who understand both commerce and geometry may pass.'
    },
    {
        'id': 12,
        'name': 'The Omega Protocol',
        'intro': '[OMEGA LEVEL CLEARANCE REQUIRED]\nThe final barrier adapts to your patterns.\nMatch the random signature to breach the core.',
        'requirement': {'randomized': True},
        'hint': 'The system analyzes YOU now. Scan and observe what it seeks.',
        'reward': 'Omega Core Access',
        'lore': 'You stand at the threshold of truth. The Veil itself recognizes your persistence. One final test remains.'
    }
]

def randomize_levels():
    """Randomize certain levels for replayability"""
    colors = ['red', 'blue', 'green', 'yellow']
    shapes = ['circle', 'triangle', 'square']
    codes = ['VEIL-42', 'SYNC-9', 'END', 'OMEGA-13']
    
    # Randomize sector 1 (The Crimson Gate) - can be any color
    c1 = random.choice(colors)
    LEVELS[1]['requirement'] = {'color': c1}
    LEVELS[1]['name'] = f"The {c1.title()} Gate"
    LEVELS[1]['intro'] = f"The firewall demands sacrifice.\nA {c1.upper()} chromatic signature is required."
    
    # Randomize sector 7 (The Final Veil)
    LEVELS[7]['actual_requirement'] = {
        'type': random.choice(['color', 'shape', 'qr']),
        'value': random.choice(['green', 'square', 'FINAL-99'])
    }
    
    # Randomize sector 12 (The Omega Protocol) - harder combinations
    omega_types = [
        {'type': 'color', 'value': random.choice(colors)},
        {'type': 'shape', 'value': random.choice(shapes)},
        {'type': 'qr', 'value': f"OMEGA-{random.randint(1, 99)}"}
    ]
    LEVELS[12]['actual_requirement'] = random.choice(omega_types)

def get_level_difficulty(level_id):
    """Return difficulty rating for accessibility options"""
    difficulty_map = {
        0: 'tutorial',      # Calibration
        1: 'easy',          # Crimson Gate
        2: 'easy',          # Encoded Transmission
        3: 'easy',          # Geometric Lock
        4: 'medium',        # Dual Authentication
        5: 'medium',        # Commercial District
        6: 'medium',        # Triangular Paradox
        7: 'hard',          # Final Veil
        8: 'hard',          # Chromatic Cascade
        9: 'hard',          # Data Convergence
        10: 'very_hard',    # Geometric Trial
        11: 'very_hard',    # Synaptic Firewall
        12: 'extreme'       # Omega Protocol
    }
    return difficulty_map.get(level_id, 'medium')

def get_accessibility_hint(level_id):
    """Get detailed accessibility hint for screen readers"""
    level = LEVELS[level_id]
    req = level['requirement']
    
    hints = [level['hint']]
    
    if 'color' in req:
        hints.append(f"You need to find something {req['color']} colored.")
    if 'qr_contains' in req:
        hints.append(f"Create or find a QR code containing the text: {req['qr_contains']}")
    if 'shape' in req:
        hints.append(f"Look for a {req['shape']} shaped object.")
    if 'barcode' in req:
        hints.append("Find any product with a barcode.")
    if req.get('randomized'):
        hints.append("Scan anything first to see what the system wants.")
    
    return " ".join(hints)
