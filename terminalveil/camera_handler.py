"""
Terminal Veil - Camera Processing
OpenCV-based image analysis
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
        """Fixed: Return first match immediately, don't overwrite"""
        
        # Check QR first
        if mode in ['qr', 'any']:
            qr = self.scan_qr(frame)
            if qr:
                return {'type': 'qr', 'data': qr}
        
        # Check Barcode
        if mode in ['barcode', 'any']:
            bc = self.scan_barcode(frame)
            if bc:
                return {'type': 'barcode', 'data': bc}
        
        # Check Color - RETURN IMMEDIATELY if found
        if mode in ['color', 'any']:
            color = self.detect_color(frame)
            if color:
                return {'type': 'color', 'color': color}  # Return
        
        # Only check shape if color wasn't found (mode=any) or mode=shape specifically
        if mode in ['shape', 'any']:
            shape = self.detect_shape(frame)
            if shape:
                return {'type': 'shape', 'shape': shape}
        
        # Nothing found
        return {'type': 'any', 'raw': True}
    
    def scan_qr(self, image):
        try:
            decoded = decode(image)
            for obj in decoded:
                if obj.type == 'QRCODE':
                    return obj.data.decode('utf-8')
        except Exception as e:
            print(f"QR error: {e}")
        return None
    
    def scan_barcode(self, image):
        try:
            decoded = decode(image)
            for obj in decoded:
                if obj.type in ['EAN13', 'EAN8', 'UPCA', 'CODE128']:
                    return obj.data.decode('utf-8')
        except Exception as e:
            print(f"Barcode error: {e}")
        return None
    
    def detect_color(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        max_ratio = 0
        detected = None
        
        for name, (lower, upper) in self.color_ranges.items():
            if name == 'red2':
                continue
            
            lower_np = np.array(lower, dtype=np.uint8)
            upper_np = np.array(upper, dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_np, upper_np)
            
            if name == 'red':
                lower2 = np.array(self.color_ranges['red2'][0], dtype=np.uint8)
                upper2 = np.array(self.color_ranges['red2'][1], dtype=np.uint8)
                mask2 = cv2.inRange(hsv, lower2, upper2)
                mask = mask + mask2
            
            ratio = cv2.countNonZero(mask) / (image.shape[0] * image.shape[1])
            if ratio > 0.15 and ratio > max_ratio:
                max_ratio = ratio
                detected = name
        
        return detected
    
    def detect_shape(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 1000:
                continue
            
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            
            if len(approx) == 3:
                return "triangle"
            elif len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                if 0.9 <= float(w)/h <= 1.1:
                    return "square"
            elif len(approx) > 4:
                (x, y), r = cv2.minEnclosingCircle(cnt)
                if abs((np.pi * r * r) - area) < area * 0.2:
                    return "circle"
        
        return None
