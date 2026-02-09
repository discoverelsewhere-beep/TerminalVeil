#!/bin/bash
# Terminal Veil iOS Build Script
# Note: iOS build has limited functionality (no OpenCV/pyzbar)
# Web edition recommended for full features

cd "$(dirname "$0")"

echo "Terminal Veil iOS Build"
echo "======================="
echo ""
echo "WARNING: iOS native build has limited camera functionality."
echo "The Web Edition (app.py) is recommended for mobile devices."
echo ""

# Clean previous build
read -p "Clean previous build? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf build/
fi

# Create iOS project
echo "Creating iOS Xcode project..."
python3 -m briefcase create ios

if [ $? -eq 0 ]; then
    echo ""
    echo "Xcode project created at:"
    echo "  build/terminalveil/ios/xcode/TerminalVeil.xcodeproj"
    echo ""
    echo "Open in Xcode to build and run on device/simulator"
else
    echo "Build failed. Check logs in logs/ directory"
fi
