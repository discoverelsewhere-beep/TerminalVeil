"""
Terminal Veil - Kivy Edition (iOS/Android Ready)
"""
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
from kivy.animation import Animation
from kivy.core.audio import SoundLoader

# Game logic imports
from terminalveil.terminal import GameEngine

# Retro terminal settings
Window.clearcolor = (0, 0, 0, 1)
Window.softinput_mode = 'pan'  # For mobile keyboard

class RetroLabel(Label):
    """Green phosphor terminal text"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Courier'  # iOS has Courier
        self.color = (0, 1, 0, 1)  # Green
        self.markup = True
        self.font_size = '14sp'
        self.halign = 'left'
        self.valign = 'top'
        self.text_size = (None, None)
        self.size_hint_y = None
        self.bind(texture_size=self.setter('size'))

class TerminalOutput(ScrollView):
    """Scrollable terminal history"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        self.history = []
        
    def add_line(self, text, color='00FF00'):
        line = RetroLabel(
            text=f'[color={color}]{text}[/color]',
            size_hint_y=None
        )
        line.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1] + 5))
        self.layout.add_widget(line)
        self.history.append(text)
        Clock.schedule_once(lambda dt: self.scroll_to(line), 0.1)
    
    def clear(self):
        self.layout.clear_widgets()
        self.history = []

