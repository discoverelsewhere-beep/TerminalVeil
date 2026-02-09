"""
Terminal Veil - iOS Camera Processing (No OpenCV)
Uses PIL and numpy for basic image analysis.
"""
import numpy as np
from PIL import Image

class IOSCameraAnalyzer:
    """Simplified camera analyzer for iOS without OpenCV/pyzbar"""
    
    def __init__(self):
        # Simple color thresholds in RGB
        self.color_ranges = {
            'red': ((150, 0, 0), (255, 100, 100)),
            'blue': ((0, 0, 150), (100, 100, 255)),
            'green': ((0, 150, 0), (100, 255, 100)),
            'yellow': ((150, 150, 0), (255, 255, 100)),
        }
    
    def analyze_frame(self, frame, mode='any'):
        """
        Analyze a frame from Kivy camera.
        frame should be a numpy array (RGBA from Kivy texture).
        """
        try:
            # Convert to PIL Image
            if isinstance(frame, np.ndarray):
                if frame.shape[2] == 4:  # RGBA
                    frame = frame[:, :, :3]  # Convert to RGB
                img = Image.fromarray(frame)
            else:
                img = frame
            
            # Check for colors
            if mode in ['color', 'any']:
                color = self.detect_color(img)
                if color:
                    return {'type': 'color', 'color': color}
            
            # Check for shapes (simplified)
            if mode in ['shape', 'any']:
                shape = self.detect_shape(img)
                if shape:
                    return {'type': 'shape', 'shape': shape}
            
            # For QR/Barcode on iOS, we'd need native iOS APIs
            # Return placeholder that tells user to enter code manually
            if mode in ['qr', 'barcode']:
                return {
                    'type': 'qr', 
                    'data': 'MANUAL_ENTRY_REQUIRED',
                    'error': 'QR scanning requires manual entry on this build'
                }
            
            return {'type': 'any', 'raw': True}
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_color(self, img):
        """Detect dominant color in image"""
        if isinstance(img, Image.Image):
            img_array = np.array(img)
        else:
            img_array = img
        
        # Resize for faster processing
        small = img_array[::10, ::10]
        
        # Calculate mean colors
        mean_color = np.mean(small, axis=(0, 1))
        r, g, b = mean_color[:3]
        
        # Determine color
        max_val = max(r, g, b)
        if max_val < 50:
            return None  # Too dark
        
        # Check which color channel dominates
        if r > 150 and r > g + 30 and r > b + 30:
            return 'red'
        elif b > 150 and b > r + 30 and b > g + 30:
            return 'blue'
        elif g > 150 and g > r + 30 and g > b + 30:
            return 'green'
        elif r > 150 and g > 150 and b < 100:
            return 'yellow'
        
        return None
    
    def detect_shape(self, img):
        """Simplified shape detection"""
        # For iOS, we'll use a simple approach
        # Check image brightness distribution for circular patterns
        if isinstance(img, Image.Image):
            img_array = np.array(img)
        else:
            img_array = img
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = np.mean(img_array[:, :, :3], axis=2)
        else:
            gray = img_array
        
        # Simple heuristic: check corners vs center
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]
        corner_avg = (gray[0,0] + gray[0,-1] + gray[-1,0] + gray[-1,-1]) / 4
        center_avg = np.mean(center_region)
        
        # If center is brighter, might be a circle/square
        if center_avg > corner_avg + 30:
            # Check aspect ratio to guess circle vs square
            edge_left = np.mean(gray[:, :w//4])
            edge_right = np.mean(gray[:, 3*w//4:])
            edge_top = np.mean(gray[:h//4, :])
            edge_bottom = np.mean(gray[3*h//4:, :])
            
            # If edges are similar, likely a circle
            edge_variance = np.var([edge_left, edge_right, edge_top, edge_bottom])
            if edge_variance < 1000:
                return 'circle'
            else:
                return 'square'
        
        return None
