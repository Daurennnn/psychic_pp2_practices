import pygame
import sys
from datetime import datetime
from tools import flood_fill, draw_equilateral_triangle, draw_right_triangle, draw_rhombus

# Window and canvas dimensions
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
TOOLBAR_WIDTH = 160
CANVAS_X = TOOLBAR_WIDTH
CANVAS_Y = 0
CANVAS_WIDTH = WINDOW_WIDTH - TOOLBAR_WIDTH
CANVAS_HEIGHT = WINDOW_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (230, 230, 230)
HIGHLIGHT = (173, 216, 230)

# Color palette
PALETTE = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
    (0, 0, 255), (255, 255, 0), (255, 165, 0), (128, 0, 128),
    (0, 255, 255), (255, 20, 147), (139, 69, 19), (128, 128, 128),
]

# Brush sizes
BRUSH_SIZES = {1: 2, 2: 5, 3: 10}

# All available tools
TOOLS = [
    "pencil", "line", "rect", "circle",
    "square", "right_tri", "eq_tri", "rhombus",
    "eraser", "fill", "text",
]

TOOL_LABELS = {
    "pencil": "Pencil",
    "line": "Line",
    "rect": "Rectangle",
    "circle": "Circle",
    "square": "Square",
    "right_tri": "R.Triangle",
    "eq_tri": "Eq.Triangle",
    "rhombus": "Rhombus",
    "eraser": "Eraser",
    "fill": "Fill",
    "text": "Text",
}


def draw_toolbar(screen, font, active_tool, active_color, brush_key):
    # Toolbar background
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, TOOLBAR_WIDTH, WINDOW_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (TOOLBAR_WIDTH, 0), (TOOLBAR_WIDTH, WINDOW_HEIGHT), 2)

    y = 10
    # Draw tool buttons
    for tool in TOOLS:
        rect = pygame.Rect(5, y, TOOLBAR_WIDTH - 10, 28)
        color = HIGHLIGHT if tool == active_tool else WHITE
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, DARK_GRAY, rect, 1, border_radius=4)
        label = font.render(TOOL_LABELS[tool], True, BLACK)
        screen.blit(label, (rect.x + 5, rect.y + 6))
        y += 32

    y += 6
    # Brush size buttons
    size_label = font.render("Brush Size:", True, BLACK)
    screen.blit(size_label, (5, y))
    y += 18
    for key in [1, 2, 3]:
        rect = pygame.Rect(5, y, TOOLBAR_WIDTH - 10, 24)
        color = HIGHLIGHT if key == brush_key else WHITE
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, DARK_GRAY, rect, 1, border_radius=4)
        names = {1: "1-Small(2px)", 2: "2-Med(5px)", 3: "3-Large(10px)"}
        label = font.render(names[key], True, BLACK)
        screen.blit(label, (rect.x + 4, rect.y + 4))
        y += 28

    y += 6
    # Color palette
    col_label = font.render("Colors:", True, BLACK)
    screen.blit(col_label, (5, y))
    y += 18
    for i, color in enumerate(PALETTE):
        row = i // 2
        col = i % 2
        rect = pygame.Rect(5 + col * 38, y + row * 22, 34, 18)
        pygame.draw.rect(screen, color, rect)
        if color == active_color:
            pygame.draw.rect(screen, BLACK, rect, 3)
        else:
            pygame.draw.rect(screen, DARK_GRAY, rect, 1)

    # Show active color swatch at bottom
    swatch_y = WINDOW_HEIGHT - 60
    pygame.draw.rect(screen, BLACK, (5, swatch_y, TOOLBAR_WIDTH - 10, 30), 1)
    pygame.draw.rect(screen, active_color, (6, swatch_y + 1, TOOLBAR_WIDTH - 12, 28))
    cur_label = font.render("Active color", True, BLACK)
    screen.blit(cur_label, (5, swatch_y + 32))

    return y  # return where palette ends for click detection


