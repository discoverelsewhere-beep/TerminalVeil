"""
Terminal Veil - Game Engine with Easter Eggs and Extreme Difficulty
Handles state, progression, inventory, and command parsing.
"""
import random
from terminalveil.puzzles import LEVELS, get_level_difficulty, get_difficulty_display
from terminalveil.save_manager import SaveManager

class GameEngine:
    def __init__(self, ui=None):
        self.ui = ui
        self.state = {
            'current_level': 0,
            'inventory': [],
            'flags': {},
            'scans_this_level': [],  # Track scans for sequence puzzles
            'game_complete': False,
            'easter_eggs_found': [],
            'attempts_count': {},  # Track attempts per level
            'first_success': None  # Track first completion
        }
        self.save_manager = SaveManager()
        self.load_game()
        
        # Initialize attempt counter for current level
        if self.state['current_level'] not in self.state['attempts_count']:
            self.state['attempts_count'][self.state['current_level']] = 0
    
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
        diff_display = get_difficulty_display(self.state['current_level'])
        
        desc = f"[SECTOR {self.state['current_level'] + 1}] {diff_display}\n{intro}\n\n"
        
        # Show progress for sequence puzzles
        if 'sequence' in req:
            seq = req['sequence']
            progress = self.state['scans_this_level']
            desc += f"[PROGRESS] {len(progress)}/{len(seq)} steps completed\n"
            if progress:
                desc += f"[COMPLETED] {' → '.join(progress)}\n"
            desc += f"[NEXT] {seq[len(progress)] if len(progress) < len(seq) else 'COMPLETE'}\n\n"
        
        if 'complex_sequence' in req:
            seq = req['complex_sequence']
            progress = self.state['scans_this_level']
            desc += f"[PROGRESS] {len(progress)}/{len(seq)} ritual steps\n"
            if progress:
                completed = []
                for i, p in enumerate(progress):
                    if isinstance(p, dict):
                        completed.append(p.get('type', '?'))
                    else:
                        completed.append(str(p))
                desc += f"[PERFORMED] {' → '.join(completed)}\n"
            desc += "\n"
        
        # Show objectives
        objectives = []
        if 'color' in req and 'shape' not in str(req) and 'barcode' not in str(req):
            objectives.append(f"[OBJECTIVE] {req['color'].upper()} color")
        if 'qr_contains' in req:
            objectives.append(f"[OBJECTIVE] QR: '{req['qr_contains']}'")
        if 'shape' in req and not req.get('sequence') and not req.get('complex_sequence'):
            objectives.append(f"[OBJECTIVE] {req['shape'].upper()} shape")
        if 'barcode' in req and not req.get('simultaneous'):
            objectives.append(f"[OBJECTIVE] Any barcode")
        if req.get('any'):
            objectives.append(f"[OBJECTIVE] Scan anything")
        if req.get('randomized'):
            objectives.append(f"[OBJECTIVE] Scan to discover requirement")
        if req.get('sequence'):
            objectives.append(f"[OBJECTIVE] Sequence: {' → '.join(req['sequence'])}")
        if req.get('simultaneous'):
            items = req['simultaneous']
            objectives.append(f"[OBJECTIVE] SIMULTANEOUS: {items[0].upper()} + {items[1].upper()}")
        if req.get('complex_sequence'):
            objectives.append(f"[OBJECTIVE] 4-part ritual (check progress above)")
        
        if objectives:
            desc += '\n'.join(objectives) + '\n'
        
        # Show attempt counter for extreme levels
        if self.state['current_level'] >= 10:
            attempts = self.state['attempts_count'].get(self.state['current_level'], 0)
            desc += f"\n[ATTEMPTS] {attempts}"
        
        desc += f"\nInventory: {', '.join(self.state['inventory']) if self.state['inventory'] else '[empty]'}"
        return desc
    
    def process_command(self, cmd):
        parts = cmd.lower().strip().split()
        if not parts:
            return None
        
        action = parts[0]
        args = parts[1:]
        
        # Easter egg: KONAMI code detection
        if action == 'up':
            return "The system recognizes the attempt. But codes require sequences."
        if action == 'iddqd':
            return "[GOD MODE] Nice try, Doomguy. This is not that kind of game."
        if action == 'xyzzy':
            return "A hollow voice says 'Wrong game, adventurer.'"
        
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
            'secret': self.cmd_secret,
            'clear': self.cmd_clear
        }
        
        if action in commands:
            if action in ['use', 'go']:
                return commands[action](args)
            return commands[action]()
        
        return f"Unknown command: '{action}'. Type 'help' for available commands."
    
    def cmd_help(self):
        return """[b]SYSTEM COMMANDS[/b]
[color=00FFFF]help[/color]       - Show this list
[color=00FFFF]look[/color]       - Examine current sector
[color=00FFFF]inventory[/color]  - List collected items
[color=00FFFF]scan[/color]       - Activate camera
[color=00FFFF]save[/color]       - Save progress
[color=00FFFF]load[/color]       - Load progress
[color=00FFFF]hint[/color]       - Get puzzle clue
[color=00FFFF]lore[/color]       - Read sector backstory
[color=00FFFF]secret[/color]     - Hidden knowledge
[color=00FFFF]status[/color]     - Show progress
[color=00FFFF]quit[/color]       - Exit system

[b]HINT:[/b] Some commands are not what they seem."""
    
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
        
        if req.get('sequence'):
            seq = req['sequence']
            progress = self.state['scans_this_level']
            hints.append(f"SEQUENCE: Scan in exact order!")
            hints.append(f"Progress: {len(progress)}/{len(seq)}")
            if len(progress) < len(seq):
                hints.append(f"Next: {seq[len(progress)]}")
        elif req.get('simultaneous'):
            items = req['simultaneous']
            hints.append(f"SIMULTANEOUS: {items[0].upper()} + {items[1].upper()} in ONE frame!")
        elif req.get('complex_sequence'):
            hints.append("4-PART RITUAL. Write it down:")
            hints.append("1. QR 'ALPHA' → 2. YELLOW → 3. TRIANGLE → 4. QR 'OMEGA'")
        elif req.get('any'):
            hints.append("Scan any object.")
        else:
            if 'color' in req:
                hints.append(f"Need: {req['color'].upper()} color")
            if 'qr_contains' in req:
                hints.append(f"Need: QR with '{req['qr_contains']}'")
            if 'shape' in req:
                hints.append(f"Need: {req['shape'].upper()} shape")
            if 'barcode' in req:
                hints.append("Need: Barcode")
        
        return "SCAN ready. " + " ".join(hints)
    
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
        return "No archive data available."
    
    def cmd_secret(self):
        level = self.get_current_level()
        if level and 'secret' in level:
            return f"[WHISPER] {level['secret']}"
        return "The Veil keeps its secrets."
    
    def cmd_status(self):
        lvl = self.state['current_level'] + 1
        total = len(LEVELS)
        diff = get_difficulty_display(self.state['current_level'])
        inv_count = len(self.state['inventory'])
        return f"Sector {lvl}/{total} {diff} | Inventory: {inv_count}"
    
    def cmd_clear(self):
        return "__CLEAR__"
    
    def process_scan_result(self, result, add_to_inventory=False):
        """Process scan. Only add to inventory on success."""
        text_parts = []
        
        if result.get('type') == 'qr':
            text_parts.append(f"QR: {result['data']}")
        elif result.get('type') == 'color':
            text_parts.append(f"Color: {result['color'].upper()}")
        elif result.get('type') == 'shape':
            text_parts.append(f"Form: {result['shape'].upper()}")
        elif result.get('type') == 'barcode':
            text_parts.append(f"Barcode: {result['data']}")
        else:
            text_parts.append("Unknown signature")
        
        return " | ".join(text_parts)
    
    def check_puzzle_solution(self, result):
        """Check if scan solves puzzle - handles all difficulty types."""
        level = self.get_current_level()
        if not level:
            return False
        
        req = level.get('requirement', {})
        result_type = result.get('type', 'unknown')
        
        # Track attempt
        self.state['attempts_count'][self.state['current_level']] = \
            self.state['attempts_count'].get(self.state['current_level'], 0) + 1
        
        # Level 0: Calibration - anything works
        if req.get('any'):
            return result_type in ['color', 'shape', 'qr', 'barcode']
        
        # SEQUENCE PUZZLE (Level 10)
        if 'sequence' in req:
            target_seq = req['sequence']
            progress = self.state['scans_this_level']
            
            if result_type != 'shape':
                self.state['scans_this_level'] = []  # Reset on wrong type
                return False
            
            detected = result.get('shape', '').lower()
            expected = target_seq[len(progress)] if len(progress) < len(target_seq) else None
            
            if detected == expected:
                progress.append(detected)
                self.state['scans_this_level'] = progress
                # Success only when sequence complete
                return len(progress) == len(target_seq)
            else:
                # Wrong shape - RESET
                self.state['scans_this_level'] = []
                return False
        
        # SIMULTANEOUS SCAN (Level 11)
        if 'simultaneous' in req:
            targets = req['simultaneous']
            # Must detect BOTH in one scan
            # This requires special handling in camera or multiple detections
            # For now, strict requirement check
            detected_types = []
            if result_type == 'barcode':
                detected_types.append('barcode')
            elif result_type == 'color' and result.get('color') == 'red':
                detected_types.append('red')
            
            # Actually this needs camera to return multiple detections
            # For now, check if result matches one and track partial
            if result_type == 'barcode' or (result_type == 'color' and result.get('color') == 'red'):
                return True  # Simplified - camera should detect both
            return False
        
        # COMPLEX SEQUENCE (Level 12)
        if 'complex_sequence' in req:
            target_seq = req['complex_sequence']
            progress = self.state['scans_this_level']
            
            if len(progress) >= len(target_seq):
                return False
            
            expected = target_seq[len(progress)]
            
            # Check if result matches expected
            if expected['type'] != result_type:
                self.state['scans_this_level'] = []  # Reset
                return False
            
            if result_type == 'qr':
                if expected['contains'] not in result.get('data', ''):
                    self.state['scans_this_level'] = []
                    return False
            elif result_type == 'color':
                if result.get('color') != expected['value']:
                    self.state['scans_this_level'] = []
                    return False
            elif result_type == 'shape':
                if result.get('shape') != expected['value']:
                    self.state['scans_this_level'] = []
                    return False
            
            # Correct step
            progress.append({'type': result_type, 'value': result.get('data') or result.get('color') or result.get('shape')})
            self.state['scans_this_level'] = progress
            return len(progress) == len(target_seq)
        
        # RANDOMIZED LEVELS
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
        
        # STANDARD REQUIREMENTS
        matched = False
        
        if 'color' in req:
            if result_type != 'color':
                return False
            if result.get('color') != req['color']:
                return False
            matched = True
        
        if 'qr_contains' in req:
            if result_type != 'qr':
                return False
            if req['qr_contains'] not in result.get('data', ''):
                return False
            matched = True
        
        if 'shape' in req:
            if result_type != 'shape':
                return False
            if result.get('shape') != req['shape']:
                return False
            matched = True
        
        if 'barcode' in req:
            if result_type != 'barcode':
                return False
            matched = True
        
        return matched
    
    def advance_level(self):
        self.state['current_level'] += 1
        self.state['scans_this_level'] = []
        
        # Initialize attempt counter for new level
        if self.state['current_level'] not in self.state['attempts_count']:
            self.state['attempts_count'][self.state['current_level']] = 0
        
        if self.state['current_level'] >= len(LEVELS):
            self.state['game_complete'] = True
            if not self.state['first_success']:
                self.state['first_success'] = datetime.now().isoformat()
            return """[CRITICAL] ALL SECTORS BREACHED

The Veil has been lifted.
Reality is code.
You are among the elite few who have conquered The Alpha-Omega Protocol.

[ACHIEVEMENT UNLOCKED: VEIL_BREAKER]
[ATTEMPTS: {attempts}]

Type 'status' to see your glory.""".format(attempts=sum(self.state['attempts_count'].values()))
        
        level = self.get_current_level()
        level_num = self.state['current_level'] + 1
        diff = get_difficulty_display(self.state['current_level'])
        
        return f"[SECTOR {level_num}] {diff} Access granted.\n{level.get('intro', '')}"
    
    def check_victory(self):
        return self.state['game_complete']
    
    def load_game(self):
        loaded = self.save_manager.load()
        if loaded:
            self.state = loaded
