import pygame

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

    def Terminate(self):
        self.SwitchToScene(None)

class LoadingScreen(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        text = "Press 'SPACE' to Start"
        font = pygame.font.Font('turok.otf', 32)
        self.textbox = font.render(text, True, (0,100,255), (255,255,255))
        # self.textRect = self.textbox.get_rect()
        
    
    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.SwitchToScene(GameScene)

    def Update(self):
        pass

    def Render(self, screen):
        x, y = screen.get_size()
        # self.textRect.center = (x // 2, y // 2)
        screen.blit(self.textbox, ((x-100)//2, (y-100)//2))

class GameScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        text = "Press 'SPACE' to Start"
        font = pygame.font.Font('turok.otf', 32)
        self.textbox = font.render(text, True, (0,100,255), (255,255,255))

class Snake:
    pass

def quitAttempt(event, pressed_keys):
    if event.type == pygame.QUIT:
        return True
    elif event.type == pygame.KEYDOWN:
        alt_pressed = pressed_keys[pygame.K_LALT] or \
                        pressed_keys[pygame.K_RALT]
        if event.key == pygame.K_ESCAPE:
            return True
        elif event.key == pygame.K_F4 and alt_pressed:
            return True
    return False


def run_game(width, height, fps, starting_scene):
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()
        
        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            if quitAttempt(event, pressed_keys):
                active_scene.Terminate()
            else:
                filtered_events.append(event)
        
        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)
        
        active_scene = active_scene.next
        
        pygame.display.flip()
        clock.tick(fps)

if __name__ == "__main__":
    pygame.init()
    run_game(600, 400, 60, LoadingScreen())