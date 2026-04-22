# --- Window ---
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
TITLE         = "Pyrhythym"

# --- Paths ---
SONGS_DIR  = "songs"
DATA_DIR   = "data_logs"
ASSETS_DIR = "assets"

# --- Audio extensions ---
AUDIO_EXTS = (".mp3", ".mp4", ".m4a", ".ogg", ".wav")

# --- Layout ---
LANE_WIDTH      = 100   # width of center lane
SIDE_LANE_WIDTH = 160   # width of L/R lanes
CENTER_LANES    = 4
TOTAL_LANES     = 6     # L + 4 center + R

HIT_Y       = SCREEN_HEIGHT - 120   # y position of hit zone line
NOTE_HEIGHT = 30

# --- Judgement windows (seconds) ---
PERFECT_WINDOW = 0.07
GOOD_WINDOW    = 0.13
MISS_WINDOW    = 0.17

# --- Scoring ---
SCORE_PERFECT = 300
SCORE_GOOD    = 100
SCORE_MISS    = 0

# --- Health ---
MAX_HEALTH   = 100.0
DAMAGE_MISS  = 8.0
HEAL_PERFECT = 0.3

# --- Default user settings ---
DEFAULT_MUSIC_VOLUME = 0.8   # 0.0 - 1.0
DEFAULT_SFX_VOLUME   = 0.8
DEFAULT_NOTE_SPEED   = 400   # pixels per second

# --- Colors ---
COLOR_BG          = (15,  15,  25)
COLOR_LANE_CENTER = (30,  30,  50)
COLOR_LANE_SIDE   = (20,  20,  40)
COLOR_HIT_LINE    = (200, 200, 200)
COLOR_NOTE_TAP    = (100, 200, 255)
COLOR_NOTE_HOLD   = (255, 180,  60)
COLOR_NOTE_SLIDE  = (100, 255, 160)
COLOR_PERFECT     = (255, 240, 100)
COLOR_GOOD        = (100, 220, 255)
COLOR_MISS        = (255,  80,  80)
COLOR_TEXT        = (240, 240, 240)
