import pygame
from collections import deque


# Flood fill using BFS
def flood_fill(surface, x, y, fill_color):
    target_color = surface.get_at((x, y))
    target_color = (target_color.r, target_color.g, target_color.b)
    fill_color = fill_color[:3]

    if target_color == fill_color:
        return

    width, height = surface.get_size()
    visited = set()
    queue = deque()
    queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cx >= width or cy < 0 or cy >= height:
            continue
        current = surface.get_at((cx, cy))
        current = (current.r, current.g, current.b)
        if current != target_color:
            continue
        visited.add((cx, cy))
        surface.set_at((cx, cy), fill_color)
        queue.append((cx + 1, cy))
        queue.append((cx - 1, cy))
        queue.append((cx, cy + 1))
        queue.append((cx, cy - 1))


# Draw equilateral triangle given bounding box start and end
def draw_equilateral_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    base_len = abs(x2 - x1)
    height = int(base_len * (3 ** 0.5) / 2)
    direction = 1 if y2 >= y1 else -1
    p1 = (x1, y1 + direction * height)
    p2 = (x2, y1 + direction * height)
    p3 = ((x1 + x2) // 2, y1)
    pygame.draw.polygon(surface, color, [p1, p2, p3], width)


# Draw right triangle
def draw_right_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    p1 = (x1, y1)
    p2 = (x1, y2)
    p3 = (x2, y2)
    pygame.draw.polygon(surface, color, [p1, p2, p3], width)


# Draw rhombus
def draw_rhombus(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    mx = (x1 + x2) // 2
    my = (y1 + y2) // 2
    p1 = (mx, y1)
    p2 = (x2, my)
    p3 = (mx, y2)
    p4 = (x1, my)
    pygame.draw.polygon(surface, color, [p1, p2, p3, p4], width)
