from config import DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME, DEFAULT_NOTE_SPEED


class Settings:
    def __init__(self):
        self.music_volume: float = DEFAULT_MUSIC_VOLUME
        self.sfx_volume:   float = DEFAULT_SFX_VOLUME
        self.note_speed:   float = DEFAULT_NOTE_SPEED 

    def set_music_volume(self, v: float) -> None:
        self.music_volume = max(0.0, min(1.0, v))

    def set_sfx_volume(self, v: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, v))

    def set_note_speed(self, v: float) -> None:
        self.note_speed = max(100.0, min(1000.0, v))

    def __repr__(self) -> str:
        return (f"Settings(music={self.music_volume:.1f}, "
                f"sfx={self.sfx_volume:.1f}, "
                f"speed={self.note_speed:.0f}px/s)")
