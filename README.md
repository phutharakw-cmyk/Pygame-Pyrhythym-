# Pyrhythym

## Project Description

- **Project by:** Phutharak Wongpitak 6810545841
- **Game Genre:** Rhythm, Music

Pyrhythym is a rhythm game built with Python and Pygame. Notes fall from the top of the screen and the player must hit them in time with the music using keyboard keys and mouse position. The game has 6 lanes — 4 center lanes (D, F, J, K) and 2 side lanes (L/R) tracked by the mouse.

**Data Analytics** window that graphs your performance after each session.

---

## Installation

To clone this project:

```sh
git clone https://github.com/phutharakw-cmyk/Pygame-Pyrhythym-.git
```

To create and run a Python environment for this project:

**Windows:**
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac:**
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **requirements.txt** contents:
> ```
> pygame
> pandas
> matplotlib
> mutagen
> reportlab
> ```

Place your songs in the following folder structure before running:

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

---

## Running Guide

After activating the Python environment, run the game with:

**Windows:**
```bat
python game.py
```

**Mac:**
```sh
python3 game.py
```

---

## Tutorial / Usage

### Playing the game

1. Run `game.py` — the song select screen opens automatically.
2. Use **↑ ↓** to scroll through songs, **← →** to switch difficulty.
3. Press **Enter** (or double-click) to start playing.
4. Hit notes as they reach the bottom line:

| Note type | How to hit |
|-----------|-----------|
| **Tap** (blue) | Press the matching key (D / F / J / K) once |
| **Hold** (orange) | Hold the key down until the note ends |
| **Slide** (green) | Keep your mouse on the correct side of the screen (L = left half, R = right half) |

5. Press **ESC** to quit back to the song select screen.
6. **Data Analytics** press A on the song select screen to open the data analysis window.



## Game Features

- **3 note types** — Tap, Hold, Slide, each with distinct gameplay and scoring
- **Hold note tick scoring** — Hold notes award bonus points every 0.1 s while held
- **6 lanes** — 4 keyboard lanes (D F J K) + 2 mouse-position lanes (L / R)
- **Multiple difficulties** — Basic and Hard charts can exist for the same song
- **Personal best records** — best score, best combo, full-combo and all-perfect flags saved per song per difficulty
- **Post-game result popup** — shows score, accuracy, PERFECT/GOOD/MISS counts, and highlights new bests
- **Data Analytics window** — 5 charts (score line, combo bar, missed-note pie, reaction histogram, performance table) powered by Matplotlib and Pandas

---

## Known Bugs

- **Slide note timing** — the slide result is judged at the exact moment `end_time` is crossed each frame; on low frame rates this can be off by up to one frame (~16 ms).
- **Hold release edge case** — if a Hold note is released and immediately re-pressed within the GOOD window, the second press may register as a new note hit instead of a re-hold.
- **Analytics window on Mac** — `subprocess.Popen` opens the analytics window correctly on Windows; on some Mac setups Tkinter may need to be launched from the main thread. If the window does not appear, run `python analytics.py <SongTitle> <Difficulty>` manually.


---

## Unfinished Works

- **Settings page** — volume and note speed can be changed in code (`settings.py`) but there is no in-game UI panel for adjusting them during play.
- **More difficulty labels** — currently only `Basic_` and `Hard_` prefixes are recognised; support for `Easy_`, `Expert_`, etc. is not yet implemented.
---

## External Sources

Acknowledge to:

1. **Pygame** — game loop, rendering, input, audio playback  
   https://www.pygame.org — LGPL 2.1

2. **Pandas** — CSV loading and data processing in the analytics module  
   https://pandas.pydata.org — BSD 3-Clause

3. **Matplotlib** — all 5 analytics graphs (line, bar, pie, histogram, table)  
   https://matplotlib.org — PSF / BSD

4. **ReportLab** — generating the UML class diagram as a PDF  
   https://www.reportlab.com — BSD

> **Music & art:** For the music, I used tracks from T+PAZOLITE, which can be used free of charge for both personal and commercial rhythm game projects.
Reference: https://c-h-s.me/chs0038/#en
