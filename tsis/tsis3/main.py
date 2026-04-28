import pygame
import sys
from persistence import load_settings
from racer import GameScene
from scenes import MenuScene, SettingsScene, LeaderboardScene, GameOverScene, NameEntryScene

W, H = 560, 700
FPS  = 60


class Game:
    def __init__(self):
        pygame.init()
        self.screen   = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Racer")
        self.clock    = pygame.time.Clock()
        self.running  = True
        self.settings = load_settings()
        self.username = "Player"
        self.last_run = None

        self.scenes = {
            "menu":        MenuScene(self),
            "nameentry":   NameEntryScene(self),
            "game":        GameScene(self),
            "settings":    SettingsScene(self),
            "leaderboard": LeaderboardScene(self),
            "gameover":    GameOverScene(self),
        }
        self.current = None
        self.switch_scene("menu")

    def switch_scene(self, name):
        self.current = self.scenes[name]
        self.current.init()

    def run(self):
        while self.running:
            dt     = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False

            self.current.process_input(events)
            self.current.update(dt)
            self.current.render(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
