# Pyrhythym

## 1. Project Overview

**Pyrhythym** is a rhythm game built with Python and Pygame, where players hit notes that fall from the top of the screen in time with music. The game features 6 lanes — 4 center lanes controlled by keyboard keys (D, F, J, K) and 2 side lanes (Left/Right) tracked by mouse position.

**Data Analytics** window that visualizes player performance across sessions.

**Problem it solves:** Most rhythm games are closed platforms that don't let players add their own songs or study their performance data. Pyrhythym is fully open — players can chart any song they own and then analyze their own reaction time, combo patterns, and accuracy in detail.

**Target users:** Python learners, rhythm game fans, and anyone interested in combining game development with data analysis.

**Key features:**
- 3 note types: **Tap** (press key), **Hold** (hold key), **Slide** (mouse on correct side)
- Hold notes score points continuously while held
- Best score / full combo / all-perfect records saved per song and difficulty
- Post-game result popup with score, accuracy, and comparison to personal best
- Data Analytics window (Tkinter + Matplotlib) with 5 graphs per session
- Supports multiple difficulties per song (Basic, Hard) via separate CSV files

---

## 2. Concept

### 2.1 Background

Rhythm games are one of my favorite genres of games, so I wanted to create something inspired by them.

The game mechanic is kept intentionally simple — four keyboard lanes plus two mouse-position lanes — so the focus stays on timing precision rather than complex finger patterns. The side lanes (Slide notes) are unique because they don't require pressing anything; the player just keeps the mouse on the correct side of the screen, which tests sustained attention rather than reaction speed.


### 2.2 Objectives

- Build a fully playable rhythm game with note spawning, hit detection, and health system
- Store per-session performance data in CSV format and visualize it with 5 chart types
- Save personal best records (score, combo, full combo, all-perfect) per song and difficulty
- Keep all code modular so each part (game, editor, analytics) can be developed independently

---

## 3. UML Class Diagram

