import pygame
import random
import math
from scene import Scene
from ui import draw_text
from persistence import save_score

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (100, 100, 100)
DARK   = (30,  30,  30)
GREEN  = (50,  200, 50)
YELLOW = (230, 200, 0)
RED    = (220, 40,  40)
BLUE   = (40,  120, 220)
CYAN   = (0,   220, 220)
ORANGE = (230, 130, 0)
PURPLE = (160, 40,  200)
LTGRAY = (180, 180, 180)
ROAD   = (60,  60,  60)
STRIPE = (220, 220, 0)

CAR_COLORS = {
    "red":    (220, 40,  40),
    "blue":   (40,  100, 220),
    "green":  (40,  180, 60),
    "yellow": (220, 200, 0),
    "white":  (230, 230, 230),
}

DIFFICULTY = {
    "easy":   {"traffic_interval": 3.0, "hazard_interval": 4.0, "base_speed": 180},
    "normal": {"traffic_interval": 2.0, "hazard_interval": 2.5, "base_speed": 220},
    "hard":   {"traffic_interval": 1.2, "hazard_interval": 1.5, "base_speed": 280},
}

LANE_COUNT  = 5
ROAD_LEFT   = 80
ROAD_RIGHT  = 480
ROAD_W      = ROAD_RIGHT - ROAD_LEFT
LANE_W      = ROAD_W // LANE_COUNT
W, H        = 560, 700


def lane_x(lane):
    return ROAD_LEFT + lane * LANE_W + LANE_W // 2


class RoadStripe:
    def __init__(self, y):
        self.y = y

    def update(self, speed, dt):
        self.y += speed * dt

    def render(self, screen):
        for lane in range(LANE_COUNT - 1):
            x = ROAD_LEFT + (lane + 1) * LANE_W
            if 0 <= self.y <= H:
                pygame.draw.rect(screen, STRIPE, (x - 2, self.y, 4, 30))