class TerminalInput(TextInput):
    """Command input with history"""
    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.multiline = False
        self.background_color = (0, 0.05, 0, 1)
        self.foreground_color = (0, 1, 0, 1)
        self.cursor_color = (0, 1, 0, 1)
        self.font_name = 'Courier'
        self.font_size = '16sp'
        self.hint_text = 'Enter command...'
        self.hint_text_color = (0, 0.3, 0, 1)
        self.padding = [10, 10]
        self.history = []
        self.history_index = -1
        
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Handle up/down for history"""
        if keycode[1] == 'up':
            if self.history and self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.text = self.history[-(self.history_index + 1)]
        elif keycode[1] == 'down':
            if self.history_index > 0:
                self.history_index -= 1
                self.text = self.history[-(self.history_index + 1)]
            else:
                self.history_index = -1
                self.text = ''
        elif keycode[1] == 'return':
            if self.callback and self.text.strip():
                self.history.insert(0, self.text)
                self.history_index = -1
                self.callback(self.text)
                self.text = ''
        return super().keyboard_on_key_down(window, keycode, text, modifiers)

class CameraPopup(Popup):
    """Camera interface for scanning"""
    def __init__(self, mode='any', on_capture=None, **kwargs):
        super().__init__(**kwargs)
        self.title = 'NEURAL LINK // SCANNING'
        self.title_color = (0, 1, 0, 1)
        self.title_size = '16sp'
        self.background_color = (0, 0, 0, 0.95)
        self.size_hint = (0.95, 0.8)
        self.auto_dismiss = False
        
        self.mode = mode
        self.on_capture = on_capture
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Status
        self.status = RetroLabel(
            text='Align object and tap CAPTURE',
            size_hint_y=None,
            height=30
        )
        layout.add_widget(self.status)
        
        # Camera widget (Kivy's native camera)
        self.camera = Camera(
            play=True,
            resolution=(640, 480),
            size_hint_y=0.7
        )
        layout.add_widget(self.camera)
        
        # Buttons
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        capture_btn = Button(
            text='CAPTURE',
            background_color=(0, 0.2, 0, 1),
            color=(0, 1, 0, 1),
            font_name='Courier',
            font_size='16sp'
        )
        capture_btn.bind(on_press=self.capture)
        
        cancel_btn = Button(
            text='ABORT',
            background_color=(0.2, 0, 0, 1),
            color=(1, 0, 0, 1),
            font_name='Courier',
            font_size='16sp'
        )
        cancel_btn.bind(on_press=self.dismiss)
        
        btn_box.add_widget(capture_btn)
        btn_box.add_widget(cancel_btn)
        layout.add_widget(btn_box)
        
        self.add_widget(layout)
        
        # Auto-capture for QR mode after 3 seconds
        if mode == 'qr':
            Clock.schedule_once(lambda dt: self.auto_capture(), 3)
    
    def auto_capture(self):
        """Auto capture for QR"""
        self.status.text = 'AUTO-DETECTING...'
        self.capture(None)
    
    def capture(self, instance):
        self.status.text = 'ANALYZING...'
        # Export texture to analyze
        if self.camera.texture:
            self.analyze_frame()
    
    def analyze_frame(self):
        """Process camera frame"""
        try:
            from camera_handler import CameraAnalyzer
            import numpy as np
            
            # Get texture pixels
            texture = self.camera.texture
            pixels = texture.pixels
            size = texture.size
            
            # Convert to numpy array (RGBA)
            image = np.frombuffer(pixels, np.uint8)
            image = image.reshape(size[1], size[0], 4)
            
            # Convert to BGR for OpenCV
            import cv2
            frame = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            
            # Analyze
            analyzer = CameraAnalyzer()
            results = analyzer.analyze_frame(frame, self.mode)
            
            if self.on_capture:
                self.on_capture(results)
            self.dismiss()
            
        except Exception as e:
            self.status.text = f'ERROR: {str(e)[:20]}'
            print(f"Camera error: {e}")

class TerminalVeilUI(BoxLayout):
    """Main UI container"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5
        
        # Initialize game engine
        self.engine = GameEngine(self)
        
        # Header
        header = RetroLabel(
            text='TERMINAL VEIL v2.0 // SECURE CONNECTION',
            size_hint_y=None,
            height=40,
            font_size='18sp',
            halign='center'
        )
        header.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.add_widget(header)
        
        # Terminal output
        self.output = TerminalOutput(size_hint_y=0.75)
        self.add_widget(self.output)
        
        # Status bar
        self.status_bar = RetroLabel(
            text='SYSTEM READY',
            size_hint_y=None,
            height=25,
            font_size='12sp',
            color=(0, 0.6, 0, 1)
        )
        self.add_widget(self.status_bar)
        
        # Input area
        input_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        
        self.prompt = RetroLabel(text='>', size_hint_x=None, width=20)
        input_layout.add_widget(self.prompt)
        
        self.input = TerminalInput(callback=self.process_command, size_hint_x=0.6)
        input_layout.add_widget(self.input)
        
        # Control buttons (mobile-friendly)
        btn_layout = BoxLayout(size_hint_x=0.4, spacing=5)
        
        scan_btn = Button(
            text='SCAN',
            background_color=(0, 0.3, 0, 1),
            color=(0, 1, 0, 1),
            font_name='Courier'
        )
        scan_btn.bind(on_press=lambda x: self.open_scan_menu())
        
        save_btn = Button(
            text='SAVE',
            background_color=(0, 0.2, 0.2, 1),
            color=(0, 1, 0, 1),
            font_name='Courier'
        )
        save_btn.bind(on_press=lambda x: self.save_game())
        
        load_btn = Button(
            text='LOAD',
            background_color=(0.2, 0.2, 0, 1),
            color=(0, 1, 0, 1),
            font_name='Courier'
        )
        load_btn.bind(on_press=lambda x: self.load_game())
        
        btn_layout.add_widget(scan_btn)
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(load_btn)
        input_layout.add_widget(btn_layout)
        
        self.add_widget(input_layout)
        
        # Boot sequence
        self.boot_sequence()
        
        # Blink cursor
        Clock.schedule_interval(self.blink_cursor, 0.5)
        
        # Focus input
        Clock.schedule_once(lambda dt: setattr(self.input, 'focus', True), 0.5)
    
    def boot_sequence(self):
        lines = [
            ("TERMINAL VEIL v2.0 // MIXED-REALITY PROTOCOL", "00FF00"),
            ("Initializing...", "00AA00"),
            ("Camera subsystem... STANDBY", "00FF00"),
            ("Database... CONNECTED", "00AA00"),
            ("", "00FF00"),
            ("Type 'help' or tap SCAN", "00FFFF"),
            ("", "00FF00"),
        ]
        for i, (text, color) in enumerate(lines):
            Clock.schedule_once(lambda dt, t=text, c=color: self.output.add_line(t, c), i * 0.2)
        
        Clock.schedule_once(lambda dt: self.show_game_text(), len(lines) * 0.2 + 0.3)
    
    def show_game_text(self):
        desc = self.engine.get_current_description()
        self.typewriter_effect(desc)
    
    def typewriter_effect(self, text):
        """Typewriter effect for story text"""
        def add_char(idx):
            if idx <= len(text):
                partial = text[:idx]
                if self.output.layout.children:
                    self.output.layout.remove_widget(self.output.layout.children[0])
                self.output.add_line(partial, '00FF00')
                Clock.schedule_once(lambda dt: add_char(idx + 1), 0.01)
        add_char(0)
    
    def blink_cursor(self, dt):
        self.cursor_visible = getattr(self, 'cursor_visible', True)
        self.cursor_visible = not self.cursor_visible
        color = (0, 1, 0, 1) if self.cursor_visible else (0, 0.2, 0, 1)
        self.prompt.color = color
    
    def process_command(self, cmd):
        self.output.add_line(f'> {cmd}', '00AA00')
        
        if cmd.lower().startswith('scan'):
            mode = 'any'
            if 'qr' in cmd.lower():
                mode = 'qr'
            elif 'color' in cmd.lower():
                mode = 'color'
            elif 'shape' in cmd.lower():
                mode = 'shape'
            self.open_camera(mode)
        else:
            response = self.engine.process_command(cmd)
            if response:
                if 'error' in response.lower() or 'unknown' in response.lower():
                    self.output.add_line(response, 'FF0000')
                else:
                    self.output.add_line(response, '00FF00')
            
            if self.engine.check_victory():
                self.show_victory()
            
            self.update_status()
    
    def open_scan_menu(self, *args):
        """Simple scan mode selection"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        modes = [
            ('any', 'AUTOMATIC'),
            ('qr', 'QR CODE'),
            ('color', 'COLOR'),
            ('shape', 'SHAPE')
        ]
        
        for mode, label in modes:
            btn = Button(
                text=label,
                size_hint_y=None,
                height=50,
                background_color=(0, 0.3, 0, 1),
                color=(0, 1, 0, 1)
            )
            btn.bind(on_press=lambda x, m=mode: (popup.dismiss(), self.open_camera(m)))
            content.add_widget(btn)
        
        cancel_btn = Button(
            text='CANCEL',
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0, 0, 1),
            color=(1, 0, 0, 1)
        )
        content.add_widget(cancel_btn)
        
        popup = Popup(
            title='SELECT SCAN MODE',
            content=content,
            size_hint=(0.8, 0.6),
            background_color=(0, 0, 0, 0.9)
        )
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def open_camera(self, mode):
        popup = CameraPopup(mode=mode, on_capture=self.handle_scan_result)
        popup.open()
    
    def handle_scan_result(self, result):
        if not result or 'error' in result:
            self.output.add_line('SCAN FAILED', 'FF0000')
            return
        
        result_text = self.engine.process_scan_result(result)
        self.output.add_line(f'[SCAN] {result_text}', '00FFFF')
        
        if self.engine.check_puzzle_solution(result):
            self.output.add_line('>>> ACCESS GRANTED <<<', '00FF00')
            self.output.add_line(self.engine.advance_level(), 'FFFF00')
            Clock.schedule_once(lambda dt: self.show_game_text(), 0.5)
        else:
            self.output.add_line('Data archived. Lock engaged.', 'FFA500')
        
        self.update_status()
    
    def update_status(self):
        lvl = self.engine.state['current_level'] + 1
        inv = len(self.engine.state['inventory'])
        self.status_bar.text = f'SECTOR: {lvl}/8 | INVENTORY: {inv} items'
    
    def save_game(self):
        if self.engine.save_manager.save(self.engine.state):
            self.output.add_line('PROGRESS SAVED', '00FF00')
        else:
            self.output.add_line('SAVE ERROR', 'FF0000')
    
    def load_game(self):
        loaded = self.engine.save_manager.load()
        if loaded:
            self.engine.state = loaded
            self.output.add_line('SESSION RESTORED', '00FF00')
            self.output.add_line(self.engine.get_current_description(), '00FF00')
            self.update_status()
        else:
            self.output.add_line('NO SAVE DATA', 'FF0000')
    
    def show_victory(self):
        self.output.add_line('', '00FF00')
        self.output.add_line('*** SYSTEM BREACH SUCCESSFUL ***', '00FFFF')
        self.output.add_line('The Veil has been lifted.', '00FFFF')
        self.output.add_line('Reality is code.', '00FFFF')

class TerminalVeilApp(App):
    def build(self):
        # Request permissions on mobile
        self.request_permissions()
        return TerminalVeilUI()
    
    def request_permissions(self):
        """Handle Android/iOS permissions"""
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
        except:
            pass  # Not on Android
    
    def on_pause(self):
        """Handle app pause on mobile"""
        return True

if __name__ == '__main__':
    TerminalVeilApp().run()