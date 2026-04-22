## Quick 3-Step Setup

### Step 1: Install pygame
```bash
pip install pygame
```

### Step 2: Organize Files
Create this structure in your project folder:

```
your-project/
├── game.py                  (copy all .py files here)
├── config.py
├── (all other .py files)
│
├── pages/                   (create folder)
│   ├── main_menu_page.py   
│   ├── select_song_page.py
│   ├── gameplay_page.py
│   └── result_popup.py
│
├── assets/                  (create folder)
│   ├── click.wav           (copy these 3 files)
│
└── songs/                   (your existing songs)
    └── (your song folders)
```

### Step 3: Run
```bash
python game.py
```
---

## Controls

### Main Menu
| Key | Action |
|-----|--------|
| ↑↓ | Navigate |
| Enter / Space | Select |
| Mouse | Hover & click |
| ESC | Exit game |

### How to Play
| Key | Action |
|-----|--------|
| ↑↓ | Scroll |
| Mouse Wheel | Scroll |
| ESC / Enter | Close |
| Click Outside | Close |

### Song Selection
| Key | Action |
|-----|--------|
| ↑↓ | Navigate |
| ←→ | Change difficulty |
| Enter | Play |
| ESC | Back to menu |

---

### Data anlysis
1. data_log will collect last 3 session of your play
2. Press A in selectsong page to show data analysis 
3. There are some sample data in data_logs that you can see the analysis
---
## Common Tasks

### How do I play a song?
1. Run `python game.py`
2. Click "START GAME"
3. Select a song with ↑↓
4. Change difficulty with ←→
5. Press Enter to play

### How do I go back?
Press ESC at any time to go back one level.

### How do I read the tutorial?
1. From main menu, click "HOW TO PLAY"
2. Scroll with ↑↓ or mouse wheel
3. Close with ESC/Enter or click outside

### Where are my saved records?
They're saved automatically in each song's folder as JSON files.

---

## System Requirements

- **Python 3.8+**
- **pygame**
- **1280x720 minimum screen resolution**
- **~50MB disk space for base game**
- **No internet required**

---

**Version**: 1.1 (with WAV sound files)  
**Status**: ✅ Production Ready  
**Date**: April 22, 2026

# Pygame-Pyrhythym-
