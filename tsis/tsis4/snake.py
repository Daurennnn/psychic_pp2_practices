import pygame
import random
import db

class SceneBase:
    def __init__(self):
        self.next = self
    
    def ProcessInput(self, events):
        print("uh-oh, you didn't override this in the child class")

    def Update(self):
        print("uh-oh, you didn't override this in the child class")

    def Render(self, screen):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene

class Menu(SceneBase):
    def __init__(self):
        self.next = self
        restart_rect = pygame.Rect(0, 0, 100, 30)
        restart_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        self.start_button = Button('Start', (100, 100, 100), 
                                   restart_rect,
                                   (200, 200, 0))
        name_rect = pygame.Rect(0, 0, 100, 30)
        name_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40)
        self.name_box = TextBox(name_rect, FONT_FREESANS)
    def ProcessInput(self, events):
        done = False
        for event in events:
            if event.type == pygame.QUIT:
                done = True
            if self.start_button.isPressed(event):
                self.SwitchToScene(GameWindow(self.name_box.text))
            self.name_box.handle_event(event)
        
        return done
    
    def Update(self, screen):
        self.Render(screen)
    def Render(self, screen):
        screen.fill((0, 0, 0))
        self.start_button.render(screen)
        self.name_box.render(screen)
        
        

class GameWindow(SceneBase):
    def __init__(self, nickname):
        self.next = self
        self.snake = Snake()
        self.moveSwitch = 0
        self.frameDelay = FRAME_RATE
        self.keyExpected = True
        self.lost = False
        self.nickname = nickname
        self.start_time = pygame.time.get_ticks()
        self.player_stats = db.get_player_stats(self.nickname)
        self.player_stats.pop('avg_score')
        print(self.player_stats)


    def ProcessInput(self, events):
        done = False
        direction = self.snake.direction
        for event in events:
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN and direction != self.snake.D_Up and self.keyExpected == True:
                    self.snake.turnDown()
                    self.keyExpected = False
                elif event.key == pygame.K_UP and direction != self.snake.D_Down and self.keyExpected == True:
                    self.snake.turnUp()
                    self.keyExpected = False
                elif event.key == pygame.K_LEFT and direction != self.snake.D_Right and self.keyExpected == True:
                    self.snake.turnLeft()
                    self.keyExpected = False
                elif event.key == pygame.K_RIGHT and direction != self.snake.D_Left and self.keyExpected == True:
                    self.snake.turnRight()
                    self.keyExpected = False

        return done
    
    def Update(self, screen):
        ate_apple = self.snake.appleEaten()
        if ate_apple != -1:
            self.snake.addSize(ate_apple)
            weight = int(random.randint(1, MAX_APPLE**3)**(1/3))
            self.snake.createApple(weight)

        if self.snake.collision(GRID_WIDTH, GRID_HEIGHT): self.lost = True
        if not self.lost:
            self.moveSwitch = self.moveSwitch + 1
            self.frameDelay = int(FRAME_RATE / self.snake.speed)
            if self.moveSwitch == self.frameDelay:
                self.keyExpected = True
                self.moveSwitch = 0
                self.snake.move()
            self.Render(screen)
        else:
            self.endscreen(screen)

    def drawGrid(self, screen):
        x0, y0, _, _ = centerGrid()
        for x in range(0, GRID_WIDTH):
            for y in range(0, GRID_HEIGHT):
                rect = pygame.Rect(x0 + x * GRID_SIZE, y0 + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)

    def showStats(self, screen):
        y = 10
        nick_text = FONT_FREESANS.render('Player: ' + self.nickname, True, (255, 255, 255), (0, 0, 0))
        screen.blit(nick_text, (10, 10))
        w, h = FONT_FREESANS.size('Player')
        y += h

        body_text = FONT_FREESANS.render('Body size: ' + str(self.snake.size), True, (255, 255, 255), (0, 0, 0))
        screen.blit(body_text, (10, y))
        y += h

        for title, value in self.player_stats.items():
            stat = FONT_FREESANS.render(f'{title}: {value}', True, (255, 255, 255), (0, 0, 0))
            screen.blit(stat, (10, y))
            y += h

    def Render(self, screen):
        screen.fill((0,0,0))
        self.snake.drawSnake(screen)
        self.snake.drawApples(screen)
        self.drawGrid(screen)
        self.showStats(screen)
        
    def endscreen(self, screen):
        db.save_result(nickname=self.nickname, 
                       points=self.snake.size, 
                       play_time=(pygame.time.get_ticks() - self.start_time)//1000)
        self.SwitchToScene(EndScreen(self.nickname))

class EndScreen(SceneBase):
    def __init__(self, nickname):
        self.next = self
        self.nickname = nickname
        restart_rect = pygame.Rect(0, 0, 100, 30)
        restart_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40)
        self.restart_button = Button('Restart', (100, 100, 100), 
                                   restart_rect,
                                   (200, 200, 0))
        menu_rect = restart_rect.copy()
        menu_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 90)
        self.menu_button = Button('Main Menu', (100, 100, 100), 
                                   menu_rect,
                                   (200, 200, 0))
        
    def ProcessInput(self, events):
        done = False
        for event in events:
            if event.type == pygame.QUIT:
                done = True
            if self.restart_button.isPressed(event):
                self.SwitchToScene(GameWindow(self.nickname))
            if self.menu_button.isPressed(event):
                self.SwitchToScene(Menu())

        return done
        
    def Update(self, screen):
        self.Render(screen)
    def Render(self, screen):
        endscreen_font = pygame.font.Font(None, 40)
        text_youlose = endscreen_font.render('YOU LOSE', True, (255, 50, 50))
        box = text_youlose.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        screen.blit(text_youlose, box)
        self.restart_button.render(screen)
        self.menu_button.render(screen)
        
