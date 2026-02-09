"""
Terminal Veil - Level Definitions
"""
import random

LEVELS = [
    {
        'id': 0,
        'name': 'Calibration',
        'intro': 'Welcome to Terminal Veil.\nYour neural interface requires calibration.\nScan any object to synchronize.',
        'requirement': {'any': True},
        'hint': 'Use SCAN button. Show camera any object.',
        'reward': 'Calibration Chip'
    },
    {
        'id': 1,
        'name': 'The Crimson Gate',
        'intro': 'The firewall demands warmth.\nA RED chromatic signature is required.',
        'requirement': {'color': 'red'},
        'hint': 'Find something red: apple, book, or draw red on paper.',
        'reward': 'Crimson Key'
    },
    {
        'id': 2,
        'name': 'Encoded Transmission',
        'intro': 'Static fills the screen.\nLocate QR code containing "VEIL-42".',
        'requirement': {'qr_contains': 'VEIL-42'},
        'hint': 'Generate QR with text "VEIL-42"',
        'reward': 'Decryption Module'
    },
    {
        'id': 3,
        'name': 'Geometric Lock',
        'intro': 'Ancient machine responds to perfect geometry.\nPresent CIRCULAR form.',
        'requirement': {'shape': 'circle'},
        'hint': 'Show a coin, lid, or draw a circle.',
        'reward': 'Circular Token'
    },
    {
        'id': 4,
        'name': 'Dual Authentication',
        'intro': 'Final security layer:\n1. BLUE chromatic data\n2. QR containing "END"',
        'requirement': {'color': 'blue', 'qr_contains': 'END'},
        'hint': 'Place blue object behind QR code with "END".',
        'reward': 'Master Key'
    },
    {
        'id': 5,
        'name': 'Commercial District',
        'intro': 'Corporate archives locked.\nScan BARCODE to access inventory.',
        'requirement': {'barcode': True},
        'hint': 'Scan any product barcode: cereal box, book, or can.',
        'reward': 'Corporate Pass'
    },
    {
        'id': 6,
        'name': 'Triangular Paradox',
        'intro': 'Three sides, three corners.\nTRIANGULAR form required.',
        'requirement': {'shape': 'triangle'},
        'hint': 'Hold up pizza slice, pyramid, or draw triangle.',
        'reward': 'Delta Code'
    },
    {
        'id': 7,
        'name': 'The Final Veil',
        'intro': 'Ultimate challenge: Match the random signature.',
        'requirement': {'randomized': True},
        'hint': 'Scan anything. System will tell you what it wants.',
        'reward': 'Reality Key'
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
