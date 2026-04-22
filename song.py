import os
import pygame
from typing import Optional
from chart  import Chart
from config import AUDIO_EXTS, SONGS_DIR

DIFFICULTY_PREFIX = {
    "basic": ("Basic", 0),
    "hard":  ("Hard",  1),
}


class Difficulty:
    def __init__(self, label: str, order: int, csv_path: str):
        self.label:    str   = label   
        self.order:    int   = order
        self.csv_path: str   = csv_path
        self.chart:    Chart = Chart()
        self.chart.loadChart(csv_path)

    @property
    def note_count(self) -> int:
        return len(self.chart.notes)

    @property
    def bpm(self) -> float:
        return self.chart.bpm


class Song:
    def __init__(self, folder_path: str):
        self.folder_path:   str             = folder_path
        self.title:         str             = os.path.basename(folder_path)
        self.artist:        str             = ""
        self.audioFile:     str             = ""
        self.coverImage:    Optional[str]   = None   
        self.difficulties:  list[Difficulty] = []  
        self._cover_surf:   Optional[pygame.Surface] = None 

        self._find_files()

    def _find_files(self) -> None:
        csv_files = []
        for fname in sorted(os.listdir(self.folder_path)):
            fpath = os.path.join(self.folder_path, fname)
            ext   = os.path.splitext(fname)[1].lower()
            name  = os.path.splitext(fname)[0]

            if ext in AUDIO_EXTS and not self.audioFile:
                self.audioFile = fpath
            elif ext == ".png" and name.lower() == self.title.lower():
                self.coverImage = fpath
            elif ext == ".csv":
                csv_files.append((name, fpath))

    
        for name, path in csv_files:
            name_lower = name.lower()
            label, order = self.title, 99
            for prefix, (lbl, ord_) in DIFFICULTY_PREFIX.items():
                if name_lower.startswith(prefix):
                    label, order = lbl, ord_
                    break
            self.difficulties.append(Difficulty(label, order, path))

        self.difficulties.sort(key=lambda d: d.order)

    @property
    def chart(self) -> Chart:
        return self.difficulties[0].chart if self.difficulties else Chart()

    @property
    def bpm(self) -> float:
        return self.difficulties[0].bpm if self.difficulties else 120.0

    @property
    def has_chart(self) -> bool:
        return len(self.difficulties) > 0

    def get_cover(self, size: tuple[int, int] = (200, 200)) -> Optional[pygame.Surface]:
        if self._cover_surf is not None:
            return self._cover_surf
        if not self.coverImage or not os.path.exists(self.coverImage):
            return None
        try:
            img = pygame.image.load(self.coverImage).convert()
            self._cover_surf = pygame.transform.smoothscale(img, size)
            return self._cover_surf
        except Exception as e:
            print(f"[Song] Cover load error: {e}")
            return None

    def loadSong(self) -> bool:
        if not self.audioFile:
            print(f"[Song] No audio file: {self.title}")
            return False
        try:
            pygame.mixer.music.load(self.audioFile)
            return True
        except Exception as e:
            print(f"[Song] Load error: {e}")
            return False

    def playSong(self, start: float = 0.0) -> None:
        pygame.mixer.music.play(start=start)

    def stopSong(self) -> None:
        pygame.mixer.music.stop()

    def __repr__(self) -> str:
        diffs = [d.label for d in self.difficulties]
        return f"Song({self.title!r}, bpm={self.bpm}, diffs={diffs})"


def scan_songs(songs_dir: str = SONGS_DIR) -> list[Song]:
    result = []
    if not os.path.isdir(songs_dir):
        os.makedirs(songs_dir, exist_ok=True)
        return result
    for folder_name in sorted(os.listdir(songs_dir)):
        path = os.path.join(songs_dir, folder_name)
        if not os.path.isdir(path):
            continue
        has_audio = any(f.lower().endswith(AUDIO_EXTS) for f in os.listdir(path))
        if has_audio:
            result.append(Song(path))
    return result
