"""
Terminal Veil - Level Definitions with Easter Eggs and Extreme Difficulty
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
        'lore': 'The system awakens. You are the first to breach the outer layers.',
        'secret': 'The first step is always the easiest.'
    },
    {
        'id': 1,
        'name': 'The Crimson Gate',
        'intro': 'The firewall demands warmth.\nA RED chromatic signature is required.',
        'requirement': {'color': 'red'},
        'hint': 'Find something red: apple, book, or draw red on paper.',
        'reward': 'Crimson Key',
        'lore': 'Blood-colored data streams flow through this sector.',
        'secret': 'Red is the color of beginnings.'
    },
    {
        'id': 2,
        'name': 'Encoded Transmission',
        'intro': 'Static fills the screen.\nLocate QR code containing "VEIL-42".',
        'requirement': {'qr_contains': 'VEIL-42'},
        'hint': 'Generate QR with text "VEIL-42"',
        'reward': 'Decryption Module',
        'lore': 'Ancient transmissions pulse through the void.',
        'secret': '42 is not the answer. It is the question.'
    },
    {
        'id': 3,
        'name': 'Geometric Lock',
        'intro': 'Ancient machine responds to perfect geometry.\nPresent CIRCULAR form.',
        'requirement': {'shape': 'circle'},
        'hint': 'Show a coin, lid, or draw a circle.',
        'reward': 'Circular Token',
        'lore': 'The architects valued infinity.',
        'secret': 'Round and round we go.'
    },
    {
        'id': 4,
        'name': 'Dual Authentication',
        'intro': 'Final security layer:\n1. BLUE chromatic data\n2. QR containing "END"',
        'requirement': {'color': 'blue', 'qr_contains': 'END'},
        'hint': 'Place blue object behind QR code with "END".',
        'reward': 'Master Key',
        'lore': 'Two truths must align.',
        'secret': 'Every ending is a beginning.'
    },
    {
        'id': 5,
        'name': 'Commercial District',
        'intro': 'Corporate archives locked.\nScan BARCODE to access inventory.',
        'requirement': {'barcode': True},
        'hint': 'Scan any product barcode.',
        'reward': 'Corporate Pass',
        'lore': 'The old world left its marks on everything.',
        'secret': 'Consumerism was always a prison.'
    },
    {
        'id': 6,
        'name': 'Triangular Paradox',
        'intro': 'Three sides, three corners.\nTRIANGULAR form required.',
        'requirement': {'shape': 'triangle'},
        'hint': 'Hold up pizza slice, pyramid, or draw triangle.',
        'reward': 'Delta Code',
        'lore': 'Three points create stability.',
        'secret': '3 is the magic number.'
    },
    {
        'id': 7,
        'name': 'The Final Veil',
        'intro': 'Ultimate challenge: Match the random signature.',
        'requirement': {'randomized': True},
        'hint': 'Scan anything. System will tell you what it wants.',
        'reward': 'Reality Key',
        'lore': 'Chaos and order dance.',
        'secret': 'You thought THAT was the final veil?'
    },
    {
        'id': 8,
        'name': 'The Chromatic Cascade',
        'intro': 'Security escalates.\nScan GREEN object to continue.',
        'requirement': {'color': 'green'},
        'hint': 'Find something green.',
        'reward': 'Emerald Pass',
        'lore': 'Life persists even in the machine.',
        'secret': 'Nature finds a way.'
    },
    {
        'id': 9,
        'name': 'The Data Convergence',
        'intro': 'Multiple data streams detected.\nQR code "SYNC-9" AND yellow chromatic signature required.',
        'requirement': {'qr_contains': 'SYNC-9', 'color': 'yellow'},
        'hint': 'Place yellow object near QR with "SYNC-9".',
        'reward': 'Convergence Chip',
        'lore': 'Streams merge.',
        'secret': '9 is 3 squared.'
    },
    # EXTREME DIFFICULTY LEVELS
    {
        'id': 10,
        'name': 'The Geometric Ascension',
        'intro': '[CRITICAL] Scan shapes in SEQUENCE:\n1. TRIANGLE → 2. SQUARE → 3. CIRCLE\nOne wrong scan RESETS everything!',
        'requirement': {'sequence': ['triangle', 'square', 'circle']},
        'hint': 'THREE shapes in ORDER. Triangle first, Square second, Circle third. ONE mistake = RESET!',
        'reward': 'Ascension Seal',
        'lore': 'The ancient ones understood geometry as language.',
        'secret': 'Order matters. Always.',
        'difficulty': 'extreme'
    },
    {
        'id': 11,
        'name': 'The Synaptic Firewall',
        'intro': '[OMEGA SECURITY] SIMULTANEOUS scan required:\nBARCODE + RED color in SINGLE frame!',
        'requirement': {'simultaneous': ['barcode', 'red']},
        'hint': 'EXTREME: Hold RED object IN FRONT of barcode. Both in ONE photo!',
        'reward': 'Synaptic Key',
        'lore': 'The firewall demands proof of mastery.',
        'secret': 'Timing and positioning.',
        'difficulty': 'extreme'
    },
    {
        'id': 12,
        'name': 'The Alpha-Omega Protocol',
        'intro': '[REALITY BREACH] COMPLETE the ritual:\n1. QR "ALPHA" → 2. YELLOW → 3. TRIANGLE → 4. QR "OMEGA"\nALL FOUR in ORDER. One mistake = TOTAL RESET!',
        'requirement': {'complex_sequence': [
            {'type': 'qr', 'contains': 'ALPHA'},
            {'type': 'color', 'value': 'yellow'},
            {'type': 'shape', 'value': 'triangle'},
            {'type': 'qr', 'contains': 'OMEGA'}
        ]},
        'hint': 'THE ULTIMATE TEST: 4 scans in order. Write it down! ALPHA→YELLOW→TRIANGLE→OMEGA',
        'reward': 'Alpha-Omega Core',
        'lore': 'Four keys to unlock reality itself. Few have succeeded.',
        'secret': 'You are worthy. Or you will be.',
        'difficulty': 'impossible'
    }
]

def randomize_levels():
    colors = ['red', 'blue', 'green', 'yellow']
    c1 = random.choice(colors)
    LEVELS[1]['requirement'] = {'color': c1}
    LEVELS[1]['name'] = f"The {c1.title()} Gate"
    LEVELS[1]['intro'] = f"The firewall demands sacrifice.\nA {c1.upper()} chromatic signature is required."
    
    LEVELS[7]['actual_requirement'] = {
        'type': random.choice(['color', 'shape', 'qr']),
        'value': random.choice(['green', 'square', 'FINAL-99'])
    }

def get_level_difficulty(level_id):
    mapping = {
        0: 'tutorial', 1: 'easy', 2: 'easy', 3: 'easy',
        4: 'medium', 5: 'medium', 6: 'medium', 7: 'hard',
        8: 'hard', 9: 'hard', 10: 'extreme', 11: 'extreme', 12: 'impossible'
    }
    return mapping.get(level_id, 'medium')

def get_difficulty_display(level_id):
    diff = get_level_difficulty(level_id)
    displays = {
        'tutorial': '[TRAINING]',
        'easy': '[EASY]',
        'medium': '[MEDIUM]',
        'hard': '[HARD]',
        'extreme': '[EXTREME]',
        'impossible': '[LEGENDARY]'
    }
    return displays.get(diff, '[NORMAL]')
