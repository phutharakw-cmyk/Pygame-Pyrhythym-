import pygame
import csv
import os

from config    import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, DATA_DIR
from settings  import Settings
from statistic import Statistic
from sound     import Sound


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.font.init()

        self.screen   = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock    = pygame.time.Clock()
        self.running  = True

        self.settings:  Settings  = Settings()
        self.statistic: Statistic = Statistic()
        self.sound:     Sound     = Sound()

        self.current_page = None
        self.startGame()

    def startGame(self) -> None:
        self.loadConfig()
        from pages.main_menu_page import Main_menu_page
        self.change_page(Main_menu_page(self))

    def change_page(self, page) -> None:
        self.current_page = page
        print(f"[Game] -> {type(page).__name__}")

    def loadConfig(self) -> None:
        pass

    def saveStatistic(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        path = os.path.join(DATA_DIR, "statistic.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["totalScore", "maxCombo", "playCount",
                        "perfectCount", "goodCount", "missCount"])
            w.writerow([
                self.statistic.totalScore,
                self.statistic.maxCombo,
                self.statistic.playCount,
                self.statistic.perfectCount,
                self.statistic.goodCount,
                self.statistic.missCount,
            ])
        print(f"[Game] Statistic saved -> {path}")

    def exitGame(self) -> None:
        self.saveStatistic()
        self.running = False

    def run(self) -> None:
        while self.running:
            dt     = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.exitGame()

            if self.current_page:
                self.current_page.handle_events(events)
                self.current_page.update(dt)
                self.current_page.draw(self.screen)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
