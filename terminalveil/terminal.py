"""
Terminal Veil - Game Engine
Handles state, progression, inventory, and command parsing.
"""
import random
from terminalveil.puzzles import LEVELS, get_level_difficulty, get_accessibility_hint
from terminalveil.save_manager import SaveManager

class GameEngine:
    def __init__(self, ui=None):
        self.ui = ui
        self.state = {
            'current_level': 0,
            'inventory': [],
            'flags': {},
            'scans_this_level': [],
            'game_complete': False
        }
        self.save_manager = SaveManager()
        self.load_game()
    
    def get_current_level(self):
        if self.state['current_level'] < len(LEVELS):
            return LEVELS[self.state['current_level']]
        return None
    
    def get_current_description(self):
        level = self.get_current_level()
        if not level:
            return "System Error: No level data found."
        
        intro = level.get('intro', 'Unknown sector.')
        req = level.get('requirement', {})
        
        # Build sector header with difficulty
        diff = get_level_difficulty(self.state['current_level'])
        diff_display = {
            'tutorial': '[TRAINING]',
            'easy': '',
            'medium': '[MEDIUM]',
            'hard': '[HARD]',
            'very_hard': '[VERY HARD]',
            'extreme': '[EXTREME]'
        }.get(diff, '')
        
        desc = f"[SECTOR {self.state['current_level'] + 1}] {diff_display}\n{intro}\n\n"
        
        # Show objectives clearly
        objectives = []
        if 'color' in req:
            objectives.append(f"[OBJECTIVE] Locate and scan: {req['color'].upper()} colored object")
        if 'qr_contains' in req:
            objectives.append(f"[OBJECTIVE] Decode QR containing: '{req['qr_contains']}'")
        if 'shape' in req:
            objectives.append(f"[OBJECTIVE] Present geometric form: {req['shape'].upper()}")
        if 'barcode' in req:
            objectives.append(f"[OBJECTIVE] Scan any barcode")
        if req.get('any'):
            objectives.append("[OBJECTIVE] Scan any object to calibrate")
        if req.get('randomized'):
            objectives.append("[OBJECTIVE] Scan to discover what the system seeks")
        
        if objectives:
            desc += '\n'.join(objectives) + '\n'
        
        desc += f"\nInventory: {', '.join(self.state['inventory']) if self.state['inventory'] else '[empty]'}"
        return desc
    
    def process_command(self, cmd):
        parts = cmd.lower().strip().split()
        if not parts:
            return None
        
        action = parts[0]
        args = parts[1:]
        
        commands = {
            'help': self.cmd_help,
            'look': self.cmd_look,
            'inventory': self.cmd_inventory,
            'inv': self.cmd_inventory,
            'scan': self.cmd_scan_hint,
            'use': lambda a: self.cmd_use(a),
            'go': lambda a: self.cmd_go(a),
            'save': self.cmd_save,
            'load': self.cmd_load,
            'quit': self.cmd_quit,
            'hint': self.cmd_hint,
            'status': self.cmd_status,
            'lore': self.cmd_lore,
            'clear': self.cmd_clear
        }
        
        if action in commands:
            if action in ['use', 'go']:
                return commands[action](args)
            return commands[action]()
        
        return f"Unknown command: '{action}'. Type 'help' for available commands."
    
    def cmd_help(self):
        return "[b]SYSTEM COMMANDS[/b]\n[color=00FFFF]help[/color]       - Show this list\n[color=00FFFF]look[/color]       - Examine current sector\n[color=00FFFF]inventory[/color]  - List collected items\n[color=00FFFF]scan[/color]       - Activate camera\n[color=00FFFF]save[/color]       - Save progress\n[color=00FFFF]load[/color]       - Load progress\n[color=00FFFF]hint[/color]       - Get puzzle clue\n[color=00FFFF]lore[/color]       - Read sector backstory\n[color=00FFFF]status[/color]     - Show progress\n[color=00FFFF]quit[/color]       - Exit system"
    
    def cmd_look(self):
        return self.get_current_description()
    
    def cmd_inventory(self):
        if not self.state['inventory']:
            return "Inventory: [empty]"
        return f"Inventory: {', '.join(self.state['inventory'])}"
    
    def cmd_scan_hint(self):
        level = self.get_current_level()
        if not level:
            return "No active sector."
        
        req = level.get('requirement', {})
        hints = []
        
        if req.get('any'):
            hints.append("Scan any object to proceed.")
        else:
            if 'color' in req:
                hints.append(f"Need: {req['color'].upper()} color")
            if 'qr_contains' in req:
                hints.append(f"Need: QR code with '{req['qr_contains']}'")
            if 'shape' in req:
                hints.append(f"Need: {req['shape'].upper()} shape")
            if 'barcode' in req:
                hints.append("Need: Any barcode")
        
        return "SCAN ready. " + " ".join(hints) if hints else "Use SCAN button or type scan with parameters."
    
    def cmd_use(self, args):
        if not args:
            return "Use what? Specify item name."
        item = ' '.join(args)
        if item in self.state['inventory']:
            return f"You can't use {item} here."
        return f"You don't have {item}."
    
    def cmd_go(self, args):
        return "Movement blocked. Use SCAN to solve the current sector."
    
    def cmd_save(self):
        if self.save_manager.save(self.state):
            return "Progress saved."
        return "Save failed."
    
    def cmd_load(self):
        loaded = self.save_manager.load()
        if loaded:
            self.state = loaded
            return "Previous session restored."
        return "No save data found."
    
    def cmd_quit(self):
        return "Goodbye."
    
    def cmd_hint(self):
        level = self.get_current_level()
        if level and 'hint' in level:
            return f"[HINT] {level['hint']}"
        return "No hints available."
    
    def cmd_lore(self):
        level = self.get_current_level()
        if level and 'lore' in level:
            return f"[ARCHIVE ENTRY]\n{level['lore']}"
        return "No archive data available for this sector."
    
    def cmd_status(self):
        lvl = self.state['current_level'] + 1
        total = len(LEVELS)
        difficulty = get_level_difficulty(self.state['current_level'])
        diff_display = {
            'tutorial': '[TRAINING]',
            'easy': '',
            'medium': '[MEDIUM]',
            'hard': '[HARD]',
            'very_hard': '[VERY HARD]',
            'extreme': '[EXTREME]'
        }.get(difficulty, '')
        return f"Sector {lvl}/{total} {diff_display} | Inventory: {len(self.state['inventory'])} items"
    
    def cmd_clear(self):
        return "__CLEAR__"
    
    def process_scan_result(self, result):
        """Process what was detected and add to inventory"""
        text_parts = []
        
        if result.get('type') == 'qr':
            text_parts.append(f"QR Data: {result['data']}")
            self.state['inventory'].append(f"QR:{result['data']}")
        elif result.get('type') == 'color':
            color = result.get('color', 'unknown')
            text_parts.append(f"Color signature: {color.upper()}")
            self.state['inventory'].append(f"Color:{color}")
        elif result.get('type') == 'shape':
            shape = result.get('shape', 'unknown')
            text_parts.append(f"Object analyzed: {shape.upper()} form detected")
            self.state['inventory'].append(f"Shape:{shape}")
        elif result.get('type') == 'barcode':
            text_parts.append(f"Barcode Data: {result['data']}")
            self.state['inventory'].append(f"Barcode:{result['data']}")
        else:
            text_parts.append("Unknown or unclear signature")
        
        # Remove duplicates from inventory
        self.state['inventory'] = list(set(self.state['inventory']))
        return " | ".join(text_parts)
    
    def check_puzzle_solution(self, result):
        """
        STRICT puzzle checking - must match EXACT requirements
        Returns True only if scan result satisfies ALL requirements
        """
        level = self.get_current_level()
        if not level:
            return False
        
        req = level.get('requirement', {})
        result_type = result.get('type', 'unknown')
        
        # Level 0: Calibration - any scan works
        if req.get('any'):
            return result_type in ['color', 'shape', 'qr', 'barcode']
        
        # Randomized levels (7 and 12)
        if req.get('randomized'):
            actual = level.get('actual_requirement', {})
            if actual.get('type') != result_type:
                return False
            
            if result_type == 'color':
                return result.get('color') == actual.get('value')
            elif result_type == 'shape':
                return result.get('shape') == actual.get('value')
            elif result_type == 'qr':
                return actual.get('value') in result.get('data', '')
            return False
        
        # For dual requirements (e.g., color + QR), we check if this scan
        # contributes to completing the puzzle. Since we can only scan one thing
        # at a time, we check if THIS scan matches ANY of the requirements.
        # The player may need to scan multiple things across attempts.
        
        matched = False
        
        # Check color requirement
        if 'color' in req:
            if result_type != 'color':
                return False  # Wrong type entirely
            detected = result.get('color', '').lower()
            required = req['color'].lower()
            # Must be exact color match
            if detected == required:
                matched = True
            else:
                return False  # Found color but wrong one
        
        # Check QR requirement
        if 'qr_contains' in req:
            if result_type != 'qr':
                return False  # Wrong type
            if req['qr_contains'] not in result.get('data', ''):
                return False  # QR found but wrong content
            matched = True
        
        # Check shape requirement
        if 'shape' in req:
            if result_type != 'shape':
                return False  # Wrong type
            detected = result.get('shape', '').lower()
            required = req['shape'].lower()
            if detected != required:
                return False  # Wrong shape
            matched = True
        
        # Check barcode requirement
        if 'barcode' in req:
            if result_type != 'barcode':
                return False  # Wrong type
            matched = True
        
        return matched
    
    def advance_level(self):
        self.state['current_level'] += 1
        self.state['scans_this_level'] = []
        
        if self.state['current_level'] >= len(LEVELS):
            self.state['game_complete'] = True
            return "[CRITICAL] Final sector breached.\nThe Veil has been lifted.\nReality is code."
        
        level = self.get_current_level()
        level_num = self.state['current_level'] + 1
        return f"[SECTOR {level_num}] Access granted.\n{level.get('intro', '')}"
    
    def check_victory(self):
        return self.state['game_complete']
    
    def load_game(self):
        loaded = self.save_manager.load()
        if loaded:
            self.state = loaded