class Snake:
    def __init__(self):
        # self.head = [5, 5]
        self.body = [(GRID_WIDTH//2, GRID_HEIGHT//2), (GRID_WIDTH//2 - 1, GRID_WIDTH//2)]
        self.size = 1
        self.direction = [1, 0]
        self.D_Right = [1, 0]
        self.D_Down = [0, 1]
        self.D_Left = [-1, 0]
        self.D_Up = [0, -1]
        self.speed = SNAKE_SPEED
        self.apples = []
        self.createApple()

    def turnRight(self):
        self.direction = self.D_Right
    def turnDown(self):
        self.direction = self.D_Down
    def turnLeft(self):
        self.direction = self.D_Left
    def turnUp(self):
        self.direction = self.D_Up
    def move(self):
        for i in range(self.size, 0, -1):
            x0, y0 = self.body[i - 1]
            self.body[i] = (x0, y0)
        x, y = self.body[0]
        dx, dy = self.direction
        self.body[0] = (x+dx, y+dy)

    def addSize(self, increment):
        if increment > 0:
            self.size += 1
            x1, y1 = self.body[-1]
            x2, y2 = self.body[-2]
            x_new, y_new = x1 + (x1 - x2), y1 + (y1 - y2)
            self.body.append((x_new, y_new))
            
            increment -= 1
            self.addSize(increment)

    def collision(self, x_max, y_max):
        for section in self.body[1:]:
            if self.body[0] == section: return True
        
        head_x, head_y = self.body[0]
        if not (0 <= head_x <= x_max - 1 and 0 <= head_y <= y_max - 1):
            return True
        
        return False
    
    def createApple(self, weight = 1):
        is_intersecting = True
        while is_intersecting:
            x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            for i in self.body:
                if (x, y) != i:
                    is_intersecting = False
                    break
        self.apples.append({'pos': (x, y), 'w': weight})

    def appleEaten(self):
        for i in self.body:
            for j in range(len(self.apples)):
                if i == self.apples[j]['pos']:
                    weight = self.apples[j]['w']
                    del self.apples[j]
                    return weight
        
        return -1
    
    def drawSnake(self, screen):
        x0, y0, _, _ = centerGrid()
        for i in range(self.size):
            x, y = self.body[i]
            rect = pygame.Rect(x0 + x * GRID_SIZE, y0 + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, (0, 200, 50), rect)
            text = FONT_FREESANS.render(str(i), True, (0, 0, 0))
            screen.blit(text, rect)

    def drawApples(self, screen):
        x0, y0, _, _ = centerGrid()
        for i in self.apples:
            x, y = i['pos']
            w = i['w']
            rect = pygame.Rect(x0 + x * GRID_SIZE, y0 + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, (255, 100, 100), rect)
            text = FONT_FREESANS.render(str(w), True, (0, 0, 0))
            screen.blit(text, rect)
        
class Button:
    def __init__(self, text: str, text_color, rect: pygame.Rect, color):
        self.text = text
        self.text_color = text_color
        self.rect = rect
        self.color = color

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text = FONT_FREESANS.render(self.text, True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def isPressed(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class TextBox:
    def __init__(self, rect: pygame.Rect, font):
        self.rect = rect
        self.font = font
        self.text = ""
        self._cursor_visible = True
        self._cursor_timer = 0
 
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable():
                self.text += event.unicode
 
    def update(self, dt):
        self._cursor_timer += dt
        if self._cursor_timer >= 500:
            self._cursor_timer = 0
            self._cursor_visible = not self._cursor_visible
 
    def render(self, surface):
        pygame.draw.rect(surface, (30, 30, 30), self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
 
        display = self.text + ("|" if self._cursor_visible else " ")
        text_surf = self.font.render(display, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 8, self.rect.centery - text_surf.get_height() // 2))


def centerGrid():
        grid_box = pygame.Rect(0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE)
        grid_box.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        return grid_box

pygame.init()

SNAKE_SPEED = 5
GRID_WIDTH, GRID_HEIGHT = 15, 15
GRID_SIZE = 45
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 700
FRAME_RATE = 60
FONT_FREESANS = pygame.font.Font(None, 30)
clock = pygame.time.Clock()
current_time = pygame.time.get_ticks()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
screen.fill((0,0,0))
scene = Menu()

MAX_APPLE = 4

db.init_db()



done = False
lost = False
while not done:
    events = pygame.event.get()
    done = scene.ProcessInput(events)
    
    scene.Update(screen)
    scene = scene.next

    pygame.display.flip()
    clock.tick(FRAME_RATE)