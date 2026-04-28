import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARK = (40, 40, 40)
HIGHLIGHT = (200, 200, 60)


class Button:
    def __init__(self, rect, label, font):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font

    def draw(self, screen, hovered=False):
        color = HIGHLIGHT if hovered else GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=4)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=4)
        text = self.font.render(self.label, True, BLACK if hovered else WHITE)
        tr = text.get_rect(center=self.rect.center)
        screen.blit(text, tr)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(pos)
        )


def draw_text(screen, font, text, color, center):
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=center))
