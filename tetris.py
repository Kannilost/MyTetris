import pygame
import random


ROWS, COLS = 20, 10
BLOCK_SIZE = 30
WIDTH, HEIGHT = COLS * BLOCK_SIZE, ROWS * BLOCK_SIZE
FPS = 60
PREVIEW_SIZE = 15  # Vorschau-Blockgröße in Pixeln

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [(0, 255, 255), (255, 255, 0), (128, 0, 128),
          (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0)]


SHAPES = [
    [[1, 1, 1, 1]],  # I

    [[1, 1],
     [1, 1]],        # O

    [[0, 1, 0],
     [1, 1, 1]],     # T

    [[0, 1, 1],
     [1, 1, 0]],     # S

    [[1, 1, 0],
     [0, 1, 1]],     # Z

    [[1, 0, 0],
     [1, 1, 1]],     # J

    [[0, 0, 1],
     [1, 1, 1]]      # L
]


class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def draw(self, surface):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(surface, self.color,
                        ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    
    def rotate(self):
        rotated = list(zip(*self.shape[::-1]))
        self.shape = [list(row) for row in rotated]

class Button:
    def __init__(self, x, y, width, height, text, font, bg_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = font.render(text, True, text_color)
        self.bg_color = bg_color
        self.text_color = text_color
        self.text_pos = (
            x + (width - self.text.get_width()) // 2,
            y + (height - self.text.get_height()) // 2
        )

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
        surface.blit(self.text, self.text_pos)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, start_val, font):
        self.rect = pygame.Rect(x, y, width, 10)
        self.knob_radius = 10
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.font = font
        self.dragging = False

    def draw(self, surface):
        # Balken
        pygame.draw.rect(surface, WHITE, self.rect)
        # Knopf
        knob_x = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        pygame.draw.circle(surface, (0, 128, 255), (knob_x, self.rect.y + 5), self.knob_radius)
        # Text
        label = self.font.render(f"Start-Level: {self.value}", True, WHITE)
        surface.blit(label, (self.rect.x, self.rect.y - 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(self.rect.x, self.rect.y - self.knob_radius, self.rect.width, self.knob_radius * 3).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            ratio = (rel_x - self.rect.x) / self.rect.width
            self.value = int(self.min_val + ratio * (self.max_val - self.min_val))

def calculate_fall_speed(level, base_speed):
    return max(0.1, base_speed * (1 - 0.05 * (level - 1)))

def valid_position(shape, x, y, grid):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                new_x = x + j
                new_y = y + i
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                if grid[new_y][new_x] != BLACK:
                    return False
    return True

def clear_rows(grid):
    cleared = 0
    new_grid = []

    for row in grid:
        if BLACK not in row:
            cleared += 1
        else:
            new_grid.append(row)

    for _ in range(cleared):
        new_grid.insert(0, [BLACK for _ in range(COLS)])

    return new_grid, cleared

def calculate_score(lines, level):
    if lines == 0:
        return 0

    base = 100
    combo_score = 0
    for i in range(lines):
        combo_score += base * (2 ** i)

    multiplier = 1 + 0.05 * (level - 1)
    return int(combo_score * multiplier)

def get_highest_block_y(grid):
    for y in range(ROWS):  # von oben nach unten
        for x in range(COLS):
            if grid[y][x] != BLACK:
                return y
    return ROWS  # kein Block gefunden

# === Spielfeld erstellen ===
def create_grid():
    return [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

def draw_hover_effect(button, surface, mouse_pos):
    if button.rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, (0, 180, 255), button.rect, border_radius=10)  # heller Blau
    else:
        pygame.draw.rect(surface, button.bg_color, button.rect, border_radius=10)
    surface.blit(button.text, button.text_pos)

def show_homescreen(screen, font):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.3)  # Leiser Einstieg
    pygame.mixer.music.load("sounds/Homepage.mp3")
    pygame.mixer.music.play(-1, fade_ms=2000)  # Sanftes Einblenden

    background = pygame.image.load("images/home_bg.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 60, 150, 50, "Spiel starten", font,
                    bg_color=(0, 128, 255), text_color=WHITE)
    slider = Slider(WIDTH // 2 - 100, HEIGHT // 2, 200, 1, 10, 1, font)

    title = font.render("TETRIS by Kanni", True, WHITE)
    title_pos = (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120)

    while True:
        screen.blit(background, (0, 0))  # ✅ Zeigt das Bild als Hintergrund
        screen.blit(title, title_pos)
        slider.draw(screen)
        button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            slider.handle_event(event)
            if button.is_clicked(event):
                return slider.value  # Übergibt das gewählte Level

# === Hauptfunktion ===
def main():
    pygame.init()
    font = pygame.font.SysFont("Arial", 32)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    start_level = show_homescreen(screen, font)
    level = start_level
    base_speed = 0.5
    fall_speed = calculate_fall_speed(level, base_speed)
    paused = False
    pygame.mixer.init()
    pygame.mixer.music.load("sounds/itseasy.mp3")
    pygame.mixer.music.play(-1)  # Dauerschleife
    current_music = "normal"
    move_delay = 0.1  # Sekunden zwischen Bewegungen
    initial_delay = 0.2      # Wartezeit bevor Wiederholung startet
    hold_time = 0            # Wie lange Taste gedrückt ist
    key_held = None          # Welche Taste wird gehalten
    piece = Tetromino()
    next_piece = Tetromino()
    score = 0
    lines_cleared_total = 0
    pygame.init()
    font = pygame.font.SysFont("Arial", 24)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    grid = create_grid()
    fall_time = 0
    running = True

    if not valid_position(piece.shape, piece.x, piece.y, grid):
        running = False

    while running:
        clock.tick(FPS)
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.load("sounds/options.mp3")
                        pygame.mixer.music.play(-1)
                    else:
                        highest_y = get_highest_block_y(grid)
                        if highest_y <= 5:
                            pygame.mixer.music.load("sounds/dontloose.mp3")
                            current_music = "danger"
                        else:
                            pygame.mixer.music.load("sounds/itseasy.mp3")
                            current_music = "normal"
                        pygame.mixer.music.play(-1)
                
                if not paused:
                    if event.key == pygame.K_UP:
                        original_shape = piece.shape
                        piece.rotate()
                        if not valid_position(piece.shape, piece.x, piece.y, grid):
                            piece.shape = original_shape
                    elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN]:
                        key_held = event.key
                        hold_time = 0  # Reset beim ersten Drücken

                        # Sofortige Bewegung
                        if event.key == pygame.K_LEFT and valid_position(piece.shape, piece.x - 1, piece.y, grid):
                            piece.x -= 1
                        elif event.key == pygame.K_RIGHT and valid_position(piece.shape, piece.x + 1, piece.y, grid):
                            piece.x += 1
                        elif event.key == pygame.K_DOWN and valid_position(piece.shape, piece.x, piece.y + 1, grid):
                            piece.y += 1
                            score += 1

            elif event.type == pygame.KEYUP:
                if event.key == key_held:
                    key_held = None
                    hold_time = 0

        if paused:
            screen.fill(GRAY)
            pause_text = font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH // 2 - 40, HEIGHT // 2 - 20))
            pygame.display.flip()
            continue  # überspringt den Rest der Schleife


        if key_held and not paused:
            hold_time += clock.get_time() / 1000

            if hold_time >= initial_delay:
                if key_held == pygame.K_LEFT and valid_position(piece.shape, piece.x - 1, piece.y, grid):
                    piece.x -= 1
                elif key_held == pygame.K_RIGHT and valid_position(piece.shape, piece.x + 1, piece.y, grid):
                    piece.x += 1
                elif key_held == pygame.K_DOWN and valid_position(piece.shape, piece.x, piece.y + 1, grid):
                    piece.y += 1
                    score += 1
                pygame.time.wait(int(move_delay * 1000))  # kleine Pause für Wiederholung

        if not paused:
            fall_time += clock.get_time() / 1000  # ms → Sekunden

            if fall_time >= fall_speed:
                if valid_position(piece.shape, piece.x, piece.y + 1, grid):
                    piece.y += 1
                else:
                    # Tetromino ins Grid einfügen
                    for i, row in enumerate(piece.shape):
                        for j, cell in enumerate(row):
                            if cell:
                                grid[piece.y + i][piece.x + j] = piece.color
                
                    # Zeilen löschen und Punkte zählen
                    grid, cleared = clear_rows(grid)
                    score += calculate_score(cleared, level)

                    lines_cleared_total += cleared
                    level = lines_cleared_total // 10 + start_level
                    fall_speed = calculate_fall_speed(level, base_speed)

                    if cleared > 0:
                        pygame.mixer.Sound("sounds/clear.mp3").play()

                    highest_y = get_highest_block_y(grid)

                    # 🎵 Musikwechsel nur bei hohem Einrasten
                    if highest_y<= 5 and current_music != "danger":
                        pygame.mixer.music.load("sounds/dontloose.mp3")
                        pygame.mixer.music.play(-1)
                        current_music = "danger"

                    elif highest_y > 5 and current_music != "normal":
                        pygame.mixer.music.load("sounds/itseasy.mp3")
                        pygame.mixer.music.play(-1)
                        current_music = "normal"

                    # Neues Tetromino erzeugen
                    piece = next_piece
                    next_piece = Tetromino()

                    # Spielende prüfen
                    if not valid_position(piece.shape, piece.x, piece.y, grid):
                        running = False
                fall_time = 0

        # Zeichne Grid
        for i in range(ROWS):
            for j in range(COLS):
                pygame.draw.rect(screen, grid[i][j],
                    (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(screen, GRAY,
                    (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        # Zeichne Tetromino
        next_text = font.render("Next:", True, WHITE)
        screen.blit(next_text, (WIDTH - 120, 10))

        for i, row in enumerate(next_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, next_piece.color,
                        (WIDTH - 100 + j * PREVIEW_SIZE, 40 + i * PREVIEW_SIZE, PREVIEW_SIZE, PREVIEW_SIZE))
        piece.draw(screen)

        # Zeichne Punktestand
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (10, 40))

        pygame.display.flip()

    pygame.mixer.music.load("sounds/loser.mp3")
    pygame.mixer.music.play()

    screen.fill(GRAY)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, BLACK)
    screen.blit(game_over_text, (WIDTH // 2 - 60, HEIGHT // 2 - 30))
    screen.blit(score_text, (WIDTH // 2 - 70, HEIGHT // 2 + 10))
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    main()