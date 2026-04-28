import pygame
from scene import Scene
from ui import Button, draw_text
from persistence import load_leaderboard, load_settings, save_settings

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (100, 100, 100)
DARK   = (20,  20,  20)
YELLOW = (230, 200, 0)
GREEN  = (50,  200, 50)
RED    = (220, 40,  40)
CYAN   = (0,   200, 200)


class NameEntryScene(Scene):
    def init(self):
        self.font_lg = pygame.font.SysFont(None, 52)
        self.font_md = pygame.font.SysFont(None, 32)
        self.font_sm = pygame.font.SysFont(None, 24)
        self.name    = ""
        self.error   = ""
        btn_y = 460
        self.btn_start = Button((180, btn_y, 200, 44), "START", self.font_md)

    def process_input(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif e.key == pygame.K_RETURN:
                    self._confirm()
                elif e.key == pygame.K_ESCAPE:
                    self.game.switch_scene("menu")
                elif len(self.name) < 16 and e.unicode.isprintable():
                    self.name += e.unicode
            if self.btn_start.is_clicked(pygame.mouse.get_pos(), e):
                self._confirm()

    def _confirm(self):
        name = self.name.strip()
        if not name:
            self.error = "Please enter a name."
            return
        self.game.username = name
        self.game.switch_scene("game")

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(DARK)
        draw_text(screen, self.font_lg, "RACER", YELLOW, (280, 120))
        draw_text(screen, self.font_md, "Enter your name:", WHITE, (280, 230))
        box = pygame.Rect(130, 270, 300, 46)
        pygame.draw.rect(screen, GRAY, box, border_radius=4)
        pygame.draw.rect(screen, WHITE, box, 2, border_radius=4)
        draw_text(screen, self.font_md, self.name + "_", WHITE, (280, 293))
        if self.error:
            draw_text(screen, self.font_sm, self.error, RED, (280, 340))
        pos = pygame.mouse.get_pos()
        self.btn_start.draw(screen, self.btn_start.is_hovered(pos))
        draw_text(screen, self.font_sm, "ESC = back", GRAY, (280, 540))


class MenuScene(Scene):
    def init(self):
        self.font_lg = pygame.font.SysFont(None, 64)
        self.font_md = pygame.font.SysFont(None, 34)
        bw, bh = 220, 48
        cx = 280 - bw // 2
        self.buttons = [
            Button((cx, 260, bw, bh), "Play",        self.font_md),
            Button((cx, 320, bw, bh), "Leaderboard", self.font_md),
            Button((cx, 380, bw, bh), "Settings",    self.font_md),
            Button((cx, 440, bw, bh), "Quit",        self.font_md),
        ]
        self.actions = ["nameentry", "leaderboard", "settings", "quit"]

    def process_input(self, events):
        pos = pygame.mouse.get_pos()
        for e in events:
            for btn, action in zip(self.buttons, self.actions):
                if btn.is_clicked(pos, e):
                    if action == "quit":
                        self.game.running = False
                    else:
                        self.game.switch_scene(action)

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(DARK)
        draw_text(screen, self.font_lg, "RACER", YELLOW, (280, 120))
        draw_text(screen, pygame.font.SysFont(None, 24), "Arcade Road Game", GRAY, (280, 175))
        pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.draw(screen, btn.is_hovered(pos))


class SettingsScene(Scene):
    COLORS      = ["red", "blue", "green", "yellow", "white"]
    DIFFS       = ["easy", "normal", "hard"]
    COLOR_DRAW  = {
        "red":    (220, 40,  40),
        "blue":   (40,  100, 220),
        "green":  (40,  180, 60),
        "yellow": (220, 200, 0),
        "white":  (230, 230, 230),
    }

    def init(self):
        self.font_md = pygame.font.SysFont(None, 32)
        self.font_sm = pygame.font.SysFont(None, 24)
        s = self.game.settings
        self.sound_on  = s["sound"]
        self.car_color = s["car_color"]
        self.difficulty = s["difficulty"]

        bw = 160
        self.btn_back = Button((200, 560, bw, 44), "Back", self.font_md)
        self.btn_save = Button((200, 500, bw, 44), "Save", self.font_md)

    def process_input(self, events):
        pos = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.game.switch_scene("menu")
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = pos
                if 160 <= mx <= 400:
                    if 200 <= my <= 230:
                        self.sound_on = not self.sound_on
                    elif 270 <= my <= 300:
                        idx = self.COLORS.index(self.car_color)
                        self.car_color = self.COLORS[(idx + 1) % len(self.COLORS)]
                    elif 340 <= my <= 370:
                        idx = self.DIFFS.index(self.difficulty)
                        self.difficulty = self.DIFFS[(idx + 1) % len(self.DIFFS)]

            if self.btn_save.is_clicked(pos, e):
                self.game.settings["sound"]      = self.sound_on
                self.game.settings["car_color"]  = self.car_color
                self.game.settings["difficulty"] = self.difficulty
                save_settings(self.game.settings)
            if self.btn_back.is_clicked(pos, e):
                self.game.switch_scene("menu")

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(DARK)
        draw_text(screen, self.font_md, "SETTINGS", WHITE, (280, 80))

        draw_text(screen, self.font_sm, "Sound:", GRAY, (130, 215))
        val = "ON" if self.sound_on else "OFF"
        col = GREEN if self.sound_on else RED
        draw_text(screen, self.font_md, val, col, (300, 215))
        draw_text(screen, self.font_sm, "< click to toggle >", GRAY, (280, 238))

        draw_text(screen, self.font_sm, "Car color:", GRAY, (130, 285))
        cdraw = self.COLOR_DRAW[self.car_color]
        pygame.draw.rect(screen, cdraw, (270, 270, 30, 20), border_radius=4)
        draw_text(screen, self.font_md, self.car_color, WHITE, (340, 285))
        draw_text(screen, self.font_sm, "< click to cycle >", GRAY, (280, 308))

        draw_text(screen, self.font_sm, "Difficulty:", GRAY, (130, 355))
        dcol = GREEN if self.difficulty == "easy" else YELLOW if self.difficulty == "normal" else RED
        draw_text(screen, self.font_md, self.difficulty.upper(), dcol, (300, 355))
        draw_text(screen, self.font_sm, "< click to cycle >", GRAY, (280, 378))

        pos = pygame.mouse.get_pos()
        self.btn_save.draw(screen, self.btn_save.is_hovered(pos))
        self.btn_back.draw(screen, self.btn_back.is_hovered(pos))


class LeaderboardScene(Scene):
    def init(self):
        self.font_lg = pygame.font.SysFont(None, 40)
        self.font_md = pygame.font.SysFont(None, 28)
        self.font_sm = pygame.font.SysFont(None, 22)
        self.board   = load_leaderboard()
        self.btn_back = Button((200, 580, 160, 44), "Back", self.font_md)

    def process_input(self, events):
        pos = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.game.switch_scene("menu")
            if self.btn_back.is_clicked(pos, e):
                self.game.switch_scene("menu")

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(DARK)
        draw_text(screen, self.font_lg, "TOP 10", YELLOW, (280, 50))
        headers = ["#", "Name", "Score", "Dist", "Coins"]
        xs      = [30, 80, 230, 340, 430]
        for i, (h, x) in enumerate(zip(headers, xs)):
            draw_text(screen, self.font_sm, h, GRAY, (x, 100))
        pygame.draw.line(screen, GRAY, (20, 115), (540, 115), 1)
        for rank, entry in enumerate(self.board[:10], 1):
            y   = 120 + rank * 44
            row_color = YELLOW if rank == 1 else WHITE
            vals = [
                str(rank),
                entry.get("name", "?")[:10],
                str(entry.get("score", 0)),
                str(entry.get("distance", 0)) + "m",
                str(entry.get("coins", 0)),
            ]
            for val, x in zip(vals, xs):
                draw_text(screen, self.font_md, val, row_color, (x, y))
        if not self.board:
            draw_text(screen, self.font_md, "No scores yet.", GRAY, (280, 300))
        pos = pygame.mouse.get_pos()
        self.btn_back.draw(screen, self.btn_back.is_hovered(pos))


class GameOverScene(Scene):
    def init(self):
        self.font_lg = pygame.font.SysFont(None, 56)
        self.font_md = pygame.font.SysFont(None, 32)
        self.font_sm = pygame.font.SysFont(None, 24)
        run = self.game.last_run or {}
        self.score    = run.get("score",    0)
        self.distance = run.get("distance", 0)
        self.coins    = run.get("coins",    0)
        bw, bh = 200, 46
        cx = 280 - bw // 2
        self.btn_retry = Button((cx, 430, bw, bh), "Retry",     self.font_md)
        self.btn_menu  = Button((cx, 490, bw, bh), "Main Menu", self.font_md)

    def process_input(self, events):
        pos = pygame.mouse.get_pos()
        for e in events:
            if self.btn_retry.is_clicked(pos, e):
                self.game.switch_scene("game")
            if self.btn_menu.is_clicked(pos, e):
                self.game.switch_scene("menu")

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(DARK)
        draw_text(screen, self.font_lg, "GAME OVER", RED, (280, 100))
        draw_text(screen, self.font_md, f"Player: {self.game.username}", WHITE,  (280, 190))
        draw_text(screen, self.font_md, f"Score:    {self.score}",       YELLOW, (280, 240))
        draw_text(screen, self.font_md, f"Distance: {self.distance}m",   WHITE,  (280, 280))
        draw_text(screen, self.font_md, f"Coins:    {self.coins}",       YELLOW, (280, 320))
        pos = pygame.mouse.get_pos()
        self.btn_retry.draw(screen, self.btn_retry.is_hovered(pos))
        self.btn_menu.draw(screen,  self.btn_menu.is_hovered(pos))
