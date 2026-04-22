# pages/gameplay_page.py — Gameplay

import pygame
from typing import Optional, TYPE_CHECKING

from song             import Song, Difficulty
from note             import Note, Tap, Hold, Slide, get_lane_x
from judgement_system import Judgement_system
from gameplay_ui      import Gameplay_UI
from statistic        import Data_logger
from score_record     import update_record
from pages.result_popup import ResultPopup
from config           import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG,
    MISS_WINDOW, GOOD_WINDOW,
    LANE_WIDTH, HIT_Y,
)

if TYPE_CHECKING:
    from game import Game

MAX_SCORE = 100_000   

_CENTER_LANE_ORDER = ["1", "2", "3", "4"]

def _make_key_lane() -> dict:
    return {pygame.K_d:"1", pygame.K_f:"2",
            pygame.K_j:"3", pygame.K_k:"4"}


def _calc_max_score(total_notes: int) -> int:
    return MAX_SCORE if total_notes == 0 else MAX_SCORE


def _normalize_score(raw: int, raw_max: int) -> int:
    if raw_max <= 0:
        return 0
    return min(MAX_SCORE, int(raw / raw_max * MAX_SCORE))


class Gameplay_page:
    def __init__(self, game: "Game", song: Song, difficulty: Difficulty):
        self.game        = game
        self.currentSong = song
        self.difficulty  = difficulty

        self._perfect: int = 0
        self._good:    int = 0
        self._miss:    int = 0
        self._max_combo: int = 0

        self._raw_score: int = 0
        self._raw_max:   int = 0

        self.score: int = 0
        self.combo: int = 0

        self.ui        = Gameplay_UI()
        self.judgement = Judgement_system()
        self.sound     = game.sound
        self.logger    = Data_logger(f"{song.title}_{difficulty.label}")

        self._key_lane: dict           = _make_key_lane()
        self._start_ticks:  int        = 0
        self._current_time: float      = 0.0
        self._playing:      bool       = False
        self._ended:        bool       = False
        self._holding: dict[str, Hold] = {}
        self._lane_pressed: dict[str, bool] = {l: False for l in "1234"}

        self._popup: Optional[ResultPopup] = None
        self._showing_popup: bool = False

        self._font_hint = pygame.font.SysFont("consolas", 16)

        self.startPlay()

    def _compute_raw_max(self) -> int:
        from note import HOLD_TICK_INTERVAL, HOLD_TICK_SCORE
        from config import SCORE_PERFECT
        total = 0
        for note in self.difficulty.chart.notes:
            if isinstance(note, (Tap, Hold)):
                total += SCORE_PERFECT
            elif isinstance(note, Slide):
                total += SCORE_PERFECT
            if isinstance(note, Hold):
                ticks  = int(note.duration / HOLD_TICK_INTERVAL)
                total += ticks * HOLD_TICK_SCORE
        return max(1, total)

    def startPlay(self) -> None:
        if not self.currentSong.loadSong():
            return
        self._raw_max = self._compute_raw_max()
        self.currentSong.playSong()
        self._start_ticks = pygame.time.get_ticks()
        self._playing     = True
        print(f"[Gameplay] {self.currentSong.title} [{self.difficulty.label}]"
              f"  raw_max={self._raw_max}")

    def endGame(self,finish = True) -> None:
        if self._ended:
            return
        self._ended   = True
        self._playing = False
        self.currentSong.stopSong()
        if finish:
            self.logger.export_CSV()

            self.score = _normalize_score(self._raw_score, self._raw_max)

            total_notes = len(self.difficulty.chart.notes)
            record = update_record(
                song_folder   = self.currentSong.folder_path,
                song_title    = self.currentSong.title,
                diff_label    = self.difficulty.label,
                score         = self.score,
                max_combo     = self._max_combo,
                total_notes   = total_notes,
                perfect_count = self._perfect,
                miss_count    = self._miss,
            )

            is_new_best  = (self.score  >= record.best_score  and self.score  > 0)
            is_new_combo = (self._max_combo >= record.best_combo and self._max_combo > 0)

            self.game.statistic.playCount += 1
            self.game.statistic.addScore(self.score)
            self.game.statistic.updateCombo(self._max_combo)

            print(f"[Gameplay] End — Score:{self.score}  Combo:{self._max_combo}")

            self._popup = ResultPopup(
                song_title   = self.currentSong.title,
                diff_label   = self.difficulty.label,
                score        = self.score,
                max_score    = MAX_SCORE,
                max_combo    = self._max_combo,
                total_notes  = total_notes,
                perfect      = self._perfect,
                good         = self._good,
                miss         = self._miss,
                record       = record,
                is_new_best  = is_new_best,
                is_new_combo = is_new_combo,
            )
            self._showing_popup = True
        else:
            record = update_record(
                    song_folder   = self.currentSong.folder_path,
                    song_title    = self.currentSong.title,
                    diff_label    = self.difficulty.label,
                    score         = 0,
                    max_combo     = 0,
                    total_notes   = 0,
                    perfect_count = 0,
                    miss_count    = -999,
                )
            self._popup = ResultPopup(
                    song_title   = self.currentSong.title,
                    diff_label   = self.difficulty.label,
                    score        = 0,
                    max_score    = 0,
                    max_combo    = 0,
                    total_notes  = 0,
                    perfect      = 0,
                    good         = 0,
                    miss         = 0,
                    record       = record,
                    is_new_best  = False,
                    is_new_combo = False,
                )
            self._showing_popup = True


    def _close_popup(self) -> None:
        self._showing_popup = False
        from pages.select_song_page import Select_song_page
        self.game.change_page(Select_song_page(self.game))

    def handle_events(self, events: list) -> None:
        # popup mode
        if self._showing_popup and self._popup:
            if self._popup.handle_events(events):
                self._close_popup()
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.endGame(False)
                    return
                self._on_key_down(event.key)
            if event.type == pygame.KEYUP:
                self._on_key_up(event.key)

    def update(self, dt: float) -> None:
        if self._showing_popup:
            return
        if not self._playing:
            return

        self._current_time = (pygame.time.get_ticks() - self._start_ticks) / 1000.0
        t = self._current_time

        self._check_miss(t)
        self._tick_holds(t)
        self._check_holds(t)
        self._check_slides(t)

        if self.combo > self._max_combo:
            self._max_combo = self.combo

        self.score = _normalize_score(self._raw_score, self._raw_max)

        self.logger.logScore(t, self.score)
        self.logger.logCombo(t, self.combo)

        self.ui.screenText.updateScore(self.score)
        self.ui.screenText.updateCombo(self.combo)
        self.ui.update(dt)

        notes     = self.difficulty.chart.notes
        last_time = notes[-1].time if notes else 0.0
        if t > last_time + 3.0 and not pygame.mixer.music.get_busy():
            self.endGame()


    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BG)
        self.ui.draw(screen)
        self._draw_lane_glow(screen)
        for note in self.difficulty.chart.notes:
            note.draw(screen, self._current_time,
                      self.game.settings.note_speed, SCREEN_WIDTH)
        self._draw_hud(screen)

        if self._showing_popup and self._popup:
            self._popup.draw(screen)

    def _draw_lane_glow(self, screen: pygame.Surface) -> None:
        total_center = LANE_WIDTH * 4
        start_x      = (SCREEN_WIDTH - total_center) // 2
        glow_h       = 80
        for i, lane in enumerate(_CENTER_LANE_ORDER):
            if not self._lane_pressed.get(lane, False):
                continue
            lx   = start_x + i * LANE_WIDTH
            glow = pygame.Surface((LANE_WIDTH, glow_h), pygame.SRCALPHA)
            glow.fill((255, 220, 80, 60))
            screen.blit(glow, (lx, HIT_Y - glow_h))
            pygame.draw.line(screen, (255, 220, 80),
                             (lx, HIT_Y - glow_h),
                             (lx + LANE_WIDTH, HIT_Y - glow_h), 1)

    def _draw_hud(self, screen: pygame.Surface) -> None:
        hint = self._font_hint.render("ESC to quit", True, (100, 100, 130))
        screen.blit(hint, (SCREEN_WIDTH - hint.get_width() - 16,
                            SCREEN_HEIGHT - hint.get_height() - 12))
        info = self._font_hint.render(
            f"{self.currentSong.title}  [{self.difficulty.label}]",
            True, (100, 100, 130))
        screen.blit(info, (16, SCREEN_HEIGHT - info.get_height() - 12))

    def _on_key_down(self, key: int) -> None:
        lane = self._key_lane.get(key)
        if lane is None:
            return
        self._lane_pressed[lane] = True
        t = self._current_time
        best: Optional[Note] = None
        best_diff = MISS_WINDOW + 0.01
        for note in self.difficulty.chart.notes:
            if not note.active or note.lane != lane:
                continue
            if not isinstance(note, (Tap, Hold)):
                continue
            diff = abs(note.time - t)
            if diff < best_diff:
                best_diff = diff
                best      = note
        if best is None:
            return
        result = self.judgement.judge(best, t)
        self._apply_result(best, result, t)
        if isinstance(best, Hold) and result != "MISS":
            best.startHold()
            self._holding[lane] = best

    def _on_key_up(self, key: int) -> None:
        lane = self._key_lane.get(key)
        if lane is None:
            return
        self._lane_pressed[lane] = False
        if lane not in self._holding:
            return
        hold = self._holding.pop(lane)
        hold.releaseHold()
        if self._current_time < hold.end_time - GOOD_WINDOW:
            self._apply_result(hold, "MISS", self._current_time)

    def _check_miss(self, t: float) -> None:
            for note in self.difficulty.chart.notes:
                if not getattr(note, 'active', True):
                    continue
                
                if isinstance(note, (Tap, Hold, Slide)) and t > note.time + MISS_WINDOW:
                    
                    if isinstance(note, Hold) and getattr(note, 'is_holding', False):
                        continue
                    if isinstance(note, Slide) and getattr(note, 'is_active_window', False):
                        continue
                    
                    note.miss()
                    if hasattr(self.judgement, 'resetCombo'):
                        self.judgement.resetCombo()
                    self._register_miss(note, t)

    def _tick_holds(self, t: float) -> None:
        from config import SCORE_PERFECT
        for hold in list(self._holding.values()):
            earned = hold.update_tick(t)
            if earned > 0:
                self._raw_score += earned
                self.combo       = self.judgement.combo

    def _check_holds(self, t: float) -> None:
        done = [lane for lane, hold in self._holding.items()
                if t >= hold.end_time]
        for lane in done:
            hold = self._holding.pop(lane)
            hold.hit()
            self.ui.screenText.showJudgement("PERFECT")
            

    def _check_slides(self, t: float) -> None:
        mx, _ = pygame.mouse.get_pos()
        for note in self.difficulty.chart.notes:
            if not isinstance(note, Slide) or not note.active:
                continue
            if note.time <= t <= note.end_time:
                note.is_active_window = True
            elif t > note.end_time and note.is_active_window:
                correct = note.checkSlide(mx, SCREEN_WIDTH)
                result  = self.judgement.judgeSlide(correct)
                self._apply_result(note, result, t)
                note.is_active_window = False

    def _apply_result(self, note: Note, result: str, t: float) -> None:
        from config import SCORE_PERFECT, SCORE_GOOD
        note_type = type(note).__name__.lower()

        raw = {"PERFECT": SCORE_PERFECT, "GOOD": SCORE_GOOD, "MISS": 0}.get(result, 0)
        self._raw_score += raw
        self.combo       = self.judgement.combo

        if result == "PERFECT": self._perfect += 1
        elif result == "GOOD":  self._good    += 1
        else:                   self._miss    += 1

        self.ui.healthBar.decrease(self.judgement.damageHealth(result))
        self.ui.healthBar.increase(self.judgement.healHealth(result))
        self.ui.screenText.showJudgement(result)

        if result == "MISS":
            note.miss()
        else:
            note.hit()

        self.logger.logHit(t, note.time, result, note_type)
        if result != "PERFECT":
            self.logger.logReaction(t, note.time, note_type)
        self.game.statistic.addJudgement(result)

        if self.ui.healthBar.is_dead:
            self.endGame()

    def _register_miss(self, note: Note, t: float) -> None:
        note_type = type(note).__name__.lower()
        self._miss += 1
        self.combo  = 0
        self.ui.healthBar.decrease(10)
        self.ui.screenText.showJudgement("MISS")
        self.logger.logHit(t, note.time, "MISS", note_type)
        self.logger.logReaction(t, note.time, note_type)
        self.game.statistic.addJudgement("MISS")
        if self.ui.healthBar.is_dead:
            self.endGame()
