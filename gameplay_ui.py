import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_TEXT, COLOR_PERFECT, COLOR_GOOD, COLOR_MISS,
    COLOR_LANE_CENTER, COLOR_LANE_SIDE, COLOR_HIT_LINE,
    HIT_Y, LANE_WIDTH, SIDE_LANE_WIDTH,
    MAX_HEALTH,
)

class ScreenText:
    def __init__(self):
        self.combo:     int   = 0
        self.score:     int   = 0
        self.positionX: float = SCREEN_WIDTH / 2
        self.positionY: float = SCREEN_HEIGHT / 2 - 60

        self.font_score = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_combo = pygame.font.SysFont("consolas", 48, bold=True)
        self.font_judge = pygame.font.SysFont("consolas", 36, bold=True)

        self._judge_text:  str   = ""
        self._judge_color: tuple = COLOR_TEXT
        self._judge_timer: float = 0.0

    def updateCombo(self, c: int) -> None:
        self.combo = c

    def updateScore(self, s: int) -> None:
        self.score = s

    def showJudgement(self, result: str) -> None:
        self._judge_text  = result
        self._judge_color = {
            "PERFECT": COLOR_PERFECT,
            "GOOD":    COLOR_GOOD,
            "MISS":    COLOR_MISS,
        }.get(result, COLOR_TEXT)
        self._judge_timer = 0.6

    def update(self, dt: float) -> None:
        if self._judge_timer > 0:
            self._judge_timer = max(0.0, self._judge_timer - dt)

    def draw(self, screen: pygame.Surface) -> None:
        surf = self.font_score.render(f"SCORE  {self.score:,}", True, COLOR_TEXT)
        screen.blit(surf, (20, 20))

        if self.combo >= 2:
            surf = self.font_combo.render(f"{self.combo}x", True, COLOR_TEXT)
            screen.blit(surf, (int(self.positionX) - surf.get_width() // 2,
                               int(self.positionY)))

        if self._judge_timer > 0:
            surf = self.font_judge.render(self._judge_text, True, self._judge_color)
            surf.set_alpha(int(255 * (self._judge_timer / 0.6)))
            screen.blit(surf, (int(self.positionX) - surf.get_width() // 2,
                               int(self.positionY) + 60))

    def reset(self) -> None:
        self.combo = 0
        self.score = 0
        self._judge_text  = ""
        self._judge_timer = 0.0


class HealthBar:
    BAR_W = 300
    BAR_H = 20
    X     = SCREEN_WIDTH - 330
    Y     = 20

    def __init__(self):
        self.health:    float = MAX_HEALTH
        self.maxHealth: float = MAX_HEALTH

    def increase(self, v: float) -> None:
        self.health = min(self.maxHealth, self.health + v)

    def decrease(self, v: float) -> None:
        self.health = max(0.0, self.health - v)

    @property
    def is_dead(self) -> bool:
        return self.health <= 0.0

    @property
    def ratio(self) -> float:
        return self.health / self.maxHealth if self.maxHealth > 0 else 0.0

    def updateBar(self) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (40, 40, 60),
                         (self.X, self.Y, self.BAR_W, self.BAR_H),
                         border_radius=8)
        fill_w = int(self.BAR_W * self.ratio)
        if fill_w > 0:
            color = (int(255 * (1 - self.ratio)), int(200 * self.ratio), 60)
            pygame.draw.rect(screen, color,
                             (self.X, self.Y, fill_w, self.BAR_H),
                             border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200),
                         (self.X, self.Y, self.BAR_W, self.BAR_H),
                         2, border_radius=8)
        font = pygame.font.SysFont("consolas", 14)
        surf = font.render(f"HP  {int(self.health)}/{int(self.maxHealth)}", True, (220, 220, 220))
        screen.blit(surf, (self.X, self.Y + self.BAR_H + 4))


class Gameplay_UI:
    def __init__(self):
        self.screenText: ScreenText = ScreenText()
        self.healthBar:  HealthBar  = HealthBar()

    def update(self, dt: float) -> None:
        self.screenText.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        self._draw_lanes(screen)
        self.screenText.draw(screen)
        self.healthBar.draw(screen)

    def _draw_lanes(self, screen: pygame.Surface) -> None:
        total_center = LANE_WIDTH * 4
        start_x      = (SCREEN_WIDTH - total_center) // 2
        lx           = start_x - SIDE_LANE_WIDTH
        rx           = start_x + total_center

       
        pygame.draw.rect(screen, COLOR_LANE_SIDE,
                         (lx, 0, SIDE_LANE_WIDTH, SCREEN_HEIGHT))
        
        for i in range(4):
            col = COLOR_LANE_CENTER if i % 2 == 0 \
                else tuple(max(0, c - 8) for c in COLOR_LANE_CENTER)
            pygame.draw.rect(screen, col,
                             (start_x + i * LANE_WIDTH, 0, LANE_WIDTH, SCREEN_HEIGHT))
            pygame.draw.line(screen, (50, 50, 80),
                             (start_x + i * LANE_WIDTH, 0),
                             (start_x + i * LANE_WIDTH, SCREEN_HEIGHT))
     
        pygame.draw.rect(screen, COLOR_LANE_SIDE,
                         (rx, 0, SIDE_LANE_WIDTH, SCREEN_HEIGHT))
       
        pygame.draw.line(screen, COLOR_HIT_LINE,
                         (lx, HIT_Y), (rx + SIDE_LANE_WIDTH, HIT_Y), 3)
       
        glow = pygame.Surface((rx + SIDE_LANE_WIDTH - lx, 8), pygame.SRCALPHA)
        glow.fill((200, 200, 200, 40))
        screen.blit(glow, (lx, HIT_Y - 4))
