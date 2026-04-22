# pages/select_song_page.py — Song Selection Page (English)

import pygame
from typing import List, Optional, TYPE_CHECKING
from song         import Song, Difficulty, scan_songs
from score_record import load_record, Record
from config import SONGS_DIR, SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from game import Game

# ── Layout ────────────────────────────────────────────────
HEADER_H  = 110
FOOTER_H  = 50
LIST_X    = 60
LIST_W    = 700
ITEM_H    = 80
PREVIEW_X = 820   # x position of preview panel
PREVIEW_W = SCREEN_WIDTH - PREVIEW_X - 20
COVER_SZ  = 220   # cover image size

# ── Colors ────────────────────────────────────────────────
C_BG      = (14,  14,  22)
C_PANEL   = (22,  22,  36)
C_ITEM    = (28,  28,  50)
C_HOVER   = (45,  45,  80)
C_SELECT  = (55,  85, 155)
C_BORDER  = (50,  50,  90)
C_TEXT    = (210, 210, 230)
C_DIM     = (110, 110, 140)
C_ACCENT  = (100, 200, 255)
C_WARN    = (255, 180,  60)
C_BASIC   = (100, 200, 140)
C_HARD    = (255, 100,  80)
C_DEFAULT = (160, 160, 255)

DIFF_COLORS = {"Basic": C_BASIC, "Hard": C_HARD}


