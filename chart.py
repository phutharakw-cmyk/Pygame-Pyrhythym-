import csv
from typing import List
from note import Note, Tap, Hold, Slide

class Chart:
    def __init__(self):
        self.notes:      List[Note] = []
        self.difficulty: int        = 0
        self.bpm:        float      = 120.0
        self.song_name:  str        = ""

    def loadChart(self, csv_path: str) -> None:
        self.notes.clear()
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
        except FileNotFoundError:
            print(f"[Chart] File not found: {csv_path}")
            return
        except Exception as e:
            print(f"[Chart] Read error: {e}")
            return

        if rows:
            self.song_name = rows[0][0].strip()
        if len(rows) > 1 and len(rows[1]) >= 2:
            try:
                self.bpm = float(rows[1][1])
            except ValueError:
                pass

        for row in rows[3:]:
            if len(row) < 3:
                continue
            note_type = row[0].strip()
            try:
                time = float(row[1])
            except ValueError:
                continue
            lane     = row[2].strip()
            duration = 0.0
            if len(row) > 3 and row[3].strip():
                try:
                    duration = float(row[3])
                except ValueError:
                    pass

            if note_type == "tap":
                self.notes.append(Tap(time, lane))
            elif note_type == "hold":
                self.notes.append(Hold(time, lane, duration))
            elif note_type == "slide":
                self.notes.append(Slide(time, lane, duration))
            else:
                print(f"[Chart] Unknown note type: {note_type}")

        self.notes.sort(key=lambda n: n.time)
        print(f"[Chart] Loaded {len(self.notes)} notes  bpm={self.bpm}")

    def getNotesAtTime(self, time: float, window: float = 0.2) -> List[Note]:
        return [n for n in self.notes
                if n.active and abs(n.time - time) <= window]

    def getActiveSlides(self, time: float) -> List[Slide]:
        return [n for n in self.notes
                if isinstance(n, Slide) and n.active
                and n.time <= time <= n.end_time]
