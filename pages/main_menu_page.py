import pygame
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game

C_BG         = (15, 15, 25)
C_PANEL      = (25, 25, 45)
C_TEXT       = (220, 220, 240)
C_DIM        = (120, 120, 160)
C_ACCENT     = (100, 200, 255)
C_BUTTON     = (45, 85, 155)
C_BUTTON_HOVER = (70, 120, 200)
C_BORDER     = (80, 80, 140)
C_GOLD       = (255, 210, 50)


class Main_menu_page:

    BUTTON_W = 280
    BUTTON_H = 60
    BUTTON_GAP = 20

    def __init__(self, game: "Game"):
        self.game = game
        self.hovered_button = -1
        self._howto_popup = None

        # Fonts
        self.font_title = pygame.font.SysFont("consolas", 56, bold=True)
        self.font_button = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_subtitle = pygame.font.SysFont("consolas", 18)

    def handle_events(self, events: list) -> None:
        if self._howto_popup:
            if self._howto_popup.handle_events(events):
                self._howto_popup = None
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.exitGame()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.hovered_button == 0:
                        self._start_game()
                    elif self.hovered_button == 1:
                        self._open_howto()
                elif event.key == pygame.K_DOWN:
                    self.hovered_button = 1
                elif event.key == pygame.K_UP:
                    self.hovered_button = 0

            elif event.type == pygame.MOUSEMOTION:
                self.hovered_button = self._get_hovered_button(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn = self._get_hovered_button(event.pos)
                if btn == 0:
                    self._start_game()
                elif btn == 1:
                    self._open_howto()

    def update(self, dt: float) -> None:
        if self._howto_popup:
            self._howto_popup.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(C_BG)

        w, h = screen.get_width(), screen.get_height()

        title_surf = self.font_title.render("PYRHYTHYM", True, C_ACCENT)
        screen.blit(title_surf, (
            (w - title_surf.get_width()) // 2,
            h // 2 - 140
        ))

        subtitle_surf = self.font_subtitle.render(
            "Rhythm Game", True, C_DIM
        )
        screen.blit(subtitle_surf, (
            (w - subtitle_surf.get_width()) // 2,
            h // 2 - 70
        ))

        self._draw_button(screen, "START GAME", 0, h // 2)
        self._draw_button(screen, "HOW TO PLAY", 1, h // 2 + self.BUTTON_H + self.BUTTON_GAP)

        hint_surf = self.font_subtitle.render(
            "↑↓ Navigate  | Enter to Select  | ESC to Exit",
            True, C_DIM
        )
        screen.blit(hint_surf, (
            (w - hint_surf.get_width()) // 2,
            h - 60
        ))

        if self._howto_popup:
            self._howto_popup.draw(screen)

    def _draw_button(self, screen: pygame.Surface, text: str, btn_idx: int, y: int) -> None:
        w = screen.get_width()
        x = (w - self.BUTTON_W) // 2

        is_hovered = (btn_idx == self.hovered_button)
        color = C_BUTTON_HOVER if is_hovered else C_BUTTON
        border_color = C_GOLD if is_hovered else C_BORDER

        rect = pygame.Rect(x, y, self.BUTTON_W, self.BUTTON_H)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=10)

        text_surf = self.font_button.render(text, True, C_TEXT)
        screen.blit(text_surf, (
            rect.centerx - text_surf.get_width() // 2,
            rect.centery - text_surf.get_height() // 2
        ))

    def _get_hovered_button(self, pos: tuple) -> int:
        """Return hovered button index (-1 if none)"""
        mx, my = pos
        w = pygame.display.get_surface().get_width()
        h = pygame.display.get_surface().get_height()
        x = (w - self.BUTTON_W) // 2

        start_y = h // 2

        howto_y = h // 2 + self.BUTTON_H + self.BUTTON_GAP

        if x <= mx <= x + self.BUTTON_W:
            if start_y <= my <= start_y + self.BUTTON_H:
                return 0
            if howto_y <= my <= howto_y + self.BUTTON_H:
                return 1

        return -1

    def _start_game(self) -> None:
        """Go to song selection"""
        self.game.sound.playClick()
        from pages.select_song_page import Select_song_page
        self.game.change_page(Select_song_page(self.game))

    def _open_howto(self) -> None:
        """Open How to Play popup"""
        self.game.sound.playClick()
        self._howto_popup = HowtoPlayPopup(self.game)


class HowtoPlayPopup:
    """Tutorial Popup - How to Play"""

    POPUP_W = 700
    POPUP_H = 600

    def __init__(self, game: "Game"):
        self.game = game
        self.scroll = 0.0
        self.max_scroll = 100.0

        self.font_title = pygame.font.SysFont("consolas", 32, bold=True)
        self.font_head = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_body = pygame.font.SysFont("consolas", 14)

        self._overlay = pygame.Surface((pygame.display.get_surface().get_width(),
                                        pygame.display.get_surface().get_height()),
                                       pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 140))

    def handle_events(self, events: list) -> bool:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return True
                elif event.key == pygame.K_UP:
                    self.scroll = max(0.0, self.scroll - 20.0)
                elif event.key == pygame.K_DOWN:
                    self.scroll = min(self.max_scroll, self.scroll + 20.0)

            elif event.type == pygame.MOUSEWHEEL:
                self.scroll = max(0.0, min(self.max_scroll, self.scroll - event.y * 10))

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                sx = (pygame.display.get_surface().get_width() - self.POPUP_W) // 2
                sy = (pygame.display.get_surface().get_height() - self.POPUP_H) // 2
                if not (sx <= mx <= sx + self.POPUP_W and sy <= my <= sy + self.POPUP_H):
                    return True

        return False

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._overlay, (0, 0))

        w, h = screen.get_width(), screen.get_height()
        px = (w - self.POPUP_W) // 2
        py = (h - self.POPUP_H) // 2

        pygame.draw.rect(screen, (20, 20, 38),
                         (px, py, self.POPUP_W, self.POPUP_H), border_radius=12)
        pygame.draw.rect(screen, (80, 80, 140),
                         (px, py, self.POPUP_W, self.POPUP_H), 2, border_radius=12)

        content_rect = pygame.Rect(px + 20, py + 50, self.POPUP_W - 40, self.POPUP_H - 100)
        content_y = content_rect.top - self.scroll

        title_surf = self.font_title.render("HOW TO PLAY", True, (100, 200, 255))
        screen.blit(title_surf, (px + (self.POPUP_W - title_surf.get_width()) // 2, py + 16))

        sections = [
            ("GAME OBJECTIVE", "Tap notes to the beat and get the highest score!"),
            ("TAP", "Press D, F, J, K keys when notes reach the hit line."),
            ("HOLD", "Press and hold the key until the note ends."),
            ("SLIDE", "Move your mouse left/right of the screen to get the score."),
            ("JUDGEMENT", "PERFECT (±50ms) = +300pts | GOOD (±100ms) = +100pts | MISS = 0pts"),
            ("COMBO", "Get consecutive hits to increase combo multiplier!"),
            ("HEALTH", "Take damage from misses. Gain healing from perfect hits."),
            ("DIFFICULTY", "Navigate with ↑↓, switch difficulty with ←→, Press Enter to play."),
            ("SETTINGS", "Adjust volume and note speed in the song selection menu."),
        ]

        for section_title, section_text in sections:
            title = self.font_head.render(section_title, True, (255, 210, 50))
            screen.blit(title, (content_rect.left, content_y))
            content_y += 26

            words = section_text.split()
            line = ""
            for word in words:
                test_line = line + (" " if line else "") + word
                if self.font_body.size(test_line)[0] > content_rect.width - 20:
                    if line:
                        text_surf = self.font_body.render(line, True, (220, 220, 240))
                        screen.blit(text_surf, (content_rect.left + 10, content_y))
                        content_y += 20
                    line = word
                else:
                    line = test_line

            if line:
                text_surf = self.font_body.render(line, True, (220, 220, 240))
                screen.blit(text_surf, (content_rect.left + 10, content_y))
                content_y += 20

            content_y += 8

        self.max_scroll = max(0.0, content_y - content_rect.top - content_rect.height)

        hint = self.font_body.render("Press ESC / Enter or click outside to close",
                                      True, (120, 120, 160))
        screen.blit(hint, (px + (self.POPUP_W - hint.get_width()) // 2,
                           py + self.POPUP_H - 24))
