# statistic.py — Statistic + Data_logger

import csv
import os
import uuid
import glob
from typing import List


class Statistic:
    def __init__(self):
        self.totalScore:   int  = 0
        self.maxCombo:     int  = 0
        self.playCount:    int  = 0
        self.perfectCount: int  = 0
        self.goodCount:    int  = 0
        self.missCount:    int  = 0

    def addScore(self, score: int) -> None:
        self.totalScore += score

    def updateCombo(self, combo: int) -> None:
        if combo > self.maxCombo:
            self.maxCombo = combo

    def addJudgement(self, result: str) -> None:
        if result == "PERFECT":
            self.perfectCount += 1
        elif result == "GOOD":
            self.goodCount += 1
        elif result == "MISS":
            self.missCount += 1

    def getAccuracy(self) -> float:
        total = self.perfectCount + self.goodCount + self.missCount
        if total == 0:
            return 0.0
        return (self.perfectCount + self.goodCount * 0.5) / total * 100.0


class Data_logger:
    """
    เก็บ log ระหว่างเล่น 1 session:
      scoreLog      — score ทุก 5 วินาที                    (bar chart)
      comboLog      — combo ทุกครั้งที่เปลี่ยน               (line chart)
      hitLog        — ทุกครั้งที่โน็ตโดนกด พร้อม result      (table + pie)
      reactionLog   — reaction time ทุกครั้งที่ไม่ perfect   (histogram)
    """

    EXPORT_DIR = "data_logs"
    MAX_SESSIONS = 3  # ตั้งค่าจำนวนที่ต้องการเก็บ

    def __init__(self, song_id: str):
        self.sessionId:  str  = str(uuid.uuid4())[:8]
        self.songId:     str  = song_id # ตัวอย่าง: 'hard_finesse'
        self.scoreLog:   List = []
        self.comboLog:   List = []
        self.hitLog:     List = []
        self.reactionLog: List = []

        self._last_score_log: float = -999.0
        self._last_combo:     int   = -1

    # ── Logging ───────────────────────────────────────────
    def logScore(self, current_time: float, score: int) -> None:
        """บันทึกทุก 5 วินาที"""
        if current_time - self._last_score_log >= 2.0:
            self.scoreLog.append({
                "session_id": self.sessionId,
                "song_id":    self.songId,
                "time":       round(current_time, 3),
                "score":      score,
            })
            self._last_score_log = current_time

    def logCombo(self, current_time: float, combo: int) -> None:
        """บันทึกทุกครั้งที่ combo เปลี่ยน"""
        if combo != self._last_combo:
            self.comboLog.append({
                "session_id": self.sessionId,
                "song_id":    self.songId,
                "time":       round(current_time, 3),
                "combo":      combo,
            })
            self._last_combo = combo

    def logHit(self, current_time: float, note_time: float,
               result: str, note_type: str) -> None:
        """บันทึกทุกครั้งที่โน็ตโดนกด (รวม miss ด้วย)"""
        self.hitLog.append({
            "session_id": self.sessionId,
            "song_id":    self.songId,
            "time":       round(current_time, 3),
            "note_time":  round(note_time, 3),
            "result":     result,
            "note_type":  note_type,
        })

    def logReaction(self, current_time: float,
                    note_time: float, note_type: str) -> None:
        """บันทึก reaction time เมื่อไม่ได้ PERFECT (บวก=ช้า ลบ=เร็ว)"""
        self.reactionLog.append({
            "session_id": self.sessionId,
            "song_id":    self.songId,
            "time":       round(current_time, 3),
            "reaction":   round(current_time - note_time, 4),
            "note_type":  note_type,
        })

    # ── Export ────────────────────────────────────────────
    def export_CSV(self) -> None:
            os.makedirs(self.EXPORT_DIR, exist_ok=True)
            
            # 1. จัดการลบ Session เก่าออกก่อนถ้าเกินโควต้า
            self._manage_old_sessions()

            # 2. บันทึกไฟล์ใหม่ตามปกติ
            prefix = f"{self.songId}_{self.sessionId}"
            self._write(f"{prefix}_score.csv", self.scoreLog, ["session_id", "song_id", "time", "score"])
            self._write(f"{prefix}_combo.csv", self.comboLog, ["session_id", "song_id", "time", "combo"])
            self._write(f"{prefix}_hit.csv", self.hitLog, ["session_id", "song_id", "time", "note_time", "result", "note_type"])
            self._write(f"{prefix}_reaction.csv", self.reactionLog, ["session_id", "song_id", "time", "reaction", "note_type"])

            print(f"[Data_logger] Exported → {self.EXPORT_DIR}/{prefix}_*.csv")

    def _manage_old_sessions(self) -> None:
        """ตรวจสอบไฟล์ในโฟลเดอร์ และลบ session ที่เก่าที่สุดทิ้งถ้าเกิน 3 อัน"""
        # ค้นหาไฟล์ทั้งหมดที่ขึ้นต้นด้วยชื่อเพลงนี้ (ซึ่งมีระดับความยากติดมาอยู่แล้ว)
        search_pattern = os.path.join(self.EXPORT_DIR, f"{self.songId}_*.csv")
        all_files = glob.glob(search_pattern)

        # จับกลุ่มไฟล์ตาม sessionId
        sessions = {}
        for f in all_files:
            # ชื่อไฟล์จะเป็น: hard_song_abcdefgh_score.csv
            # เราจะแยกเอา sessionId (abcdefgh) ออกมา
            parts = os.path.basename(f).replace(f"{self.songId}_", "").split("_")
            if parts:
                s_id = parts[0]
                if s_id not in sessions:
                    sessions[s_id] = os.path.getctime(f)

        # ถ้ามีเกิน 2 session (เพราะเดี๋ยวเรากำลังจะเซฟอันที่ 3 เข้าไป) 
        # หรือถ้าจะเอาเป๊ะๆ คือถ้า len >= 3 ให้ลบอันเก่าสุดออกจนเหลือที่ว่าง 1 ที่
        if len(sessions) >= self.MAX_SESSIONS:
            # เรียงจากเก่าไปใหม่ (ตาม timestamp)
            sorted_sessions = sorted(sessions.items(), key=lambda x: x[1])
            
            # จำนวนที่ต้องลบทิ้งเพื่อให้เหลือที่ว่างสำหรับ session ใหม่
            num_to_delete = len(sessions) - (self.MAX_SESSIONS - 1)
            
            for i in range(num_to_delete):
                old_id = sorted_sessions[i][0]
                # ลบไฟล์ทั้งหมดที่มี ID นี้ (score, combo, hit, reaction)
                files_to_del = glob.glob(os.path.join(self.EXPORT_DIR, f"{self.songId}_{old_id}_*.csv"))
                for f_del in files_to_del:
                    try:
                        os.remove(f_del)
                    except OSError:
                        pass

    def _write(self, filename: str, rows: List, fieldnames: List[str]) -> None:
        path = os.path.join(self.EXPORT_DIR, filename)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
