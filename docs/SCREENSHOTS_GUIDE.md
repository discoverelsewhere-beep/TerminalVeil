# Screenshot & Demo Guide for Terminal Veil

## Required Screenshots

### 1. Desktop Screenshot
**File:** `screenshots/desktop_main.png`

**How to capture:**
```bash
cd ~/TerminalVeil
python3 app.py
# Open browser to http://localhost:5000
# Resize browser to 1280x720
# Screenshot the terminal interface
```

**Should show:**
- Terminal header "TERMINAL VEIL v2.0"
- Green cyberpunk aesthetic
- Command prompt with ">"
- Sample text like "Type 'help' or tap SCAN"

---

### 2. Mobile Screenshot (iPhone/Android)
**File:** `screenshots/mobile_scanning.png`

**How to capture:**
1. Start the server: `python3 app.py`
2. On your phone, open Safari (iOS) or Chrome (Android)
3. Navigate to your computer's IP: `http://YOUR_IP:5000`
4. Tap SCAN button to show camera modal
5. Screenshot the camera interface

**Should show:**
- "NEURAL LINK ACTIVE" title
- SCAN buttons (Take Photo, Photo Library)
- Abort button
- Mobile-optimized layout

---

### 3. Level Progress Screenshot
**File:** `screenshots/level_progress.png`

**Capture:**
- Play through a few levels
- Screenshot showing different sector description
- Show inventory items collected

---

### 4. Victory Screen
**File:** `screenshots/victory.png`

**Capture:**
- Complete all 8 levels
- Screenshot the victory message:
  - "*** SYSTEM BREACH SUCCESSFUL ***"
  - "The Veil has been lifted."
  - "Reality is code."

---

## Demo GIF/Video

### Recommended Tool: Screen Studio or OBS

**Demo Script (30-60 seconds):**

1. **Opening (5s)**
   - Terminal boot sequence
   - "TERMINAL VEIL v2.0 // WEB EDITION"

2. **Command Demo (10s)**
   - Type "help"
   - Show command list
   - Type "look" to see current sector

3. **Scanning Action (20s)**
   - Tap SCAN
   - Show camera modal
   - Scan a QR code (show actual QR on screen)
   - Show "ACCESS GRANTED" message

4. **Progression (10s)**
   - Show advancing to next level
   - Brief glimpse of inventory

5. **End Card (5s)**
   - Victory screen or "Play Now" call to action

### GIF Creation Commands

```bash
# If using ffmpeg to convert video to GIF
ffmpeg -i demo_video.mp4 -vf "fps=30,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" demo.gif

# Optimize for web
gifsicle -O3 --colors 128 -o demo_optimized.gif demo.gif
```

---

## File Locations

```
TerminalVeil/
├── screenshots/
│   ├── desktop_main.png      # 1280x720
│   ├── mobile_scanning.png   # 375x812 (iPhone size)
│   ├── level_progress.png    # Any size
│   └── victory.png           # Any size
├── docs/
│   └── SCREENSHOTS_GUIDE.md  # This file
└── itchio/
    └── demo.gif              # 480px wide, ~2MB max
```

---

## Quick Commands

```bash
# Get your IP for mobile testing
ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1

# Start server
cd ~/TerminalVeil && python3 app.py

# Create screenshots directory
mkdir -p ~/TerminalVeil/screenshots
```

---

## Tips for Good Screenshots

1. **Clean background** - No desktop clutter visible
2. **Good lighting** - For mobile camera screenshots
3. **Clear QR codes** - Print or display QR codes clearly
4. **Consistent theme** - All screenshots same color scheme
5. **Show progression** - Different levels look different

---

## Recommended QR Codes for Testing

**VEIL-42 QR:**
```
https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=VEIL-42
```

**END QR:**
```
https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=END
```
