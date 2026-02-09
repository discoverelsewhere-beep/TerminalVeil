"""
Terminal Veil - iOS Edition
Uses ios_camera_handler for iOS compatibility.
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.core.window import Window

# iOS-specific imports
from terminalveil.terminal import GameEngine
from terminalveil.ios_camera_handler import IOSCameraAnalyzer

Window.clearcolor = (0, 0, 0, 1)

class RetroLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Courier'
        self.color = (0, 1, 0, 1)
        self.markup = True
        self.font_size = '14sp'
        self.halign = 'left'
        self.valign = 'top'
        self.text_size = (None, None)
        self.size_hint_y = None
        self.bind(texture_size=self.setter('size'))

class TerminalOutput(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        self.history = []
        
    def add_line(self, text, color='00FF00'):
        line = RetroLabel(text=f'[color={color}]{text}[/color]', size_hint_y=None)
        line.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1] + 5))
        self.layout.add_widget(line)
        self.history.append(text)
        Clock.schedule_once(lambda dt: self.scroll_to(line), 0.1)

class TerminalInput(TextInput):
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
        self.padding = [10, 10]
        self.history = []
        self.history_index = -1
        
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
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

class IOSCameraPopup(Popup):
    """iOS Camera with manual code entry fallback"""
    def __init__(self, mode='any', on_capture=None, **kwargs):
        super().__init__(**kwargs)
        self.title = 'NEURAL LINK // SCANNING'
        self.title_color = (0, 1, 0, 1)
        self.background_color = (0, 0, 0, 0.95)
        self.size_hint = (0.95, 0.9)
        self.auto_dismiss = False
        
        self.mode = mode
        self.on_capture = on_capture
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        self.status = RetroLabel(
            text='Align object and tap CAPTURE',
            size_hint_y=None, height=30
        )
        layout.add_widget(self.status)
        
        # Camera
        self.camera = Camera(play=True, resolution=(640, 480), size_hint_y=0.5)
        layout.add_widget(self.camera)
        
        # Buttons
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        capture_btn = Button(
            text='CAPTURE',
            background_color=(0, 0.2, 0, 1),
            color=(0, 1, 0, 1),
            font_name='Courier'
        )
        capture_btn.bind(on_press=self.capture)
        
        cancel_btn = Button(
            text='ABORT',
            background_color=(0.2, 0, 0, 1),
            color=(1, 0, 0, 1),
            font_name='Courier'
        )
        cancel_btn.bind(on_press=self.dismiss)
        
        btn_box.add_widget(capture_btn)
        btn_box.add_widget(cancel_btn)
        layout.add_widget(btn_box)
        
        # Manual entry for QR/barcode
        if mode in ['qr', 'barcode']:
            layout.add_widget(RetroLabel(
                text='--- Or enter manually ---',
                size_hint_y=None, height=30,
                halign='center'
            ))
            self.manual_input = TextInput(
                multiline=False,
                background_color=(0.1, 0.1, 0.1, 1),
                foreground_color=(0, 1, 0, 1),
                font_name='Courier',
                hint_text='Type code here...',
                size_hint_y=None, height=40
            )
            layout.add_widget(self.manual_input)
            
            manual_btn = Button(
                text='SUBMIT MANUAL',
                background_color=(0, 0.2, 0.2, 1),
                color=(0, 1, 1, 1),
                font_name='Courier',
                size_hint_y=None, height=45
            )
            manual_btn.bind(on_press=self.manual_submit)
            layout.add_widget(manual_btn)
        
        self.add_widget(layout)
    
    def capture(self, instance):
        if self.camera.texture:
            self.status.text = 'ANALYZING...'
            try:
                import numpy as np
                texture = self.camera.texture
                pixels = texture.pixels
                size = texture.size
                
                image = np.frombuffer(pixels, np.uint8)
                image = image.reshape(size[1], size[0], 4)
                
                analyzer = IOSCameraAnalyzer()
                results = analyzer.analyze_frame(image, self.mode)
                
                if self.on_capture:
                    self.on_capture(results)
                self.dismiss()
            except Exception as e:
                self.status.text = f'ERROR: {str(e)[:25]}'
    
    def manual_submit(self, instance):
        code = self.manual_input.text.strip()
        if code:
            if self.on_capture:
                self.on_capture({'type': self.mode, 'data': code})
            self.dismiss()

class IOSVeilUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5
        
        self.engine = GameEngine(self)
        
        # Header
        header = RetroLabel(
            text='TERMINAL VEIL v2.0 // iOS EDITION',
            size_hint_y=None, height=40,
            font_size='18sp', halign='center'
        )
        header.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self.add_widget(header)
        
        # Output
        self.output = TerminalOutput(size_hint_y=0.75)
        self.add_widget(self.output)
        
        # Status
        self.status_bar = RetroLabel(
            text='SYSTEM READY', size_hint_y=None, height=25,
            font_size='12sp', color=(0, 0.6, 0, 1)
        )
        self.add_widget(self.status_bar)
        
        # Input area
        input_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        
        self.prompt = RetroLabel(text='>', size_hint_x=None, width=20)
        input_layout.add_widget(self.prompt)
        
        self.input = TerminalInput(callback=self.process_command, size_hint_x=0.6)
        input_layout.add_widget(self.input)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_x=0.4, spacing=5)
        
        scan_btn = Button(text='SCAN', background_color=(0, 0.3, 0, 1), 
                         color=(0, 1, 0, 1), font_name='Courier')
        scan_btn.bind(on_press=lambda x: self.open_camera('any'))
        
        save_btn = Button(text='SAVE', background_color=(0, 0.2, 0.2, 1),
                         color=(0, 1, 0, 1), font_name='Courier')
        save_btn.bind(on_press=lambda x: self.save_game())
        
        btn_layout.add_widget(scan_btn)
        btn_layout.add_widget(save_btn)
        input_layout.add_widget(btn_layout)
        
        self.add_widget(input_layout)
        
        self.boot_sequence()
        Clock.schedule_interval(self.blink_cursor, 0.5)
    
    def boot_sequence(self):
        lines = [
            ("TERMINAL VEIL v2.0 // iOS EDITION", "00FF00"),
            ("Initializing neural interface...", "00AA00"),
            ("Camera: NATIVE iOS", "00FF00"),
            ("Ready for mixed-reality protocol.", "00FFFF"),
            ("", "00FF00"),
            ("Type 'help' or tap SCAN", "00FFFF"),
        ]
        for i, (text, color) in enumerate(lines):
            Clock.schedule_once(lambda dt, t=text, c=color: self.output.add_line(t, c), i * 0.2)
        Clock.schedule_once(lambda dt: self.show_game_text(), len(lines) * 0.2 + 0.3)
    
    def show_game_text(self):
        desc = self.engine.get_current_description()
        self.output.add_line(desc, '00FF00')
    
    def blink_cursor(self, dt):
        self.cursor_visible = getattr(self, 'cursor_visible', True)
        self.cursor_visible = not self.cursor_visible
        self.prompt.color = (0, 1, 0, 1) if self.cursor_visible else (0, 0.2, 0, 1)
    
    def process_command(self, cmd):
        self.output.add_line(f'> {cmd}', '00AA00')
        
        if cmd.lower().startswith('scan'):
            self.open_camera('any')
        else:
            response = self.engine.process_command(cmd)
            if response:
                self.output.add_line(response, '00FF00')
            if self.engine.check_victory():
                self.show_victory()
            self.update_status()
    
    def open_camera(self, mode):
        popup = IOSCameraPopup(mode=mode, on_capture=self.handle_scan_result)
        popup.open()
    
    def handle_scan_result(self, result):
        if 'error' in result:
            self.output.add_line(f'SCAN: {result["error"]}', 'FF0000')
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
        self.status_bar.text = f'SECTOR: {lvl}/8 | INVENTORY: {inv}'
    
    def save_game(self):
        if self.engine.save_manager.save(self.engine.state):
            self.output.add_line('PROGRESS SAVED', '00FF00')
        else:
            self.output.add_line('SAVE ERROR', 'FF0000')
    
    def show_victory(self):
        self.output.add_line('', '00FF00')
        self.output.add_line('*** SYSTEM BREACH SUCCESSFUL ***', '00FFFF')
        self.output.add_line('The Veil has been lifted.', '00FFFF')

class TerminalVeilIOSApp(App):
    def build(self):
        try:
            from ios.permissions import request_permission
            request_permission('camera')
        except:
            pass
        return IOSVeilUI()
    
    def on_pause(self):
        return True

if __name__ == '__main__':
    TerminalVeilIOSApp().run()
