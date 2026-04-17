import pygame

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

quit = False
while not quit:

    quit = quitAttempt()