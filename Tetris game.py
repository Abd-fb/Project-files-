import pygame
import random
import time
import os

pygame.init()

WIDTH, HEIGHT = 400, 600
SIDEBAR = 240
screen = pygame.display.set_mode((WIDTH + SIDEBAR, HEIGHT))
pygame.display.set_caption("Tetris Pro")
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("verdana", 42, bold=True)
FONT = pygame.font.SysFont("verdana", 20)
SMALL = pygame.font.SysFont("verdana", 14)

BG = (15, 18, 30)
GRID = (40, 45, 70)
WHITE = (255,255,255)
ACCENT = (0,200,255)

GRID_SIZE = 30
COLUMNS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

SHAPES = [
    [[1,1,1,1]],
    [[1,1],[1,1]],
    [[0,1,0],[1,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]],
    [[0,1,1],[1,1,0]],
    [[1,1,0],[0,1,1]]
]

COLORS = [
    (0,255,255),(255,255,0),(160,32,240),
    (0,0,255),(255,165,0),(0,255,0),(255,0,0)
]

class Piece:
    def __init__(self):
        i = random.randrange(len(SHAPES))
        self.shape = SHAPES[i]
        self.color = COLORS[i]
        self.x = COLUMNS//2 - len(self.shape[0])//2
        self.y = 0

    def get_cells(self):
        positions = []
        for i,row in enumerate(self.shape):
            for j,val in enumerate(row):
                if val:
                    positions.append((self.x+j, self.y+i))
        return positions

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


def valid(piece, locked):
    for x,y in piece.get_cells():
        if x < 0 or x >= COLUMNS or y >= ROWS:
            return False
        if (x,y) in locked:
            return False
    return True


def draw_cell(x,y,color):
    rect = (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, GRID, rect, 2, border_radius=6)


def clear_rows(locked):
    full_rows = []
    for y in range(ROWS):
        if all((x,y) in locked for x in range(COLUMNS)):
            full_rows.append(y)

    for y in full_rows:
        for x in range(COLUMNS):
            locked.pop((x,y), None)

    for (x,y) in sorted(list(locked.keys()), key=lambda k:k[1])[::-1]:
        shift = sum(1 for r in full_rows if y < r)
        if shift:
            locked[(x,y+shift)] = locked.pop((x,y))

    return len(full_rows)


def draw_sidebar(score, time_left, best, mode):
    pygame.draw.rect(screen, (25,30,50), (WIDTH,0,SIDEBAR,HEIGHT))

    screen.blit(TITLE_FONT.render("TETRIS", True, ACCENT), (WIDTH+30,30))

    pygame.draw.rect(screen,(35,40,70),(WIDTH+20,120,200,120),border_radius=10)
    screen.blit(FONT.render(f"Score: {score}",True,WHITE),(WIDTH+30,140))
    screen.blit(FONT.render(f"Best: {best}",True,WHITE),(WIDTH+30,170))

    if mode=="Time":
        screen.blit(FONT.render(f"Time: {int(time_left)}",True,WHITE),(WIDTH+30,200))


def game_over(score):
    while True:
        screen.fill(BG)
        t1 = TITLE_FONT.render("GAME OVER", True, WHITE)
        t2 = FONT.render(f"Score: {score}", True, WHITE)
        t3 = FONT.render("Click to continue", True, WHITE)

        screen.blit(t1,(WIDTH//2-140,200))
        screen.blit(t2,(WIDTH//2-60,260))
        screen.blit(t3,(WIDTH//2-100,320))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); return
            if e.type==pygame.MOUSEBUTTONDOWN:
                return


def main(mode):
    locked = {}
    piece = Piece()
    fall = 0
    speed = 0.4
    score = 0

    start = time.time()
    total_time = 60

    best = 0
    if os.path.exists("highscore.txt"):
        best = int(open("highscore.txt").read())

    running = True
    while running:
        fall += clock.get_rawtime()
        clock.tick()

        if mode == "Time":
            time_left = total_time - (time.time() - start)
            if time_left <= 0:
                break
        else:
            time_left = 0

        # MOVE DOWN
        if fall/1000 > speed:
            fall = 0
            piece.y += 1

            if not valid(piece, locked):
                piece.y -= 1

                # LOCK piece EXACTLY where valid
                for pos in piece.get_cells():
                    locked[pos] = piece.color

                piece = Piece()

                # GAME OVER if new piece invalid
                if not valid(piece, locked):
                    break

                score += 10

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); return

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    piece.x -= 1
                    if not valid(piece, locked): piece.x += 1
                if e.key == pygame.K_RIGHT:
                    piece.x += 1
                    if not valid(piece, locked): piece.x -= 1
                if e.key == pygame.K_DOWN:
                    piece.y += 1
                    if not valid(piece, locked): piece.y -= 1
                if e.key == pygame.K_UP:
                    old = piece.shape
                    piece.rotate()
                    if not valid(piece, locked): piece.shape = old

        screen.fill(BG)

        # DRAW locked blocks
        for (x,y),color in locked.items():
            draw_cell(x,y,color)

        # DRAW current piece
        for x,y in piece.get_cells():
            draw_cell(x,y,piece.color)

        # CLEAR
        score += clear_rows(locked)*20

        draw_sidebar(score, time_left, best, mode)
        pygame.display.update()

    if score > best:
        open("highscore.txt","w").write(str(score))

    game_over(score)


def button(text,y,mouse):
    rect = pygame.Rect(WIDTH//2-140,y,280,60)
    color = (60,70,120) if rect.collidepoint(mouse) else (40,50,90)
    pygame.draw.rect(screen,color,rect,border_radius=12)
    txt = FONT.render(text,True,WHITE)
    screen.blit(txt,(rect.x+40,rect.y+18))
    return rect


def menu():
    while True:
        screen.fill(BG)
        mouse = pygame.mouse.get_pos()

        title = TITLE_FONT.render("TETRIS PRO", True, ACCENT)
        screen.blit(title,(WIDTH//2-160,120))

        b1 = button("Time Attack (60s)",260,mouse)
        b2 = button("Free Mode",340,mouse)

        pygame.display.update()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); return
            if e.type==pygame.MOUSEBUTTONDOWN:
                if b1.collidepoint(e.pos): main("Time")
                if b2.collidepoint(e.pos): main("Free")


if __name__ == "__main__":
    menu()