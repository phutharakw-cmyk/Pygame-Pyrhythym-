import pygame
import os
from config import ASSETS_DIR


class Sound:
    def __init__(self):
        self.clickSound: pygame.mixer.Sound | None = None
        self.hitSound:   pygame.mixer.Sound | None = None
        self.missSound:  pygame.mixer.Sound | None = None
        self._load()

    def _load(self) -> None:
        files = {
            "clickSound": os.path.join(ASSETS_DIR, "click.wav"),
            "hitSound":   os.path.join(ASSETS_DIR, "hit.wav"),
            "missSound":  os.path.join(ASSETS_DIR, "miss.wav"),
        }
        
        for attr, path in files.items():
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    setattr(self, attr, sound)
                    print(f"[Sound] Loaded {attr} from {path}")
                else:
                    print(f"[Sound] File not found: {path}")
            except Exception as e:
                print(f"[Sound] Error loading {attr}: {e}")

    def set_volume(self, sfx_volume: float) -> None:
        for s in (self.clickSound, self.hitSound, self.missSound):
            if s:
                s.set_volume(max(0.0, min(1.0, sfx_volume)))

    def playClick(self) -> None:
        try:
            if self.clickSound:
                self.clickSound.play()
        except Exception as e:
            print(f"[Sound] Error playing click: {e}")