[*(See attached UML_Diagram.pdf)*](https://github.com/phutharakw-cmyk/Pygame-Pyrhythym-/blob/main/UML.pdf)

---

## 4. Object-Oriented Programming Implementation

Below is every class in the project with a brief description of its role.

| Class | File | Description |
|---|---|---|
| **Game** | `game.py` | Main entry point. Holds the game loop, manages page switching, and owns Settings, Statistic, and Sound. |
| **Settings** | `settings.py` | Stores runtime user preferences (music volume, SFX volume, note speed). Values can be changed during gameplay. |
| **Config** | `config.py` | Module-level constants that never change at runtime — screen size, lane widths, colours, scoring thresholds. |
| **Sound** | `sound.py` | Loads and plays three sound effects|
| **Select_song_page** | `pages/select_song_page.py` | Song selection screen. Scans the `songs/` folder, displays cover art and difficulty badges, loads personal-best records, and opens the Analytics window. |
| **Gameplay_page** | `pages/gameplay_page.py` | Main gameplay screen. Runs the note-spawning loop, handles keyboard and mouse input, calculates a normalised score out of 100,000, and triggers the result popup on game end. |
| **ResultPopup** | `pages/result_popup.py` | Overlay drawn on top of Gameplay_page after a song ends. Shows score, accuracy, PERFECT/GOOD/MISS breakdown, and NEW BEST / FULL COMBO / ALL PERFECT badges. |
| **Song** | `song.py` | Represents one song folder. Discovers the audio file, cover image, and CSV charts inside the folder. Provides `loadSong()` and `playSong()` wrappers for `pygame.mixer.music`. |
| **Difficulty** | `song.py` | Represents one difficulty level (e.g. Basic, Hard). Holds a label, sort order, and a loaded `Chart` object. |
| **Chart** | `chart.py` | Reads a CSV chart file and builds a list of `Note` objects. Provides `getNotesAtTime()` and `getActiveSlides()` helpers. |
| **Note** | `note.py` | Abstract base class for all note types. Stores `time`, `lane`, `is_hit`, and `is_missed`. Defines `get_y()` for position calculation and abstract `draw()`. |
| **Tap** | `note.py` | Subclass of Note. A single keypress. Implements `checkHit()` which returns True if the input time is within the miss window. |
| **Hold** | `note.py` | Subclass of Note. A key that must be held for a set duration. Accumulates score every 0.1 s via `update_tick()`. Body clips at the hit line once held. |
| **Slide** | `note.py` | Subclass of Note. Falls like a Hold but requires no keypress — only the mouse to be on the correct half of the screen during the note's duration. |
| **Judgement_system** | `judgement_system.py` | Evaluates each note press as PERFECT (±50 ms), GOOD (±100 ms), or MISS. Calculates score with a combo bonus and health damage/heal values. |
| **Gameplay_UI** | `gameplay_ui.py` | Composes `ScreenText` and `HealthBar` and draws the lane background and hit line every frame. |
| **ScreenText** | `gameplay_ui.py` | Renders the score, combo counter, and a fading judgement flash (PERFECT / GOOD / MISS) on screen. |
| **HealthBar** | `gameplay_ui.py` | Draws a colour-shifting HP bar. Decreases on MISS, increases slightly on PERFECT. Signals `is_dead` when HP reaches zero. |
| **Statistic** | `statistic.py` | Accumulates totals across all sessions: total score, max combo, play count, and perfect/good/miss counts. Saved to CSV on exit. |
| **Data_logger** | `statistic.py` | Records detailed per-session data into four logs (score, combo, hit, reaction) and exports them as CSV files at the end of each session. |
| **Record** | `score_record.py` | Dataclass storing the personal best for one song+difficulty: best score, best combo, play count, full-combo flag, and all-perfect flag. Persisted as JSON inside the song folder. |


---

## 5. Statistical Data

### 5a. Data Recording Method

All data is recorded automatically during gameplay with no input from the player. The `Data_logger` class inside `statistic.py` writes to four in-memory lists and exports them as CSV files to the `data_logs/` folder when the song ends.

| Log file | When it is written | How often |
|---|---|---|
| `_score.csv` | Every game update tick | Once every 2 seconds of song time |
| `_combo.csv` | Every game update tick | Only when the combo value changes |
| `_hit.csv` | Every time a note is judged | Once per note (including misses) |
| `_reaction.csv` | Every time a note is not PERFECT | Once per GOOD or MISS note |

Each row includes `session_id` (8-character UUID), `song_id`, and `time` (seconds into the song), so rows from different sessions can be linked and compared.

Personal-best records (`best_score`, `best_combo`, `play_count`, `full_combo`, `all_perfect`) are saved as a JSON file inside each song folder after every session.

### 5b. Data Features

| Feature | Graph type | X-axis | Y-axis | Purpose |
|---|---|---|---|---|
| Player Score every 2 s | Line graph | Time (seconds) | Score (0–100,000) | Shows how quickly the player earns points — a flat section means many misses |
| Player Combo over time | Bar graph | 10-second intervals | Max combo in interval | Reveals which part of the song breaks the player's streak |
| Types of Notes Missed | Pie chart | — | — | Shows which note type (tap / hold / slide) causes the most failures |
| Reaction Time distribution | Histogram + Normal curve | Reaction time (ms) | Density | Positive = hits late, negative = hits early; spread shows consistency |
| Perfect / Good / Miss per session | Table | — | — | Full performance summary across all loaded sessions for easy comparison |

---


## 6. External Sources

The game engine and all tools used are open-source Python libraries. No commercial assets are included in the repository.

| Item | Source | License |
|---|---|---|
| **Pygame** — game loop, rendering, audio | [pygame.org](https://www.pygame.org) | LGPL 2.1 |
| **Pandas** — CSV loading and data processing | [pandas.pydata.org](https://pandas.pydata.org) | BSD 3-Clause |
| **Matplotlib** — all 5 analytics graphs | [matplotlib.org](https://matplotlib.org) | PSF / BSD |
| **ReportLab** — UML PDF generation | [reportlab.com](https://www.reportlab.com) | BSD |

**Music and art:** For the music, I used tracks from T+PAZOLITE, which can be used free of charge for both personal and commercial rhythm game projects.
Reference: https://c-h-s.me/chs0038/#en

## 7. Youtube and Proposal

https://github.com/phutharakw-cmyk/Pygame-Pyrhythym-/blob/main/Proposal_PyRhythm.pdf

https://youtu.be/0KdL-rnnPbk?si=13sRNPFiAvCKCoZi
