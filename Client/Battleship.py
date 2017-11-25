'''Main game runner'''
import pygame
from pygame.locals import *

REGULAR = 10
LARGE = 25
HUGE = 50

WIDTH = 30
HEIGHT = 30
MARGIN = 5
BOARD_BUFFER = 30
WINDOW_SIZE = [1280, 960]

READY_BUTTON = (400, 340, 100, 60)
READY_BUTTON_TEXT = (400, 355)

BLUE = (0, 128, 225)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (72, 72, 72)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

def main():
    '''Main game initialization, loop, and close'''
    pygame.init()
    pygame.font.init()
    game_font = pygame.font.SysFont('Arial', 30)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    done = False
    ready = False
    clock = pygame.time.Clock()
    board = Board(REGULAR)
    pygame.draw.rect(screen, GREEN, READY_BUTTON)
    ready_surface = game_font.render('READY', False, BLACK)
    screen.blit(ready_surface, READY_BUTTON_TEXT)
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                if not ready:
                    col = position[0]
                    row = position[1]
                    if col >= 400 and col <= 500 and row >= 340 and row <= 400:
                        ready = True
                        pygame.draw.rect(screen, BLACK, READY_BUTTON)
                    board.update(position, 3)
                else:
                    board.update(position, 1)
        board.draw(screen)
        clock.tick(60)
        pygame.display.flip()
    pygame.quit()

class Board(object):
    '''Board class handles board details'''
    def __init__(self, size):
        self.size = size
        self.target_grid = [[0 for x in range(size)] for y in range(size)]
        self.local_grid = [[0 for x in range(size)] for y in range(size)]

    def draw(self, screen):
        '''draws current state of board'''
        local_grid_location = (MARGIN*self.size)+1 +(HEIGHT*self.size) + BOARD_BUFFER
        #set up upper "viewport" board
        for row in range(self.size):
            for column in range(self.size):
                #Blue is standard board color (water)
                tile_color = BLUE
                #Grid entry 1 for miss
                if self.target_grid[row][column] == 1:
                    tile_color = WHITE
                #Grid entry 2 for hit
                elif self.target_grid[row][column] == 2:
                    tile_color = RED
                pygame.draw.rect(screen, tile_color, [(MARGIN + WIDTH) * column + MARGIN, \
                    (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])

        #set up lower local "positioning" board
        for row in range(self.size):
            for column in range(self.size):
                #Blue is standard board color (water)
                tile_color = BLUE
                #Grid entry 1 for miss
                if self.local_grid[row][column] == 1:
                    tile_color = WHITE
                #Grid entry 2 for hit
                elif self.local_grid[row][column] == 2:
                    tile_color = RED
                #Grid entry 3 for ship placement
                elif self.local_grid[row][column] == 3:
                    tile_color = GRAY
                pygame.draw.rect(screen, tile_color, [(MARGIN + WIDTH) * column + MARGIN, \
                    (MARGIN + HEIGHT) * row + MARGIN + local_grid_location, WIDTH, HEIGHT])


    def update(self, pos, value):
        '''Updates client board to display server information'''
        column = pos[0] // (WIDTH + MARGIN)
        row = pos[1] // (HEIGHT + MARGIN)
        print("Click ", pos, "Grid Coordinates: ", row, column)
        if value == 3:
            if row > self.size and not column > self.size-1 and not row > (self.size * 2):
                self.local_grid[row-(self.size+1)][column] = value
        #Checks that positioning is within grid bounds
        if not row > self.size-1 and not column > self.size-1:
            self.target_grid[row][column] = value


class Player(object):
    def __init__(self, player_num, name, comp, size):
        self.player_num = player_num
        self.name = name
        self.comp = comp
        self.positioning = [[0 for x in range(size)] for y in range(size)]

    #def attack(self, receive_player_num, x, y):


if __name__ == '__main__':
    main()
