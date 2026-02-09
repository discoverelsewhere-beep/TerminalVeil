"""
Terminal Veil - Camera Processing
OpenCV-based image analysis - FIXED VERSION
"""
import cv2
import numpy as np
from pyzbar.pyzbar import decode

class CameraAnalyzer:
    def __init__(self):
        self.color_ranges = {
            'red': ([0, 100, 100], [10, 255, 255]),
            'red2': ([160, 100, 100], [180, 255, 255]),
            'blue': ([100, 100, 100], [130, 255, 255]),
            'green': ([40, 100, 100], [80, 255, 255]),
            'yellow': ([20, 100, 100], [35, 255, 255])
        }
    
    def analyze_frame(self, frame, mode='any'):
        """
        Analyze frame and return detection result.
        Priority: QR > Barcode > Color > Shape
        """
        
        # Check QR first (highest priority)
        if mode in ['qr', 'any']:
            qr = self.scan_qr(frame)
            if qr:
                return {'type': 'qr', 'data': qr}
        
        # Check Barcode
        if mode in ['barcode', 'any']:
            bc = self.scan_barcode(frame)
            if bc:
                return {'type': 'barcode', 'data': bc}
        
        # Check Color BEFORE shape (color is easier to detect reliably)
        if mode in ['color', 'any']:
            color = self.detect_color(frame)
            if color:
                return {'type': 'color', 'color': color}
        
        # Only check shape if color detection failed or mode is specifically 'shape'
        if mode in ['shape', 'any']:
            shape = self.detect_shape(frame)
            if shape:
                return {'type': 'shape', 'shape': shape}
        
        # Nothing found
        return {'type': 'unknown', 'raw': True}
    
    def scan_qr(self, image):
        """Scan for QR codes"""
        try:
            decoded = decode(image)
            for obj in decoded:
                if obj.type == 'QRCODE':
                    return obj.data.decode('utf-8')
        except Exception as e:
            print(f"QR error: {e}")
        return None
    
    def scan_barcode(self, image):
        """Scan for barcodes (EAN, UPC, CODE128)"""
        try:
            decoded = decode(image)
            for obj in decoded:
                if obj.type in ['EAN13', 'EAN8', 'UPCA', 'CODE128']:
                    return obj.data.decode('utf-8')
        except Exception as e:
            print(f"Barcode error: {e}")
        return None
    
    def detect_color(self, image):
        """Detect dominant color in image - LOWERED THRESHOLD for better detection"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        max_ratio = 0
        detected = None
        
        for name, (lower, upper) in self.color_ranges.items():
            if name == 'red2':
                continue
            
            lower_np = np.array(lower, dtype=np.uint8)
            upper_np = np.array(upper, dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_np, upper_np)
            
            # Special handling for red (two hue ranges)
            if name == 'red':
                lower2 = np.array(self.color_ranges['red2'][0], dtype=np.uint8)
                upper2 = np.array(self.color_ranges['red2'][1], dtype=np.uint8)
                mask2 = cv2.inRange(hsv, lower2, upper2)
                mask = cv2.bitwise_or(mask, mask2)
            
            # Calculate ratio of matching pixels
            total_pixels = image.shape[0] * image.shape[1]
            ratio = cv2.countNonZero(mask) / total_pixels
            
            # LOWERED THRESHOLD from 0.15 to 0.08 (8% of image)
            if ratio > 0.08 and ratio > max_ratio:
                max_ratio = ratio
                detected = name
        
        return detected
    
    def detect_shape(self, image):
        """Detect geometric shapes (triangle, square, circle)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use adaptive thresholding for better results
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_shape = None
        best_area = 0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filter small contours
            if area < 500:
                continue
            
            # Get perimeter and approximate polygon
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            
            shape = None
            
            # Triangle: 3 vertices
            if len(approx) == 3:
                shape = "triangle"
            # Square/Rectangle: 4 vertices
            elif len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h if h > 0 else 0
                # Square has aspect ratio close to 1
                if 0.8 <= aspect_ratio <= 1.2:
                    shape = "square"
            # Circle: many vertices (5+)
            elif len(approx) >= 5:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                circle_area = np.pi * radius * radius
                # Check if contour area matches circle area
                if circle_area > 0 and abs(circle_area - area) / circle_area < 0.3:
                    shape = "circle"
            
            # Keep the largest valid shape
            if shape and area > best_area:
                best_shape = shape
                best_area = area
        
        return best_shape
