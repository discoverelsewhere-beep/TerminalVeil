"""
Terminal Veil - Analytics and Hall of Fame
Track game completions and statistics
"""
import json
import os
from datetime import datetime

class AnalyticsManager:
    def __init__(self, filename='veil_analytics.json'):
        self.filepath = os.path.join(os.path.expanduser('~'), filename)
        self.data = self._load()
    
    def _load(self):
        """Load analytics data"""
        if not os.path.exists(self.filepath):
            return {
                'total_plays': 0,
                'completions': [],
                'level_reaches': {},  # How many reached each level
                'sector_attempts': {},  # Attempts per sector
                'first_launch': datetime.now().isoformat()
            }
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except:
            return self._load()  # Reset on error
    
    def _save(self):
        """Save analytics data"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Analytics save error: {e}")
    
    def record_game_start(self):
        """Record new game session"""
        self.data['total_plays'] += 1
        self._save()
    
    def record_level_reach(self, level):
        """Record player reaching a level"""
        level_key = f"level_{level}"
        self.data['level_reaches'][level_key] = \
            self.data['level_reaches'].get(level_key, 0) + 1
        self._save()
    
    def record_attempt(self, level):
        """Record attempt at a level"""
        level_key = f"level_{level}"
        self.data['sector_attempts'][level_key] = \
            self.data['sector_attempts'].get(level_key, 0) + 1
        self._save()
    
    def record_completion(self, player_name, attempts, time_taken=None):
        """Record game completion for Hall of Fame"""
        completion = {
            'player': player_name,
            'attempts': attempts,
            'date': datetime.now().isoformat(),
            'time_taken': time_taken
        }
        self.data['completions'].append(completion)
        # Keep only top 10 by attempts (lower is better)
        self.data['completions'].sort(key=lambda x: x['attempts'])
        self.data['completions'] = self.data['completions'][:10]
        self._save()
    
    def get_hall_of_fame(self):
        """Get Hall of Fame entries"""
        return self.data.get('completions', [])
    
    def get_stats(self):
        """Get game statistics"""
        completions = len(self.data.get('completions', []))
        total_plays = self.data.get('total_plays', 0)
        
        # Calculate completion rate
        completion_rate = (completions / total_plays * 100) if total_plays > 0 else 0
        
        # Find most attempted sector
        sector_attempts = self.data.get('sector_attempts', {})
        hardest_sector = max(sector_attempts, key=sector_attempts.get) if sector_attempts else "N/A"
        
        return {
            'total_plays': total_plays,
            'completions': completions,
            'completion_rate': round(completion_rate, 2),
            'hardest_sector': hardest_sector,
            'unique_players': len(set(c['player'] for c in self.data.get('completions', [])))
        }