class PlayerCar:
    W, H = 36, 56

    def __init__(self, lane, color):
        self.lane   = lane
        self.color  = color
        self.x      = lane_x(lane)
        self.y      = H - 100
        self.moving = False
        self.target_x = self.x
        self.shield    = False
        self.nitro     = False

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = lane_x(self.lane)

    def move_right(self):
        if self.lane < LANE_COUNT - 1:
            self.lane += 1
            self.target_x = lane_x(self.lane)

    def update(self, dt):
        dx = self.target_x - self.x
        if abs(dx) > 2:
            self.x += dx * min(1, dt * 10)
        else:
            self.x = self.target_x

    def rect(self):
        return pygame.Rect(self.x - self.W // 2, self.y - self.H // 2, self.W, self.H)

    def render(self, screen):
        r = self.rect()
        pygame.draw.rect(screen, self.color, r, border_radius=6)
        pygame.draw.rect(screen, WHITE, (r.x + 4, r.y + 6, r.w - 8, 10), border_radius=3)
        pygame.draw.rect(screen, WHITE, (r.x + 4, r.bottom - 16, r.w - 8, 10), border_radius=3)
        if self.shield:
            pygame.draw.ellipse(screen, CYAN, r.inflate(12, 12), 3)
        if self.nitro:
            for i in range(3):
                fx = r.centerx + random.randint(-6, 6)
                fy = r.bottom + random.randint(4, 16)
                pygame.draw.circle(screen, ORANGE, (fx, fy), random.randint(3, 7))


class TrafficCar:
    W, H = 36, 56
    COLORS = [(180, 60, 60), (60, 80, 180), (60, 160, 60), (160, 120, 40)]

    def __init__(self, lane, speed):
        self.lane  = lane
        self.x     = lane_x(lane)
        self.y     = -40
        self.speed = speed
        self.color = random.choice(self.COLORS)

    def update(self, dt):
        self.y += self.speed * dt

    def rect(self):
        return pygame.Rect(self.x - self.W // 2, self.y - self.H // 2, self.W, self.H)

    def render(self, screen):
        r = self.rect()
        pygame.draw.rect(screen, self.color, r, border_radius=6)
        pygame.draw.rect(screen, LTGRAY, (r.x + 4, r.y + 6, r.w - 8, 10), border_radius=3)
        pygame.draw.rect(screen, LTGRAY, (r.x + 4, r.bottom - 16, r.w - 8, 10), border_radius=3)

    def off_screen(self):
        return self.y > H + 60


class Coin:
    def __init__(self, lane, speed, value=1):
        self.lane  = lane
        self.x     = lane_x(lane)
        self.y     = -20
        self.speed = speed
        self.value = value
        self.color = YELLOW if value == 1 else (220, 140, 0) if value == 2 else (180, 60, 220)
        self.r     = 10 if value == 1 else 13 if value == 2 else 16

    def update(self, dt):
        self.y += self.speed * dt

    def rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)

    def render(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.r, 2)
        label = {1: "1", 2: "2", 5: "5"}[self.value]
        font  = pygame.font.SysFont(None, 18)
        surf  = font.render(label, True, BLACK)
        screen.blit(surf, surf.get_rect(center=(int(self.x), int(self.y))))

    def off_screen(self):
        return self.y > H + 30


class Hazard:
    TYPES = ["oil", "bump", "pothole"]

    def __init__(self, lane, speed, htype=None):
        self.lane  = lane
        self.x     = lane_x(lane)
        self.y     = -30
        self.speed = speed
        self.htype = htype or random.choice(self.TYPES)
        self.w     = LANE_W - 10
        self.h     = 22

    def update(self, dt):
        self.y += self.speed * dt

    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def render(self, screen):
        r = self.rect()
        if self.htype == "oil":
            pygame.draw.ellipse(screen, (30, 30, 60), r)
            pygame.draw.ellipse(screen, PURPLE, r, 2)
            font = pygame.font.SysFont(None, 16)
            surf = font.render("OIL", True, PURPLE)
            screen.blit(surf, surf.get_rect(center=r.center))
        elif self.htype == "bump":
            pygame.draw.rect(screen, GRAY, r, border_radius=4)
            font = pygame.font.SysFont(None, 16)
            surf = font.render("BUMP", True, WHITE)
            screen.blit(surf, surf.get_rect(center=r.center))
        else:
            pygame.draw.ellipse(screen, DARK, r)
            pygame.draw.ellipse(screen, RED, r, 2)
            font = pygame.font.SysFont(None, 16)
            surf = font.render("HOLE", True, RED)
            screen.blit(surf, surf.get_rect(center=r.center))

    def off_screen(self):
        return self.y > H + 40


class PowerUp:
    TYPES = ["nitro", "shield", "repair"]
    COLORS = {"nitro": ORANGE, "shield": CYAN, "repair": GREEN}
    LABELS = {"nitro": "N", "shield": "S", "repair": "R"}
    LIFETIME = 8.0

    def __init__(self, lane, speed, ptype=None):
        self.lane    = lane
        self.x       = lane_x(lane)
        self.y       = -20
        self.speed   = speed
        self.ptype   = ptype or random.choice(self.TYPES)
        self.r       = 14
        self.elapsed = 0.0

    def update(self, dt):
        self.y       += self.speed * dt
        self.elapsed += dt

    def rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)

    def render(self, screen):
        color = self.COLORS[self.ptype]
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(screen, WHITE,  (int(self.x), int(self.y)), self.r, 2)
        font = pygame.font.SysFont(None, 20)
        surf = font.render(self.LABELS[self.ptype], True, BLACK)
        screen.blit(surf, surf.get_rect(center=(int(self.x), int(self.y))))

    def expired(self):
        return self.elapsed > self.LIFETIME or self.y > H + 30


class NitroStrip:
    def __init__(self, speed):
        self.x     = ROAD_LEFT
        self.y     = -30
        self.speed = speed
        self.w     = ROAD_W
        self.h     = 18

    def update(self, dt):
        self.y += self.speed * dt

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def render(self, screen):
        r = self.rect()
        pygame.draw.rect(screen, ORANGE, r)
        for i in range(0, self.w, 20):
            pygame.draw.line(screen, YELLOW, (r.x + i, r.y), (r.x + i + 10, r.y + r.h), 2)
        font = pygame.font.SysFont(None, 18)
        surf = font.render("NITRO STRIP", True, BLACK)
        screen.blit(surf, surf.get_rect(center=r.center))

    def off_screen(self):
        return self.y > H + 30


