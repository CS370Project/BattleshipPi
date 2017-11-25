'''Main game runner'''
import pygame
from pygame.locals import *

REGULAR = 10
LARGE = 25
HUGE = 50

WIDTH = 30
HEIGHT = 30
MARGIN = 5
BOARD_BUFFER = 20
WINDOW_SIZE = [1280, 960]

BLUE = (0, 128, 225)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (169, 169, 169)

def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    done = False
    clock = pygame.time.Clock()
    board = Board(REGULAR)
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
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
                pygame.draw.rect(screen, tile_color, [(MARGIN + WIDTH) * column + MARGIN, (MARGIN + HEIGHT) * \
                    row + MARGIN, WIDTH, HEIGHT])

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
                pygame.draw.rect(screen, tile_color, [(MARGIN + WIDTH) * column + MARGIN, (MARGIN + HEIGHT) \
                    * row + MARGIN + local_grid_location, WIDTH, HEIGHT])


    def update(self, pos, value):
        '''Updates client board to display server information'''
        column = pos[0] // (WIDTH + MARGIN)
        row = pos[1] // (HEIGHT + MARGIN)
        #Checks that positioning is within grid bounds
        if not row > 9 and not column > 9:
            self.target_grid[row][column] = value
        print("Click ", pos, "Grid Coordinates: ", row, column)


class Player(object):
    def __init__(self, player_num, name, comp, size):
        self.player_num = player_num
        self.name = name
        self.comp = comp
        self.positioning = [[0 for x in range(size)] for y in range(size)]

    #def attack(self, receive_player_num, x, y):


if __name__ == '__main__':
    main()
