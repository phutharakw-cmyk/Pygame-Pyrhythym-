import pygame
from score_record import Record
from config import SCREEN_WIDTH, SCREEN_HEIGHT

C_BG_OVERLAY = (0, 0, 0, 160)
C_PANEL      = (20, 20, 38)
C_BORDER     = (80, 80, 140)
C_TEXT       = (220, 220, 240)
C_DIM        = (120, 120, 150)
C_ACCENT     = (100, 200, 255)
C_PERFECT    = (255, 240, 100)
C_GOOD       = (100, 220, 255)
C_MISS       = (255,  80,  80)
C_GOLD       = (255, 210,  50)
C_GREEN      = (100, 240, 140)
C_NEW        = (255, 160,  60)

PANEL_W = 560
PANEL_H = 500
PANEL_X = (SCREEN_WIDTH  - PANEL_W) // 2
PANEL_Y = (SCREEN_HEIGHT - PANEL_H) // 2


class ResultPopup:
    def __init__(self, song_title: str, diff_label: str,
                 score: int, max_score: int,
                 max_combo: int, total_notes: int,
                 perfect: int, good: int, miss: int,
                 record: Record,
                 is_new_best: bool, is_new_combo: bool):

        self.song_title  = song_title
        self.diff_label  = diff_label
        self.score       = score
        self.max_score   = max_score
        self.max_combo   = max_combo
        self.total_notes = total_notes
        self.perfect     = perfect
        self.good        = good
        self.miss        = miss
        self.record      = record
        self.is_new_best  = is_new_best
        self.is_new_combo = is_new_combo

        denom = perfect + good + miss
        self.accuracy = (perfect + good * 0.5) / denom * 100 if denom > 0 else 0.0

        pygame.font.init()
        self.font_title  = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_lg     = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_med    = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_sm     = pygame.font.SysFont("consolas", 14)
        self.font_hint   = pygame.font.SysFont("consolas", 13)

        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill(C_BG_OVERLAY)

    def handle_events(self, events: list) -> bool:
        """คืน True เมื่อผู้เล่นกด Enter / Space / ESC หรือคลิก"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if not (PANEL_X <= mx <= PANEL_X + PANEL_W and
                        PANEL_Y <= my <= PANEL_Y + PANEL_H):
                    return True
                btn = self._continue_rect()
                if btn.collidepoint(mx, my):
                    return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._overlay, (0, 0))

        pygame.draw.rect(screen, C_PANEL,
                         (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), border_radius=12)
        pygame.draw.rect(screen, C_BORDER,
                         (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), 2, border_radius=12)

        y = PANEL_Y + 24

        self._center(screen, "RESULTS", y, self.font_title, C_ACCENT)
        y += 32
        self._center(screen, f"{self.song_title}  [{self.diff_label}]",
                     y, self.font_sm, C_DIM)
        y += 28

        score_color = C_GOLD if self.is_new_best else C_TEXT
        self._center(screen, f"{self.score:,}", y, self.font_lg, score_color)
        if self.is_new_best:
            self._center(screen, "NEW BEST!", y + 44, self.font_sm, C_NEW)
        y += 60

        pct = self.score / self.max_score * 100 if self.max_score > 0 else 0
        self._center(screen, f"{pct:.1f}%  of max {self.max_score:,}",
                     y, self.font_sm, C_DIM)
        y += 28

        pygame.draw.line(screen, C_BORDER,
                         (PANEL_X + 30, y), (PANEL_X + PANEL_W - 30, y))
        y += 14

        col1 = PANEL_X + 60
        col2 = PANEL_X + PANEL_W // 2 + 20
        row_h = 40

        self._stat_row(screen, "PERFECT",  str(self.perfect),  col1, y, C_PERFECT)
        self._stat_row(screen, "MAX COMBO", str(self.max_combo),col2, y,
                       C_GOLD if self.is_new_combo else C_TEXT)
        y += row_h
        self._stat_row(screen, "GOOD",  str(self.good),  col1, y, C_GOOD)
        self._stat_row(screen, "ACCURACY", f"{self.accuracy:.1f}%", col2, y, C_TEXT)
        y += row_h
        self._stat_row(screen, "MISS",  str(self.miss),  col1, y, C_MISS)
        self._stat_row(screen, "NOTES",  str(self.total_notes), col2, y, C_DIM)
        y += row_h + 8

        bx = PANEL_X + 40
        if self.record.all_perfect:
            bx = self._badge(screen, bx, y, "ALL PERFECT", C_GOLD)
        if self.record.full_combo:
            bx = self._badge(screen, bx, y, "FULL COMBO", C_GREEN)
        if self.is_new_best:
            bx = self._badge(screen, bx, y, "NEW BEST", C_NEW)
        y += 36

        pygame.draw.line(screen, C_BORDER,
                         (PANEL_X + 30, y), (PANEL_X + PANEL_W - 30, y))
        y += 10
        self._center(screen, f"Best  {self.record.best_score:,}   "
                              f"Best Combo  {self.record.best_combo}   "
                              f"Plays  {self.record.play_count}",
                     y, self.font_sm, C_DIM)
        y += 24

        btn = self._continue_rect()
        pygame.draw.rect(screen, C_BORDER, btn, border_radius=8)
        self._center(screen, "Continue  [ Enter ]", btn.centery - 10,
                     self.font_med, C_ACCENT)

        self._center(screen, "Press Enter / Space / ESC or click to continue",
                     PANEL_Y + PANEL_H - 22, self.font_hint, C_DIM)

    def _continue_rect(self) -> pygame.Rect:
        w, h = 240, 44
        return pygame.Rect(PANEL_X + (PANEL_W - w) // 2,
                           PANEL_Y + PANEL_H - 70, w, h)

    def _center(self, screen, text, y, font, color) -> None:
        surf = font.render(str(text), True, color)
        screen.blit(surf, (PANEL_X + (PANEL_W - surf.get_width()) // 2, y))

    def _stat_row(self, screen, label, value, x, y, val_color) -> None:
        lbl  = self.font_sm.render(label,  True, C_DIM)
        val  = self.font_med.render(value, True, val_color)
        screen.blit(lbl, (x, y))
        screen.blit(val, (x, y + 16))

    def _badge(self, screen, x, y, text, color) -> int:
        surf = self.font_sm.render(text, True, color)
        w    = surf.get_width() + 16
        pygame.draw.rect(screen, color, (x, y, w, 24), 1, border_radius=4)
        screen.blit(surf, (x + 8, y + 4))
        return x + w + 8
