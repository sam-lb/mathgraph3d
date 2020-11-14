import pygame;
from random import randint;

screen = pygame.display.set_mode((500, 500));
pygame.display.set_caption("marching squares");

A = (0, 1);
B = (1, 2);
C = (2, 3);
D = (0, 3);

table = {
    0:  (),
    1:  ((A, D),),
    2:  ((A, B),),
    3:  ((D, B),),
    4:  ((B, C),),
    5:  ((A, B), (C, D)),
    6:  ((A, C),),
    7:  ((C, D),),
    8:  ((C, D),),
    9:  ((A, C),),
    10: ((A, D), (B, C)),
    11: ((B, C),),
    12: ((B, D),),
    13: ((A, B),),
    14: ((A, D),),
    15: (),
};

sc = 25;
n, m = 20, 20;
rad=5;

def random_grid(n, m):
    return [[randint(0, 1) for j in range(m)] for i in range(n)];

def midpoint(A, B):
    return (A[0] + B[0]) / 2, (A[1] + B[1]) / 2;

def draw_grid(grid):
    x = 10;
    y = 10;
    for row in grid:
        for point in row:
            pygame.draw.circle(screen, (0, 0, 0), (x, y), rad, not point);
            y += sc;
        x += sc;
        y = 10;

def create_polygonization(grid):
    a = lambda i, j: (10 + i * sc, 10 + j * sc);
    for i, row in enumerate(grid[1:], start=1):
        for j in range(1, len(row)):
            #verts 
            cell = grid[i-1][j-1], grid[i][j-1], grid[i][j], grid[i-1][j];
            code = int("".join(map(str, cell)), 2);
            cell = a(i-1,j), a(i,j), a(i,j-1), a(i-1,j-1);
            for line in table[code]:
                m1 = midpoint(cell[line[0][0]], cell[line[0][1]]);
                m2 = midpoint(cell[line[1][0]], cell[line[1][1]]);
                pygame.draw.line(screen, (255, 0, 0), m1, m2, 3);
            #pygame.draw.rect(screen, (0, 0, 255), (i*sc-sc+10, j*sc-sc+10, sc, sc), 1);
            pygame.display.update();
            pygame.time.delay(60);
        #pygame.event.get();
grid = random_grid(n,m);
#create_polygonization(grid);

clock = pygame.time.Clock();
running = True;
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False;
            break;
        elif event.type == pygame.KEYDOWN:
            pass;
    if not running: break;

    screen.fill((255, 255, 255));
    draw_grid(grid);
    create_polygonization(grid);
    grid = random_grid(n, m);
    pygame.display.update();
    clock.tick(30);
pygame.quit();
