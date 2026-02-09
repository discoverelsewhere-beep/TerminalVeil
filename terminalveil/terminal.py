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
        
        desc = f"[SECTOR {self.state['current_level'] + 1}]\n{intro}\n\n"
        
        if 'color' in req:
            desc += f"[OBJECTIVE] Locate and scan: {req['color'].upper()} chromatic signature\n"
        if 'qr_contains' in req:
            desc += f"[OBJECTIVE] Decode QR containing: '{req['qr_contains']}'\n"
        if 'shape' in req:
            desc += f"[OBJECTIVE] Present geometric form: {req['shape'].upper()}\n"
        if 'barcode' in req:
            desc += f"[OBJECTIVE] Scan any barcode\n"
        
        desc += f"\nInventory: {', '.join(self.state['inventory']) if self.state['inventory'] else '[empty]'}"
        return desc
    
    def cmd_lore(self):
        level = self.get_current_level()
        if level and 'lore' in level:
            return f"[ARCHIVE ENTRY]\n{level['lore']}"
        return "No archive data available for this sector."
    
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
        return "Use SCAN button or type scan with parameters."
    
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
    
    def cmd_status(self):
        lvl = self.state['current_level'] + 1
        total = len(LEVELS)
        difficulty = get_level_difficulty(self.state['current_level'])
        diff_display = {
            'tutorial': '[TRAINING]',
            'easy': '[EASY]',
            'medium': '[MEDIUM]', 
            'hard': '[HARD]',
            'very_hard': '[VERY HARD]',
            'extreme': '[EXTREME]'
        }.get(difficulty, '[NORMAL]')
        return f"Sector {lvl}/{total} {diff_display} | Inventory: {len(self.state['inventory'])} items"
    
    def cmd_clear(self):
        return "__CLEAR__"
    
    def process_scan_result(self, result):
        text_parts = []
        
        if result.get('type') == 'qr':
            text_parts.append(f"QR Data: {result['data']}")
            self.state['inventory'].append(f"QR:{result['data']}")
        elif result.get('type') == 'color':
            text_parts.append(f"Color: {result['color']}")
            self.state['inventory'].append(f"Color:{result['color']}")
        elif result.get('type') == 'shape':
            text_parts.append(f"Shape: {result['shape']}")
            self.state['inventory'].append(f"Shape:{result['shape']}")
        elif result.get('type') == 'barcode':
            text_parts.append(f"Barcode: {result['data']}")
            self.state['inventory'].append(f"Barcode:{result['data']}")
        else:
            text_parts.append("Unknown signature")
        
        self.state['inventory'] = list(set(self.state['inventory']))
        return " | ".join(text_parts)
    
    def check_puzzle_solution(self, result):
        level = self.get_current_level()
        if not level:
            return False
        
        req = level.get('requirement', {})
        
        if 'color' in req and result.get('type') == 'color':
            detected = result.get('color', '').lower()
            required = req['color'].lower()
            if required in detected or detected in required:
                return True
        
        if 'qr_contains' in req and result.get('type') == 'qr':
            if req['qr_contains'] in result.get('data', ''):
                return True
        
        if 'shape' in req and result.get('type') == 'shape':
            if result.get('shape', '').lower() == req['shape'].lower():
                return True
        
        if 'barcode' in req and result.get('type') == 'barcode':
            return True
        
        if req.get('randomized'):
            actual = level.get('actual_requirement', {})
            if actual.get('type') == result.get('type'):
                if result.get('color') == actual.get('value') or result.get('shape') == actual.get('value') or actual.get('value') in result.get('data', ''):
                    return True
        
        if req.get('any'):
            return True
            
        return False
    
    def advance_level(self):
        self.state['current_level'] += 1
        self.state['scans_this_level'] = []
        
        if self.state['current_level'] >= len(LEVELS):
            self.state['game_complete'] = True
            return "[CRITICAL] Final sector accessed."
        
        level = self.get_current_level()
        return f"[SECTOR {self.state['current_level']}] Access granted.\n{level.get('intro', '')}"
    
    def check_victory(self):
        return self.state['game_complete']
    
    def load_game(self):
        loaded = self.save_manager.load()
        if loaded:
            self.state = loaded
