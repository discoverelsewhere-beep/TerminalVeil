# Terminal Veil v2.0

**The hardest mixed-reality puzzle game ever created.**

Scan real-world objects (colors, shapes, QR codes, barcodes) to solve 13 increasingly difficult puzzles. Only 1% of players will complete The Alpha-Omega Protocol.

![Terminal Veil Icon](resources/icon.png)

## 🎮 Play Now

**Web:** https://terminalveilproject.onrender.com

**itch.io:** https://anointedchaos.itch.io/terminal-veil

## 🏆 Features

- **13 Sectors** of progressive difficulty
- **Hall of Fame** - Compete for fewest attempts
- **Analytics** - Track completion rates
- **Easter Eggs** - Hidden secrets throughout
- **File Upload** - Play without camera
- **Extreme Difficulty** - Levels 10-12 are brutally hard

## 📊 The 13 Sectors

### Tutorial (Easy)
1. **Calibration** - Scan anything
2. **Crimson Gate** - Find RED
3. **Encoded Transmission** - QR: "VEIL-42"

### Medium
4. **Geometric Lock** - Show CIRCLE
5. **Dual Authentication** - BLUE + QR "END"
6. **Commercial District** - Any barcode
7. **Triangular Paradox** - Show TRIANGLE

### Hard
8. **The Final Veil** - Random requirement
9. **The Chromatic Cascade** - Find GREEN
10. **The Data Convergence** - QR "SYNC-9" + YELLOW

### EXTREME (Legendary Difficulty)
11. **The Geometric Ascension** - Scan 3 shapes in ORDER (Triangle→Square→Circle). One mistake = RESET
12. **The Synaptic Firewall** - SIMULTANEOUS: Barcode + RED in ONE frame
13. **The Alpha-Omega Protocol** - 4-part ritual: QR "ALPHA"→YELLOW→TRIANGLE→QR "OMEGA". One error = TOTAL RESET

## 🎯 Commands

- `help` - Show commands
- `hint` - Get puzzle hint
- `lore` - Read backstory
- `secret` - Hidden knowledge
- `status` - Show progress
- `hof` - Hall of Fame
- `name [your-name]` - Set player name
- `save` / `load` - Save progress

## 🚀 Quick Start (Local)

```bash
cd ~/TerminalVeil
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5494`

## 📱 QR Codes Needed

See [docs/QR_CODES.md](docs/QR_CODES.md) for all QR codes.

Quick links:
- [VEIL-42](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=VEIL-42)
- [END](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=END)
- [ALPHA](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=ALPHA)
- [OMEGA](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=OMEGA)

## 🏅 Hall of Fame

Complete all 13 sectors to enter the Hall of Fame. Lower attempts = higher rank.

**Current Stats:**
- Total Plays: [Check in-game with `hof` command]
- Completion Rate: ~1%

## 📦 Project Structure

```
TerminalVeil/
├── app_sync.py          # Flask server
├── terminalveil/        # Game package
│   ├── terminal.py      # Game engine
│   ├── puzzles.py       # 13 level definitions
│   ├── camera_handler.py # Computer vision
│   ├── analytics.py     # Stats & Hall of Fame
│   └── save_manager.py  # Save/load
├── templates/
│   └── index.html       # Web UI
└── docs/
    ├── QR_CODES.md      # All QR codes
    └── SCREENSHOTS_GUIDE.md
```

## 🔒 Privacy

See [PRIVACY_POLICY.md](PRIVACY_POLICY.md). We collect minimal data - just game analytics.

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Can you break The Veil?** 🎮
