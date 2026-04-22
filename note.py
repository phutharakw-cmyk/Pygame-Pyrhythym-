import pygame
from config import (
    HIT_Y, NOTE_HEIGHT, LANE_WIDTH, SIDE_LANE_WIDTH,
    MISS_WINDOW,
    COLOR_NOTE_TAP, COLOR_NOTE_HOLD, COLOR_NOTE_SLIDE,
    SCREEN_WIDTH,
)

HOLD_TICK_INTERVAL = 0.1   
HOLD_TICK_SCORE    = 10    


def get_lane_x(lane: str, screen_width: int) -> int:
    total_center = LANE_WIDTH * 4
    start_x = (screen_width - total_center) // 2
    mapping = {
        "L": start_x - SIDE_LANE_WIDTH // 2,
        "1": start_x + LANE_WIDTH * 0 + LANE_WIDTH // 2,
        "2": start_x + LANE_WIDTH * 1 + LANE_WIDTH // 2,
        "3": start_x + LANE_WIDTH * 2 + LANE_WIDTH // 2,
        "4": start_x + LANE_WIDTH * 3 + LANE_WIDTH // 2,
        "R": start_x + total_center + SIDE_LANE_WIDTH // 2,
    }
    return mapping.get(lane, screen_width // 2)


class Note:
    def __init__(self, time: float, lane: str):
        self.time:      float = time
        self.lane:      str   = lane
        self.is_hit:    bool  = False
        self.is_missed: bool  = False

    @property
    def active(self) -> bool:
        return not self.is_hit and not self.is_missed

    def get_y(self, current_time: float, note_speed: float) -> float:
        return HIT_Y - (self.time - current_time) * note_speed

    def spawn(self) -> None: pass
    def hit(self)   -> None: self.is_hit    = True
    def miss(self)  -> None: self.is_missed = True

    def draw(self, screen: pygame.Surface, current_time: float,
             note_speed: float, screen_width: int) -> None:
        raise NotImplementedError


class Tap(Note):
    W = 80
    H = NOTE_HEIGHT

    def checkHit(self, input_time: float) -> bool:
        return abs(input_time - self.time) <= MISS_WINDOW

    def draw(self, screen, current_time, note_speed, screen_width):
        if not self.active:
            return
        x    = get_lane_x(self.lane, screen_width)
        y    = int(self.get_y(current_time, note_speed))
        if y > screen.get_height() + self.H:
            return
        rect = pygame.Rect(x - self.W // 2, y - self.H // 2, self.W, self.H)
        pygame.draw.rect(screen, COLOR_NOTE_TAP, rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)


class Hold(Note):
    W = 80
    H = NOTE_HEIGHT

    def __init__(self, time: float, lane: str, duration: float):
        super().__init__(time, lane)
        self.duration:         float = duration
        self.is_holding:       bool  = False
 
        self._last_tick_time:  float = 0.0 
        self._tick_score_total: int  = 0 

    @property
    def end_time(self) -> float:
        return self.time + self.duration

    def startHold(self) -> None:
        self.is_holding      = True
        self._last_tick_time = self.time  
    def releaseHold(self) -> None:
        self.is_holding = False

    def update_tick(self, current_time: float) -> int:
        """
        Call every frame while is_holding=True.
        Returns score earned this frame (multiples of HOLD_TICK_SCORE).
        Scoring is based on total ticks that should have fired by now,
        ensuring the correct count regardless of frame rate jitter.
        """
        if not self.is_holding:
            return 0
     
        elapsed        = min(current_time, self.end_time) - self.time
        total_due      = int(elapsed / HOLD_TICK_INTERVAL)
        already_given  = self._tick_score_total // HOLD_TICK_SCORE
        new_ticks      = max(0, total_due - already_given)
        if new_ticks == 0:
            return 0
        earned                 = new_ticks * HOLD_TICK_SCORE
        self._tick_score_total += earned
        return earned

    def draw(self, screen: pygame.Surface, current_time: float,
                note_speed: float, screen_width: int) -> None:
            if not self.active and not self.is_holding:
                return

            x = get_lane_x(self.lane, screen_width)

        
            head_y = int(self.get_y(current_time, note_speed))
            tail_y = int(HIT_Y - (self.end_time - current_time) * note_speed)

            if self.is_holding:
                tail_y = min(tail_y, HIT_Y)
                draw_head_y = min(head_y, HIT_Y)
            else:
                draw_head_y = head_y

            body_top    = tail_y
            body_bottom = draw_head_y
            body_h      = max(0, body_bottom - body_top)

            if body_h > 0:

                body_color = (
                    int(COLOR_NOTE_HOLD[0] * 0.7),
                    int(COLOR_NOTE_HOLD[1] * 0.7),
                    int(COLOR_NOTE_HOLD[2] * 0.7),
                )
                pygame.draw.rect(screen, body_color,
                                pygame.Rect(x - self.W // 2 + 12,
                                            body_top, self.W - 24, body_h),
                                border_radius=4)

       
            if not self.is_holding or head_y <= HIT_Y:
                hy = head_y if not self.is_holding else min(head_y, HIT_Y)
                
              
                if hy <= screen.get_height() + self.H:
                    hrect = pygame.Rect(x - self.W // 2, hy - self.H // 2, self.W, self.H)
                    pygame.draw.rect(screen, COLOR_NOTE_HOLD, hrect, border_radius=6)
                    pygame.draw.rect(screen, (255, 255, 255), hrect, 2, border_radius=6)

           
            if self.is_holding and self.duration > 0:
                elapsed  = max(0.0, current_time - self.time)
                progress = min(1.0, elapsed / self.duration)
                bar_h    = max(4, int(body_h * (1.0 - progress)))
                pygame.draw.rect(screen, (255, 255, 100),
                                pygame.Rect(x + self.W // 2 - 6,
                                            body_top, 4, bar_h),
                                border_radius=2)


class Slide(Note):
    W = 120
    H = NOTE_HEIGHT

    def __init__(self, time: float, lane: str, duration: float):
        super().__init__(time, lane)
        self.duration:         float = duration
        self.is_active_window: bool  = False

    @property
    def end_time(self) -> float:
        return self.time + self.duration

    def checkSlide(self, mouse_x: float, screen_width: float) -> bool:
        if self.lane == "L":
            return mouse_x < screen_width / 2
        return mouse_x >= screen_width / 2

    def draw(self, screen: pygame.Surface, current_time: float,
             note_speed: float, screen_width: int) -> None:
        if not self.active and not getattr(self, 'is_active_window', False):
            return
            
        x = get_lane_x(self.lane, screen_width)
        
    
        head_y = int(self.get_y(current_time, note_speed))
        tail_y = int(HIT_Y - (self.end_time - current_time) * note_speed)


        if getattr(self, 'is_active_window', False):
            draw_head_y = min(head_y, HIT_Y)
            draw_tail_y = min(tail_y, HIT_Y)
        else:
            draw_head_y = head_y
            draw_tail_y = tail_y

        body_top    = draw_tail_y
        body_bottom = draw_head_y
        body_h      = max(0, body_bottom - body_top)

   
        if body_h > 0:
            pygame.draw.rect(screen, COLOR_NOTE_SLIDE,
                             pygame.Rect(x - self.W // 2 + 10, body_top, self.W - 20, body_h),
                             border_radius=4)
                             
     
        if not getattr(self, 'is_active_window', False) or head_y <= HIT_Y:
            hy = head_y if not getattr(self, 'is_active_window', False) else min(head_y, HIT_Y)
            
    
            if hy <= screen.get_height() + self.H:
                hrect = pygame.Rect(x - self.W // 2, hy - self.H // 2, self.W, self.H)
                pygame.draw.rect(screen, COLOR_NOTE_SLIDE, hrect, border_radius=6)
                pygame.draw.rect(screen, (255, 255, 255), hrect, 2, border_radius=6)
