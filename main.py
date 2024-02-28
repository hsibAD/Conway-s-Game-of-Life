import pygame
import sys
import numpy as np

pygame.init()

pygame.mixer.music.load('sound/song.mp3')
pygame.mixer.music.play(-1)
click = pygame.mixer.Sound('sound/click.wav')

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Conway's Game of Life")

BG_COLOR = (10, 10, 10)
TEXT_COLOR = (255, 255, 255)
ALIVE_COLOR = (0, 255, 0)
DEAD_COLOR = (245, 245, 245)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
GRADIENT_TOP = (23, 32, 42)
GRADIENT_BOTTOM = (44, 62, 80)
GRID_COLOR = (200, 200, 200)

font = pygame.font.Font(None, 50)
button_font = pygame.font.Font(None, 36)


grid_history = []

def draw_gradient_background(top_color, bottom_color):
    top = pygame.Color(*top_color)
    bottom = pygame.Color(*bottom_color)
    for Y in range(HEIGHT):
        color = tuple(
            top.lerp(bottom, Y / HEIGHT)[i] for i in range(3)
        )
        pygame.draw.line(screen, color, (0, Y), (WIDTH, Y))

def draw_button(text, x, y, width, height, mouse_pos, action=None):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect, border_radius=10)
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect, border_radius=10)
        if pygame.mouse.get_pressed()[0]:
            pygame.time.wait(200)
            if action:
                action()

    text_surf = button_font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))
    screen.blit(text_surf, text_rect)

def clear_grid():
    global grid, grid_history
    grid = np.zeros((grid_size, grid_size))
    grid_history = []

def draw_grid():
    for x in range(0, WIDTH, cell_size):
        for y in range(0, HEIGHT, cell_size):
            rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

def update_grid(grid):
    new_grid = grid.copy()
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            alive_neighbors = np.sum(grid[i-1:i+2, j-1:j+2]) - grid[i, j]
            if grid[i, j] == 1:
                if alive_neighbors < 2 or alive_neighbors > 3:
                    new_grid[i, j] = 0
            else:
                if alive_neighbors == 3:
                    new_grid[i, j] = 1
    return new_grid

def set_difficulty(difficulty):
    global grid_size, cell_size
    if difficulty == "easy":
        grid_size = 5
    elif difficulty == "medium":
        grid_size = 20
    elif difficulty == "hard":
        grid_size = 50
    cell_size = WIDTH // grid_size
    game_loop()

def main_menu():
    running = True
    while running:
        draw_gradient_background(GRADIENT_TOP, GRADIENT_BOTTOM)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        title_text = font.render("Conway's Game of Life", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(WIDTH / 2, 100))
        screen.blit(title_text, title_rect)

        draw_button("Easy", WIDTH / 2 - 150, 250, 300, 50, mouse_pos, lambda: set_difficulty("easy"))
        draw_button("Medium", WIDTH / 2 - 150, 350, 300, 50, mouse_pos, lambda: set_difficulty("medium"))
        draw_button("Hard", WIDTH / 2 - 150, 450, 300, 50, mouse_pos, lambda: set_difficulty("hard"))
        pygame.display.flip()

def game_loop():
    global grid, grid_size, cell_size, grid_history
    grid = np.zeros((grid_size, grid_size))
    running = True
    paused = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    running = False
                if event.key == pygame.K_UP and paused:
                    grid = update_grid(grid)
                    grid_history.append(grid.copy())
                if event.key == pygame.K_DOWN and paused and grid_history:
                    grid = grid_history.pop()
                if event.key == pygame.K_RETURN and paused and grid_history:
                    clear_grid()

            if pygame.mouse.get_pressed()[0]:
                click.play()
                x, y = pygame.mouse.get_pos()
                x_cell, y_cell = x // cell_size, y // cell_size
                if x_cell < grid_size and y_cell < grid_size:
                    grid[x_cell, y_cell] = not grid[x_cell, y_cell]
                    if paused:
                        grid_history.append(grid.copy())

        screen.fill(BG_COLOR)

        for i in range(grid_size):
            for j in range(grid_size):
                rect = pygame.Rect(i * cell_size, j * cell_size, cell_size, cell_size)
                color = ALIVE_COLOR if grid[i, j] == 1 else DEAD_COLOR
                pygame.draw.rect(screen, color, rect)

        if not paused and running:
            grid = update_grid(grid)
            grid_history.append(grid.copy())
        draw_grid()
        pygame.display.flip()

main_menu()
pygame.quit()
sys.exit()
