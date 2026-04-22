from config import (
    PERFECT_WINDOW, GOOD_WINDOW, MISS_WINDOW,
    SCORE_PERFECT, SCORE_GOOD, SCORE_MISS,
    DAMAGE_MISS, HEAL_PERFECT,
)
from note import Note


class Judgement_system:
    def __init__(self):
        self.perfectWindow: float = PERFECT_WINDOW
        self.goodWindow:    float = GOOD_WINDOW
        self.missWindow:    float = MISS_WINDOW
        self.combo:         int   = 0

    def judge(self, note: Note, input_time: float) -> str:
        diff = abs(input_time - note.time)
        if diff <= self.perfectWindow:
            self.combo += 1
            return "PERFECT"
        elif diff <= self.goodWindow:
            self.combo += 1
            return "GOOD"
        else:
            self.combo = 0
            return "MISS"

    def judgeSlide(self, mouse_correct: bool) -> str:
        if mouse_correct:
            self.combo += 1
            return "PERFECT"
        self.combo = 0
        return "MISS"

    def addScore(self, result: str) -> int:
        base = {
            "PERFECT": SCORE_PERFECT,
            "GOOD":    SCORE_GOOD,
            "MISS":    SCORE_MISS,
        }.get(result, 0)
        bonus = base * (self.combo // 10)
        return base + bonus

    def resetCombo(self) -> None:
        self.combo = 0

    def damageHealth(self, result: str) -> float:
        return DAMAGE_MISS if result == "MISS" else 0.0

    def healHealth(self, result: str) -> float:
        return HEAL_PERFECT if result == "PERFECT" else 0.0