class Select_song_page:
    def __init__(self, game: "Game"):
        self.game = game
        self.songList:      List[Song]           = []
        self.selectedSong:  Optional[Song]       = None
        self.selectedDiff:  Optional[Difficulty] = None
        self._hovered:  int = -1
        self._selected: int = -1
        self._diff_idx: int = 0   # selected difficulty index
        self._scroll:   int = 0

        self.font_title = pygame.font.SysFont("consolas", 26, bold=True)
        self.font_med   = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_sm    = pygame.font.SysFont("consolas", 13)
        self.font_lg    = pygame.font.SysFont("consolas", 20, bold=True)

        self._record_cache: dict = {}   # key=(title,diff) → Record
        self.displaySongList()

    # ── Public API ────────────────────────────────────────
    def displaySongList(self) -> None:
        self.songList     = scan_songs(SONGS_DIR)
        self._selected    = -1
        self._hovered     = -1
        self._scroll      = 0
        self._diff_idx    = 0
        self.selectedSong = None
        self.selectedDiff = None

    def selectSong(self, song: Song) -> None:
        self.selectedSong = song
        self._diff_idx    = 0
        self.selectedDiff = song.difficulties[0] if song.difficulties else None
        self._load_records(song)

    def _load_records(self, song: Song) -> None:
        """Load records for all difficulties of this song"""
        self._record_cache.clear()
        for diff in song.difficulties:
            key = (song.title, diff.label)
            self._record_cache[key] = load_record(
                song.folder_path, song.title, diff.label)

    def _get_record(self) -> "Record | None":
        if not self.selectedSong or not self.selectedDiff:
            return None
        key = (self.selectedSong.title, self.selectedDiff.label)
        return self._record_cache.get(key)

    def confirmSong(self) -> None:
        if not self.selectedSong or not self.selectedDiff:
            return
        from pages.gameplay_page import Gameplay_page
        self.game.change_page(
            Gameplay_page(self.game, self.selectedSong, self.selectedDiff)
        )

    def _back_to_menu(self) -> None:
        """Go back to main menu"""
        self.game.sound.playClick()
        from pages.main_menu_page import Main_menu_page
        self.game.change_page(Main_menu_page(self.game))

    # ── Page interface ────────────────────────────────────
    def handle_events(self, events: list) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._back_to_menu()
                elif event.key == pygame.K_RETURN and self._selected >= 0:
                    self.confirmSong()
                elif event.key == pygame.K_DOWN:
                    self._selected = min(len(self.songList) - 1, self._selected + 1)
                    if self._selected >= 0:
                        self.selectSong(self.songList[self._selected])
                    self._clamp_scroll()
                elif event.key == pygame.K_UP:
                    self._selected = max(0, self._selected - 1)
                    if self._selected >= 0:
                        self.selectSong(self.songList[self._selected])
                    self._clamp_scroll()
                elif event.key == pygame.K_LEFT:
                    self._cycle_diff(-1)
                elif event.key == pygame.K_RIGHT:
                    self._cycle_diff(1)
                elif event.key == pygame.K_r:
                    self.displaySongList()
                elif event.key == pygame.K_a:
                    print("[System] Opening Data Analysis...")
                    try:
                        from data_analysis import open_analysis_window
                        open_analysis_window() 
                    except Exception as e:
                        print(f"Error opening data analysis: {e}")

            if event.type == pygame.MOUSEWHEEL:
                self._scroll = max(0, min(
                    max(0, len(self.songList) - 1),
                    self._scroll - event.y
                ))

            if event.type == pygame.MOUSEMOTION:
                self._hovered = self._item_at(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check difficulty badge click
                if self.selectedSong:
                    consumed = self._click_diff_badge(event.pos)
                    if consumed:
                        continue
                idx = self._item_at(event.pos)
                if idx >= 0:
                    if idx == self._selected:
                        self.confirmSong()
                    else:
                        self._selected = idx
                        self.selectSong(self.songList[idx])

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(C_BG)
        self._draw_header(screen)
        self._draw_list(screen)
        self._draw_preview(screen)
        self._draw_footer(screen)

    # ── Drawing ───────────────────────────────────────────
    def _draw_header(self, screen: pygame.Surface) -> None:
        W = screen.get_width()
        pygame.draw.rect(screen, C_PANEL, (0, 0, W, HEADER_H))
        pygame.draw.line(screen, C_BORDER, (0, HEADER_H), (W, HEADER_H))
        self._text(screen, "Pyrhythym", 40, 18, self.font_title, C_ACCENT)
        self._text(screen, "UP/DOWN: Select Song   LEFT/RIGHT: Change Difficulty   Enter: Play   R: Rescan   ESC: Back   A: Analytics",
                   40, 55, self.font_sm, C_DIM)
        self._text(screen, f"Found {len(self.songList)} songs in {SONGS_DIR}/",
                   40, 80, self.font_sm, C_DIM)

    def _draw_list(self, screen: pygame.Surface) -> None:
        H       = screen.get_height()
        LIST_Y  = HEADER_H + 10
        visible = (H - LIST_Y - FOOTER_H - 10) // ITEM_H
        if not self.songList:
            self._text(screen,
                       f"No songs found — Place songs in {SONGS_DIR}/songname/songname.mp3",
                       LIST_X, LIST_Y + 20, self.font_med, C_WARN)
            return
        for i in range(visible):
            idx = self._scroll + i
            if idx >= len(self.songList):
                break
            self._draw_item(screen, idx, LIST_Y + i * ITEM_H)

    def _draw_item(self, screen: pygame.Surface, idx: int, y: int) -> None:
        song = self.songList[idx]
        x, w = LIST_X, LIST_W
        col  = C_SELECT if idx == self._selected else (C_HOVER if idx == self._hovered else C_ITEM)
        rect = pygame.Rect(x, y + 2, w, ITEM_H - 4)
        pygame.draw.rect(screen, col, rect, border_radius=8)
        pygame.draw.rect(screen, C_BORDER, rect, 1, border_radius=8)

        self._text(screen, song.title, x + 16, y + 10, self.font_med, C_TEXT)

        # Difficulty badges
        bx = x + 16
        for diff in song.difficulties:
            c    = DIFF_COLORS.get(diff.label, C_DEFAULT)
            surf = self.font_sm.render(diff.label, True, c)
            sw   = surf.get_width()
            pygame.draw.rect(screen, c, (bx - 4, y + 34, sw + 8, 18), 1, border_radius=3)
            screen.blit(surf, (bx, y + 36))
            bx += sw + 16

        if not song.difficulties:
            self._text(screen, "NO CHART", x + 16, y + 36, self.font_sm, C_WARN)

        # BPM info on right
        if song.difficulties:
            info = f"BPM {song.bpm:.0f}"
            self._text(screen, info, x + w - 120, y + 36, self.font_sm, C_DIM)

    def _draw_preview(self, screen: pygame.Surface) -> None:
        """Right panel — cover + info + difficulty selector"""
        if not self.selectedSong:
            return
        song  = self.selectedSong
        px    = PREVIEW_X
        py    = HEADER_H + 10
        pw    = PREVIEW_W
        ph    = screen.get_height() - py - FOOTER_H - 10

        # Panel background
        pygame.draw.rect(screen, C_PANEL, (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(screen, C_BORDER, (px, py, pw, ph), 1, border_radius=10)

        cy = py + 16

        # ── Cover Image ──
        cover = song.get_cover((COVER_SZ, COVER_SZ))
        if cover:
            cx = px + (pw - COVER_SZ) // 2
            screen.blit(cover, (cx, cy))
            pygame.draw.rect(screen, C_BORDER, (cx, cy, COVER_SZ, COVER_SZ), 1)
        else:
            # Placeholder
            ph_rect = pygame.Rect(px + (pw - COVER_SZ) // 2, cy, COVER_SZ, COVER_SZ)
            pygame.draw.rect(screen, (30, 30, 50), ph_rect, border_radius=6)
            pygame.draw.rect(screen, C_BORDER, ph_rect, 1, border_radius=6)
            no_img = self.font_sm.render("No Cover", True, C_DIM)
            screen.blit(no_img, (ph_rect.centerx - no_img.get_width() // 2,
                                  ph_rect.centery - no_img.get_height() // 2))
        cy += COVER_SZ + 14

        # ── Song Title ──
        title_surf = self.font_lg.render(song.title, True, C_TEXT)
        if title_surf.get_width() > pw - 20:
            title_surf = pygame.transform.scale(
                title_surf, (pw - 20, title_surf.get_height()))
        screen.blit(title_surf, (px + (pw - title_surf.get_width()) // 2, cy))
        cy += 28

        # ── BPM ──
        bpm_surf = self.font_sm.render(f"BPM  {song.bpm:.0f}", True, C_DIM)
        screen.blit(bpm_surf, (px + (pw - bpm_surf.get_width()) // 2, cy))
        cy += 26

        # ── Difficulty Selector ──
        if not song.difficulties:
            return

        pygame.draw.line(screen, C_BORDER, (px + 10, cy), (px + pw - 10, cy))
        cy += 10

        diff_label = self.font_sm.render("DIFFICULTY", True, C_DIM)
        screen.blit(diff_label, (px + (pw - diff_label.get_width()) // 2, cy))
        cy += 20

        # Draw difficulty badges
        self._diff_badge_rects = []
        total_w = sum(70 for _ in song.difficulties) + (len(song.difficulties) - 1) * 8
        bx = px + (pw - total_w) // 2
        for i, diff in enumerate(song.difficulties):
            color = DIFF_COLORS.get(diff.label, C_DEFAULT)
            rect  = pygame.Rect(bx, cy, 70, 28)
            self._diff_badge_rects.append((rect, i))
            if i == self._diff_idx:
                pygame.draw.rect(screen, color, rect, border_radius=6)
                surf = self.font_sm.render(diff.label, True, (0, 0, 0))
            else:
                pygame.draw.rect(screen, C_ITEM, rect, border_radius=6)
                pygame.draw.rect(screen, color, rect, 1, border_radius=6)
                surf = self.font_sm.render(diff.label, True, color)
            screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                                rect.centery - surf.get_height() // 2))
            bx += 78
        cy += 38

        # ── Difficulty Info ──
        if self.selectedDiff:
            d     = self.selectedDiff
            notes = self.font_sm.render(f"Notes  {d.note_count}", True, C_TEXT)
            screen.blit(notes, (px + (pw - notes.get_width()) // 2, cy))
            cy += 22

        # ── Best Record ──
        rec = self._get_record()
        if rec and rec.play_count > 0:
            pygame.draw.line(screen, C_BORDER, (px+10, cy), (px+pw-10, cy))
            cy += 8
            # Best score
            bs = self.font_med.render(f"Best  {rec.best_score:,}", True, C_ACCENT)
            screen.blit(bs, (px + (pw - bs.get_width()) // 2, cy))
            cy += 22
            # Best combo + plays
            sub = self.font_sm.render(
                f"Combo  {rec.best_combo}    Plays  {rec.play_count}", True, C_DIM)
            screen.blit(sub, (px + (pw - sub.get_width()) // 2, cy))
            cy += 20
            # Badges
            bx2 = px + 20
            if rec.all_perfect:
                bx2 = self.__badge(screen, bx2, cy, "ALL PERFECT", (255, 210, 50))
            if rec.full_combo:
                bx2 = self.__badge(screen, bx2, cy, "FULL COMBO", (100, 240, 140))
            cy += 28
        elif rec:
            ns = self.font_sm.render("No record yet", True, C_DIM)
            screen.blit(ns, (px + (pw - ns.get_width()) // 2, cy))
            cy += 22

        # ── Hint ──
        hint = self.font_sm.render("Enter to play", True, C_DIM)
        screen.blit(hint, (px + (pw - hint.get_width()) // 2, cy + 4))

    def _draw_footer(self, screen: pygame.Surface) -> None:
        H  = screen.get_height()
        fy = H - FOOTER_H
        pygame.draw.line(screen, C_BORDER, (0, fy), (screen.get_width(), fy))
        if self.selectedSong and self.selectedDiff:
            msg = (f"Selected: {self.selectedSong.title}  "
                   f"[{self.selectedDiff.label}]  "
                   f"Notes: {self.selectedDiff.note_count}")
            self._text(screen, msg, 40, fy + 14, self.font_sm, C_TEXT)

    # ── Helpers ───────────────────────────────────────────
    def _cycle_diff(self, direction: int) -> None:
        if not self.selectedSong or not self.selectedSong.difficulties:
            return
        n = len(self.selectedSong.difficulties)
        self._diff_idx    = (self._diff_idx + direction) % n
        self.selectedDiff = self.selectedSong.difficulties[self._diff_idx]

    def _click_diff_badge(self, pos) -> bool:
        """Click difficulty badge in preview — return True if consumed"""
        if not hasattr(self, '_diff_badge_rects'):
            return False
        for rect, idx in self._diff_badge_rects:
            if rect.collidepoint(pos):
                self._diff_idx    = idx
                self.selectedDiff = self.selectedSong.difficulties[idx]
                return True
        return False

    def _item_at(self, pos) -> int:
        mx, my = pos
        if not (LIST_X <= mx <= LIST_X + LIST_W):
            return -1
        H       = pygame.display.get_surface().get_height()
        LIST_Y  = HEADER_H + 10
        visible = (H - LIST_Y - FOOTER_H - 10) // ITEM_H
        for i in range(visible):
            idx = self._scroll + i
            if idx >= len(self.songList):
                break
            iy = LIST_Y + i * ITEM_H
            if iy <= my <= iy + ITEM_H:
                return idx
        return -1

    def _clamp_scroll(self) -> None:
        H       = pygame.display.get_surface().get_height()
        LIST_Y  = HEADER_H + 10
        visible = (H - LIST_Y - FOOTER_H - 10) // ITEM_H
        if self._selected >= self._scroll + visible:
            self._scroll = self._selected - visible + 1
        elif self._selected < self._scroll:
            self._scroll = self._selected

    def _text(self, screen, text, x, y, font, color) -> None:
        screen.blit(font.render(str(text), True, color), (x, y))

    def __badge(self, screen, x, y, text, color) -> int:
        surf = self.font_sm.render(text, True, color)
        w    = surf.get_width() + 16
        pygame.draw.rect(screen, color, (x, y, w, 24), 1, border_radius=4)
        screen.blit(surf, (x + 8, y + 4))
        return x + w + 8