class GameScene(Scene):
    STRIPE_GAP    = 80
    COIN_INTERVAL  = 1.8
    POWERUP_INTERVAL = 7.0
    NITRO_STRIP_INTERVAL = 15.0
    NITRO_DURATION = 4.0
    NITRO_MULT     = 1.6
    CRASH_LIMIT    = 3

    def __init__(self, game):
        super().__init__(game)

    def init(self):
        s  = self.game.settings
        dc = DIFFICULTY[s["difficulty"]]
        self.base_speed       = dc["base_speed"]
        self.traffic_interval = dc["traffic_interval"]
        self.hazard_interval  = dc["hazard_interval"]
        self.road_speed       = self.base_speed

        color = CAR_COLORS.get(s["car_color"], RED)
        self.player = PlayerCar(2, color)

        self.stripes   = [RoadStripe(y) for y in range(0, H, self.STRIPE_GAP)]
        self.traffic   = []
        self.coins     = []
        self.hazards   = []
        self.powerups  = []
        self.nitrostrips = []

        self.coin_count  = 0
        self.coin_score  = 0
        self.distance    = 0.0
        self.finish_dist = 3000.0
        self.score       = 0
        self.crashes     = 0

        self.traffic_timer  = 0.0
        self.hazard_timer   = 0.0
        self.coin_timer     = 0.0
        self.powerup_timer  = 0.0
        self.nitro_strip_timer = 0.0

        self.active_powerup      = None
        self.powerup_timer_left  = 0.0
        self.slowed              = False
        self.slow_timer          = 0.0
        self.bump_timer          = 0.0

        self.font_sm  = pygame.font.SysFont(None, 22)
        self.font_md  = pygame.font.SysFont(None, 30)
        self.font_lg  = pygame.font.SysFont(None, 48)

        self.flash_msg  = ""
        self.flash_time = 0.0
        self.running    = True

    def _difficulty_scale(self):
        progress = min(self.distance / self.finish_dist, 1.0)
        return 1.0 + progress * 1.5

    def _current_speed(self):
        spd = self.base_speed * self._difficulty_scale()
        if self.active_powerup == "nitro":
            spd *= self.NITRO_MULT
        if self.slowed:
            spd *= 0.5
        return spd

    def _safe_lane(self, exclude_lane=None):
        occupied = set()
        for obj in self.traffic + self.hazards + self.powerups + self.coins:
            if obj.y < 120:
                occupied.add(obj.lane)
        if exclude_lane is not None:
            occupied.add(exclude_lane)
        choices = [l for l in range(LANE_COUNT) if l not in occupied]
        return random.choice(choices) if choices else random.randint(0, LANE_COUNT - 1)

    def _spawn_traffic(self):
        spd = self._current_speed() * random.uniform(0.7, 0.95)
        lane = self._safe_lane(exclude_lane=self.player.lane)
        self.traffic.append(TrafficCar(lane, spd))

    def _spawn_hazard(self):
        spd  = self._current_speed()
        lane = self._safe_lane(exclude_lane=self.player.lane)
        self.hazards.append(Hazard(lane, spd))

    def _spawn_coin(self):
        spd  = self._current_speed()
        lane = random.randint(0, LANE_COUNT - 1)
        w    = random.choices([1, 2, 5], weights=[6, 3, 1])[0]
        self.coins.append(Coin(lane, spd, w))

    def _spawn_powerup(self):
        if self.active_powerup:
            return
        spd  = self._current_speed()
        lane = self._safe_lane()
        self.powerups.append(PowerUp(lane, spd))

    def _spawn_nitro_strip(self):
        self.nitrostrips.append(NitroStrip(self._current_speed()))

    def _apply_powerup(self, ptype):
        self.active_powerup = ptype
        if ptype == "nitro":
            self.powerup_timer_left = self.NITRO_DURATION
            self._flash("NITRO!")
        elif ptype == "shield":
            self.player.shield = True
            self.powerup_timer_left = 0
            self._flash("SHIELD!")
        elif ptype == "repair":
            if self.crashes > 0:
                self.crashes -= 1
            self.active_powerup = None
            self._flash("REPAIR!")
        self.score += 50

    def _flash(self, msg):
        self.flash_msg  = msg
        self.flash_time = 1.5

    def _handle_collision_traffic(self):
        if self.player.shield:
            self.player.shield = False
            self.active_powerup = None
            self._flash("SHIELD USED!")
            return
        self.crashes += 1
        self._flash(f"CRASH! ({self.crashes}/{self.CRASH_LIMIT})")
        if self.crashes >= self.CRASH_LIMIT:
            self._end_game()

    def _handle_collision_hazard(self, h):
        if self.player.shield:
            self.player.shield = False
            self.active_powerup = None
            self._flash("SHIELD USED!")
            return
        if h.htype == "oil":
            self.slowed   = True
            self.slow_timer = 2.5
            self._flash("SLIPPING!")
        elif h.htype == "bump":
            self.slowed    = True
            self.slow_timer = 1.0
            self._flash("BUMP!")
        elif h.htype == "pothole":
            self.crashes += 1
            self._flash(f"POTHOLE! ({self.crashes}/{self.CRASH_LIMIT})")
            if self.crashes >= self.CRASH_LIMIT:
                self._end_game()

    def _end_game(self):
        self.running = False
        final_score = self.score + int(self.distance)
        save_score(self.game.username, final_score, self.distance, self.coin_count)
        self.game.last_run = {
            "score": final_score,
            "distance": int(self.distance),
            "coins": self.coin_count,
        }
        self.game.switch_scene("gameover")

    def process_input(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    self.player.move_left()
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    self.player.move_right()
                elif e.key == pygame.K_ESCAPE:
                    self.game.switch_scene("menu")

    def update(self, dt):
        if not self.running:
            return

        scale = self._difficulty_scale()
        self.road_speed = self._current_speed()

        self.distance += self.road_speed * dt * 0.05
        self.score     = self.coin_score + int(self.distance)

        if self.distance >= self.finish_dist:
            self._flash("FINISH!")
            self._end_game()
            return

        if self.slowed:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slowed = False

        if self.active_powerup == "nitro":
            self.powerup_timer_left -= dt
            self.player.nitro = True
            if self.powerup_timer_left <= 0:
                self.active_powerup = None
                self.player.nitro   = False
        else:
            self.player.nitro = False

        if self.flash_time > 0:
            self.flash_time -= dt

        for s in self.stripes:
            s.update(self.road_speed, dt)
        self.stripes = [s for s in self.stripes if s.y <= H]
        if not self.stripes or self.stripes[-1].y > self.STRIPE_GAP:
            self.stripes.append(RoadStripe(-10))

        self.traffic_timer += dt
        ti = self.traffic_interval / scale
        if self.traffic_timer >= ti:
            self.traffic_timer = 0
            self._spawn_traffic()

        self.hazard_timer += dt
        hi = self.hazard_interval / scale
        if self.hazard_timer >= hi:
            self.hazard_timer = 0
            self._spawn_hazard()

        self.coin_timer += dt
        if self.coin_timer >= self.COIN_INTERVAL:
            self.coin_timer = 0
            self._spawn_coin()

        self.powerup_timer += dt
        if self.powerup_timer >= self.POWERUP_INTERVAL:
            self.powerup_timer = 0
            self._spawn_powerup()

        self.nitro_strip_timer += dt
        if self.nitro_strip_timer >= self.NITRO_STRIP_INTERVAL:
            self.nitro_strip_timer = 0
            self._spawn_nitro_strip()

        for obj in self.traffic:
            obj.update(dt)
        for obj in self.hazards:
            obj.update(dt)
        for obj in self.coins:
            obj.update(dt)
        for obj in self.powerups:
            obj.update(dt)
        for obj in self.nitrostrips:
            obj.update(dt)

        pr = self.player.rect()
        for t in self.traffic[:]:
            if pr.colliderect(t.rect()):
                self.traffic.remove(t)
                self._handle_collision_traffic()
                if not self.running:
                    return

        for h in self.hazards[:]:
            if pr.colliderect(h.rect()):
                self.hazards.remove(h)
                self._handle_collision_hazard(h)
                if not self.running:
                    return

        for c in self.coins[:]:
            if pr.colliderect(c.rect()):
                self.coins.remove(c)
                self.coin_count += 1
                self.coin_score += c.value * 10
                self.road_speed = min(self.road_speed + 5, self.base_speed * 2)

        for p in self.powerups[:]:
            if pr.colliderect(p.rect()):
                self.powerups.remove(p)
                self._apply_powerup(p.ptype)

        for n in self.nitrostrips[:]:
            if pr.colliderect(n.rect()):
                self.nitrostrips.remove(n)
                if self.active_powerup != "nitro":
                    self.active_powerup     = "nitro"
                    self.powerup_timer_left = self.NITRO_DURATION
                    self.player.nitro       = True
                    self._flash("NITRO STRIP!")

        self.traffic    = [t for t in self.traffic    if not t.off_screen()]
        self.hazards    = [h for h in self.hazards    if not h.off_screen()]
        self.coins      = [c for c in self.coins      if not c.off_screen()]
        self.powerups   = [p for p in self.powerups   if not p.expired()]
        self.nitrostrips = [n for n in self.nitrostrips if not n.off_screen()]

        self.player.update(dt)

    def render(self, screen):
        screen.fill(DARK)
        pygame.draw.rect(screen, ROAD, (ROAD_LEFT, 0, ROAD_W, H))
        pygame.draw.rect(screen, WHITE, (ROAD_LEFT, 0, 3, H))
        pygame.draw.rect(screen, WHITE, (ROAD_RIGHT - 3, 0, 3, H))

        for s in self.stripes:
            s.render(screen)
        for n in self.nitrostrips:
            n.render(screen)
        for h in self.hazards:
            h.render(screen)
        for c in self.coins:
            c.render(screen)
        for p in self.powerups:
            p.render(screen)
        for t in self.traffic:
            t.render(screen)
        self.player.render(screen)

        self._render_hud(screen)

    def _render_hud(self, screen):
        W_S = 560
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, ROAD_LEFT, H))
        pygame.draw.rect(screen, (20, 20, 20), (ROAD_RIGHT, 0, W_S - ROAD_RIGHT, H))

        def left_text(txt, y, color=WHITE):
            draw_text(screen, self.font_sm, txt, color, (40, y))

        left_text(f"Score", 30)
        left_text(f"{self.score}", 50, YELLOW)
        left_text(f"Coins", 80)
        left_text(f"{self.coin_count}", 100, YELLOW)
        left_text(f"Dist", 130)
        prog = min(self.distance / self.finish_dist, 1.0)
        left_text(f"{int(self.distance)}m", 150, YELLOW)
        pygame.draw.rect(screen, GRAY,  (10, 170, 60, 10))
        pygame.draw.rect(screen, GREEN, (10, 170, int(60 * prog), 10))
        left_text(f"HP", 195)
        hp = max(0, self.CRASH_LIMIT - self.crashes)
        for i in range(self.CRASH_LIMIT):
            c = RED if i < hp else GRAY
            pygame.draw.circle(screen, c, (15 + i * 18, 215), 7)

        rx = ROAD_RIGHT + 10
        def right_text(txt, y, color=WHITE):
            draw_text(screen, self.font_sm, txt, color, (rx + 25, y))

        right_text("Power", 30)
        if self.active_powerup == "nitro":
            right_text(f"NITRO", 52, ORANGE)
            right_text(f"{self.powerup_timer_left:.1f}s", 70, ORANGE)
        elif self.active_powerup == "shield":
            right_text("SHIELD", 52, CYAN)
        elif self.active_powerup:
            right_text(self.active_powerup.upper(), 52, GREEN)
        else:
            right_text("none", 52, GRAY)

        right_text("Keys:", 200)
        right_text("←→ move", 220, GRAY)
        right_text("ESC menu", 238, GRAY)

        if self.slowed:
            draw_text(screen, self.font_md, "SLOWED!", RED, (W_S // 2, H - 40))

        if self.flash_time > 0:
            alpha = min(255, int(255 * self.flash_time))
            surf  = self.font_lg.render(self.flash_msg, True, YELLOW)
            surf.set_alpha(alpha)
            screen.blit(surf, surf.get_rect(center=(W_S // 2, H // 2 - 60)))
