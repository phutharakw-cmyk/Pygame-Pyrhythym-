import json
import os
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Record:
    best_score:   int   = 0
    best_combo:   int   = 0
    play_count:   int   = 0
    all_perfect:  bool  = False   
    full_combo:   bool  = False   


def _record_path(song_folder: str, song_title: str, diff_label: str) -> str:
    safe_title = song_title.replace(" ", "_")
    safe_diff  = diff_label.replace(" ", "_")
    return os.path.join(song_folder, f"{safe_title}_{safe_diff}_record.json")


def load_record(song_folder: str, song_title: str, diff_label: str) -> Record:
    path = _record_path(song_folder, song_title, diff_label)
    if not os.path.exists(path):
        return Record()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return Record(**data)
    except Exception as e:
        print(f"[Record] Load error: {e}")
        return Record()


def save_record(song_folder: str, song_title: str, diff_label: str,
                record: Record) -> None:
    path = _record_path(song_folder, song_title, diff_label)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(record), f, indent=2)
    except Exception as e:
        print(f"[Record] Save error: {e}")


def update_record(song_folder: str, song_title: str, diff_label: str,
                  score: int, max_combo: int, total_notes: int,
                  perfect_count: int, miss_count: int) -> Record:
    """โหลด record เดิม อัปเดต แล้ว save คืน record ใหม่"""
    rec = load_record(song_folder, song_title, diff_label)
    rec.play_count  += 1
    rec.best_score   = max(rec.best_score, score)
    rec.best_combo   = max(rec.best_combo, max_combo)
    if miss_count == 0 :
        rec.full_combo = True
    if perfect_count == total_notes and total_notes > 0:
        rec.all_perfect = True
    save_record(song_folder, song_title, diff_label, rec)
    return rec
