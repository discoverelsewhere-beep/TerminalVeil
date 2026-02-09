# Terminal Veil - Build Instructions

## Web Edition (Recommended)

The web edition works on iPhone, Android, and Desktop browsers without app store installation.

### Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the server
./run_web.sh
# or
python3 app.py
```

Then open the displayed URL on any device on your network.

### Production Deployment

For public hosting, consider:

1. **PythonAnywhere** - Free tier available
2. **Render** - Simple web service deployment
3. **Heroku** - Easy git-based deployment
4. **Self-hosted** - Run on Raspberry Pi or home server

Example Render deployment:
```yaml
# render.yaml
services:
  - type: web
    name: terminal-veil
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

## iOS Native Build

⚠️ **Note**: iOS native build requires macOS with Xcode and has limited functionality:
- Color detection: ✅ Works
- Shape detection: ✅ Works  
- QR/Barcode: ⚠️ Manual entry only (no OpenCV/pyzbar on iOS)

### Prerequisites

- macOS with Xcode installed
- Python 3.11+ with briefcase: `pip3 install briefcase`

### Build Steps

```bash
# Run the build script
./build_ios.sh

# Or manually:
python3 -m briefcase create ios
python3 -m briefcase build ios
python3 -m briefcase run ios
```

### Xcode Project Location

After creation:
```
build/terminalveil/ios/xcode/TerminalVeil.xcodeproj
```

Open in Xcode to:
- Build for device/simulator
- Sign for App Store distribution
- Test on connected iPhone

## Project Structure

```
TerminalVeil/
├── app.py                  # Flask web server (MAIN ENTRY POINT)
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Briefcase iOS config
├── run_web.sh              # Quick web server script
├── build_ios.sh            # iOS build script
├── terminalveil/           # Game package
│   ├── terminal.py         # Game engine
│   ├── puzzles.py          # 8 level definitions
│   ├── camera_handler.py   # Full OpenCV version
│   ├── ios_camera_handler.py # iOS-compatible version
│   └── save_manager.py     # Save/load system
├── templates/
│   └── index.html          # Web UI
└── resources/              # App icons (iOS)
```

## Game Features

8 puzzle sectors using real-world scanning:

1. **Calibration** - Scan any object
2. **Crimson Gate** - Find RED object
3. **Encoded Transmission** - QR code with "VEIL-42"
4. **Geometric Lock** - CIRCULAR form
5. **Dual Authentication** - BLUE + QR with "END"
6. **Commercial District** - Barcode scan
7. **Triangular Paradox** - TRIANGULAR form
8. **The Final Veil** - Random signature match

## Troubleshooting

### Camera not working on mobile browser
- Ensure you're using HTTPS (required for camera access)
- On iOS: Use Safari (Chrome iOS has camera limitations)
- Allow camera permissions when prompted

### QR codes not scanning
- Ensure good lighting
- Hold device steady
- Try different distances (6-12 inches optimal)

### iOS build fails
- Check Xcode is properly installed: `xcode-select -p`
- Clean build folder: `rm -rf build/`
- Check logs in `logs/briefcase.*.log`
