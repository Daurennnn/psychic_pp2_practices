import pygame
import os
import math

class ImageLibrary:
    def __init__(self):
        self._image_library = {}
    def get_image(self, path):
        image = self._image_library.get(path)
        if image == None:
            canonic_path = path.replace('/', os.sep).replace('\\', os.sep)
            image = pygame.image.load(canonic_path)
            self._image_library[path] = image
        return image
    
def rotate_image(image, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    rect_centered = rotated_image.get_rect(center=image.get_rect(center=(50, 50)).center)
    return (rotated_image, rect_centered)
# def rotate_axis(image, angle, x, y):
#     rotated_image = pygame.transform.rotate(image, angle)

#     center_x, center_y = 

#     rect_centered = rotated_image.get_rect(center=image.get_rect)

pygame.init()
screen = pygame.display.set_mode((400, 300))
done = False
clock = pygame.time.Clock()

Sprites = ImageLibrary()
Sprites.get_image('tutorial_2_3.png')

ball = Sprites.get_image('tutorial_2_3.png')
ball_directed = ball
angle = 0
color = (0, 255, 0)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            color = (255, 0, 0)
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            color = (0, 255, 0)
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        angle += 1

    screen.fill((0, 0, 0))
    indicators_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.rect(indicators_surface, color, pygame.Rect(5, 5, 40, 40))
    screen.blit(indicators_surface, (0, 0))

    screen.blit(*rotate_image(ball, angle))
    
    
    pygame.display.flip()
    clock.tick(60)