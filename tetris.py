import pygame
import random


ROWS, COLS = 20, 10
BLOCK_SIZE = 30
WIDTH, HEIGHT = COLS * BLOCK_SIZE, ROWS * BLOCK_SIZE
FPS = 60


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

# === Spielfeld erstellen ===
def create_grid():
    return [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

# === Hauptfunktion ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    grid = create_grid()
    piece = Tetromino()
    running = True

    while running:
        clock.tick(FPS)
        screen.fill(GRAY)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Zeichne Grid
        for i in range(ROWS):
            for j in range(COLS):
                pygame.draw.rect(screen, grid[i][j],
                    (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(screen, GRAY,
                    (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        # Zeichne Tetromino
        piece.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()