def get_toolbar_click(mx, my, active_tool, active_color, brush_key):
    y = 10
    for tool in TOOLS:
        rect = pygame.Rect(5, y, TOOLBAR_WIDTH - 10, 28)
        if rect.collidepoint(mx, my):
            return tool, active_color, brush_key
        y += 32

    y += 24  # label
    for key in [1, 2, 3]:
        rect = pygame.Rect(5, y, TOOLBAR_WIDTH - 10, 24)
        if rect.collidepoint(mx, my):
            return active_tool, active_color, key
        y += 28

    y += 24  # color label
    for i, color in enumerate(PALETTE):
        row = i // 2
        col = i % 2
        rect = pygame.Rect(5 + col * 38, y + row * 22, 34, 18)
        if rect.collidepoint(mx, my):
            return active_tool, color, brush_key

    return active_tool, active_color, brush_key


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Paint App")

    font = pygame.font.SysFont("Arial", 12)
    text_font = pygame.font.SysFont("Arial", 20)

    # Canvas is a separate surface so we can save it cleanly
    canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
    canvas.fill(WHITE)

    # Preview surface for live shape preview (line, rect, etc.)
    preview = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)

    active_tool = "pencil"
    active_color = BLACK
    brush_key = 1

    drawing = False
    start_pos = None
    last_pos = None

    # Text tool state
    text_mode = False
    text_pos = None
    text_buffer = ""

    clock = pygame.time.Clock()

    while True:
        brush_size = BRUSH_SIZES[brush_key]
        mx, my = pygame.mouse.get_pos()
        canvas_mx = mx - CANVAS_X
        canvas_my = my - CANVAS_Y

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard events
            if event.type == pygame.KEYDOWN:
                # Brush size shortcuts
                if event.key == pygame.K_1:
                    brush_key = 1
                elif event.key == pygame.K_2:
                    brush_key = 2
                elif event.key == pygame.K_3:
                    brush_key = 3

                # Save with Ctrl+S
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"canvas_{timestamp}.png"
                    pygame.image.save(canvas, filename)
                    print(f"Saved: {filename}")

                # Text tool input
                if text_mode and active_tool == "text":
                    if event.key == pygame.K_RETURN:
                        # Render text permanently onto canvas
                        rendered = text_font.render(text_buffer, True, active_color)
                        canvas.blit(rendered, text_pos)
                        text_mode = False
                        text_buffer = ""
                        text_pos = None
                    elif event.key == pygame.K_ESCAPE:
                        text_mode = False
                        text_buffer = ""
                        text_pos = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode

            # Mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mx < TOOLBAR_WIDTH:
                    # Click on toolbar
                    active_tool, active_color, brush_key = get_toolbar_click(
                        mx, my, active_tool, active_color, brush_key
                    )
                    text_mode = False
                    text_buffer = ""
                else:
                    # Click on canvas
                    pos = (canvas_mx, canvas_my)

                    if active_tool == "fill":
                        flood_fill(canvas, canvas_mx, canvas_my, active_color)

                    elif active_tool == "text":
                        text_mode = True
                        text_pos = pos
                        text_buffer = ""

                    else:
                        drawing = True
                        start_pos = pos
                        last_pos = pos

            # Mouse button up
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos:
                    pos = (canvas_mx, canvas_my)
                    draw_shape(canvas, active_tool, active_color, brush_size, start_pos, pos)
                drawing = False
                start_pos = None
                last_pos = None

            # Mouse motion
            if event.type == pygame.MOUSEMOTION:
                if drawing and mx >= CANVAS_X:
                    pos = (canvas_mx, canvas_my)
                    if active_tool == "pencil":
                        if last_pos:
                            pygame.draw.line(canvas, active_color, last_pos, pos, brush_size)
                        last_pos = pos
                    elif active_tool == "eraser":
                        if last_pos:
                            pygame.draw.line(canvas, WHITE, last_pos, pos, brush_size * 4)
                        last_pos = pos

        # Draw everything
        screen.fill(LIGHT_GRAY)
        screen.blit(canvas, (CANVAS_X, CANVAS_Y))

        # Live preview for shape tools while dragging
        if drawing and start_pos and active_tool not in ("pencil", "eraser", "fill", "text"):
            pos = (canvas_mx, canvas_my)
            preview.fill((0, 0, 0, 0))
            draw_shape(preview, active_tool, active_color, brush_size, start_pos, pos)
            screen.blit(preview, (CANVAS_X, CANVAS_Y))

        # Text cursor and live text preview
        if text_mode and text_pos:
            preview.fill((0, 0, 0, 0))
            rendered = text_font.render(text_buffer + "|", True, active_color)
            preview.blit(rendered, text_pos)
            screen.blit(preview, (CANVAS_X, CANVAS_Y))

        draw_toolbar(screen, font, active_tool, active_color, brush_key)
        pygame.display.flip()
        clock.tick(60)


def draw_shape(surface, tool, color, brush_size, start, end):
    x1, y1 = start
    x2, y2 = end

    if tool == "line":
        pygame.draw.line(surface, color, start, end, brush_size)

    elif tool == "rect":
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(surface, color, rect, brush_size)

    elif tool == "square":
        side = min(abs(x2 - x1), abs(y2 - y1))
        sx = x1 if x2 >= x1 else x1 - side
        sy = y1 if y2 >= y1 else y1 - side
        rect = pygame.Rect(sx, sy, side, side)
        pygame.draw.rect(surface, color, rect, brush_size)

    elif tool == "circle":
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        r = max(abs(x2 - x1), abs(y2 - y1)) // 2
        pygame.draw.circle(surface, color, (cx, cy), r, brush_size)

    elif tool == "right_tri":
        draw_right_triangle(surface, color, start, end, brush_size)

    elif tool == "eq_tri":
        draw_equilateral_triangle(surface, color, start, end, brush_size)

    elif tool == "rhombus":
        draw_rhombus(surface, color, start, end, brush_size)


if __name__ == "__main__":
    main()
