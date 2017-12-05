'''Main game runner'''
import sys
import socket
import threading
import json
import base64
import pygame
import struct
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

CARRIER_BUTTON = (400, 410, 100, 60)
CARRIER_BUTTON_TEXT = (400, 425)
BATTLESHIP_BUTTON = (400, 480, 100, 60)
BATTLESHIP_BUTTON_TEXT = (400, 495)
CRUISER_BUTTON = (400, 550, 100, 60)
CRUISER_BUTTON_TEXT = (400, 565)
DESTROYER_BUTTON = (400, 620, 100, 60)
DESTROYER_BUTTON_TEXT = (400, 635)

MESSENGER = (540, 5, 735, 950)

DIRECTION_TIP = (5, 760, 345, 60)
DIRECTION_TIP_TEXT = (5, 765)
DIRECTION_TEXT = (5, 785)

BLUE = (0, 128, 225)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (72, 72, 72)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

CARRIER_COUNT = 1
BATTLESHIP_COUNT = 1
CRUISER_COUNT = 2
DESTROYER_COUNT = 1

CARRIER_SIZE = 5
BATTLESHIP_SIZE = 4
CRUISER_SIZE = 3
DESTROYER_SIZE = 2

GRID_COORD = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J'}

def draw_messanger(screen, message):
    '''Draw message area with current set text'''
    game_font = pygame.font.SysFont('Arial', 20)
    pygame.draw.rect(screen, WHITE, MESSENGER)
    message_size = 0
    for i in message:
        messenger_surface = game_font.render(i, False, BLACK)
        screen.blit(messenger_surface, (545, 10 + (message_size * 20)))
        message_size += 1

def draw_placement(screen, direction):
    '''Draw direction tip'''
    game_font = pygame.font.SysFont('Arial', 30)
    tip_font = pygame.font.SysFont('Arial', 12)
    pygame.draw.rect(screen, WHITE, DIRECTION_TIP)
    direction_surface = game_font.render(direction, False, BLACK)
    direction_tip_surface = tip_font.render('Press DOWN or RIGHT arrows to change ship direction:', False, BLACK)
    screen.blit(direction_surface, DIRECTION_TEXT)
    screen.blit(direction_tip_surface, DIRECTION_TIP_TEXT)

# Credit to: Adam Rosenfield on stack overflow
# https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def main(host, port, username):
    '''Main game initialization, loop, and close'''
    pygame.init()
    pygame.font.init()
    game_font = pygame.font.SysFont('Arial', 30)
    ship_font = pygame.font.SysFont('Arial', 16)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    done = False
    ready = False
    turn = False
    vertical = False
    carrier_place = False
    battleship_place = False
    cruiser_place = False
    destroyer_place = False
    ship_collection = []
    ship_id = 0
    message = ['Welcome to BATTLESHIP!']
    clock = pygame.time.Clock()
    board = Board(REGULAR)

    def printSocketRec (sockname, connection, stopEvent):
        nonlocal message
        while True:
            if stopEvent.is_set():
                break
            msg = recv_msg(connection).decode('utf-8')
            print(msg)
            for line in msg.splitlines():
                message.append('{}: {}'.format(sockname, line))
        connection.close()
    
    # Create server connection
    connection_stop = threading.Event()
    connection = socket.socket()
    connection_thread = threading.Thread(target=printSocketRec, args=(username, connection, connection_stop))
    connection.settimeout(1000)
    connection.connect((host, int(port)))
    connection_thread.start()
    #msg = connection.recv(140).decode("utf-8")
    #message.append(msg)
    

    # Create GUI buttons for placement and ready
    pygame.draw.rect(screen, GREEN, READY_BUTTON)
    ready_surface = game_font.render('READY', False, BLACK)
    screen.blit(ready_surface, READY_BUTTON_TEXT)

    pygame.draw.rect(screen, BLUE, CARRIER_BUTTON)
    carrier_surface = ship_font.render('Carrier', False, BLACK)
    screen.blit(carrier_surface, CARRIER_BUTTON_TEXT)
    carrier_ready = CARRIER_COUNT

    pygame.draw.rect(screen, BLUE, BATTLESHIP_BUTTON)
    battleship_surface = ship_font.render('Battleship', False, BLACK)
    screen.blit(battleship_surface, BATTLESHIP_BUTTON_TEXT)
    battleship_ready = BATTLESHIP_COUNT

    pygame.draw.rect(screen, BLUE, CRUISER_BUTTON)
    cruiser_surface = ship_font.render('Cruiser', False, BLACK)
    screen.blit(cruiser_surface, CRUISER_BUTTON_TEXT)
    cruiser_ready = CRUISER_COUNT

    pygame.draw.rect(screen, BLUE, DESTROYER_BUTTON)
    destroyer_surface = ship_font.render('Destroyer', False, BLACK)
    screen.blit(destroyer_surface, DESTROYER_BUTTON_TEXT)
    destroyer_ready = DESTROYER_COUNT

    while not done:
        if len(message) > 47:
            del message[0]
        if len(message) > 2:
            if len(message[-2]) > 18:
                if message[-1][-11:] == "make a move" or message[-1][-18] == "try somewhere else":
                    turn = True
                else:
                    turn = False
            if len(message[-2]) > 16:
                if message[-2][:16] == "Your opponent hit":
                    board.hit(int(message[-2][-5]),int(message[-2][-2]))
        draw_messanger(screen, message)
        if vertical:
            draw_placement(screen, 'Vertical')
        else:
            draw_placement(screen, 'Horizontal')

        for event in pygame.event.get():
            # Change ship placement direction. Only down and right arrows
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    vertical = True
                elif event.key == pygame.K_RIGHT:
                    vertical = False

            # Check for player quiting the game
            if event.type == pygame.QUIT:
                done = True

            # Check for button selection
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                col = position[0]
                row = position[1]
                grid_x = col // (WIDTH + MARGIN)
                grid_y = row // (HEIGHT + MARGIN)
                if not ready:
                    if col >= 400 and col <= 500 and row >= 340 and row <= 400:
                        if carrier_ready == 0 and battleship_ready == 0 and cruiser_ready == 0 \
                            and destroyer_ready == 0:
                            #Send player board for verification
                            
                            board_send = json.dumps([ship.__dict__ for ship in ship_collection]).encode()
                            connection.sendall(board_send)
                            ready = True
                            pygame.draw.rect(screen, BLACK, READY_BUTTON)

                    # Select Carrier to place
                    elif col >= 400 and col <= 500 and row >= 410 and row <= 470:
                        carrier_place = True
                        battleship_place = False
                        cruiser_place = False
                        destroyer_place = False
                        if carrier_ready > 0:
                            pygame.draw.rect(screen, WHITE, CARRIER_BUTTON)
                            screen.blit(carrier_surface, CARRIER_BUTTON_TEXT)
                        if battleship_ready > 0:
                            pygame.draw.rect(screen, BLUE, BATTLESHIP_BUTTON)
                            screen.blit(battleship_surface, BATTLESHIP_BUTTON_TEXT)
                        if cruiser_ready > 0:
                            pygame.draw.rect(screen, BLUE, CRUISER_BUTTON)
                            screen.blit(cruiser_surface, CRUISER_BUTTON_TEXT)
                        if destroyer_ready > 0:
                            pygame.draw.rect(screen, BLUE, DESTROYER_BUTTON)
                            screen.blit(destroyer_surface, DESTROYER_BUTTON_TEXT)
                    # Select Battleship to place
                    elif col >= 400 and col <= 500 and row >= 480 and row <= 540:
                        carrier_place = False
                        battleship_place = True
                        cruiser_place = False
                        destroyer_place = False
                        if carrier_ready > 0:
                            pygame.draw.rect(screen, BLUE, CARRIER_BUTTON)
                            screen.blit(carrier_surface, CARRIER_BUTTON_TEXT)
                        if battleship_ready > 0:
                            pygame.draw.rect(screen, WHITE, BATTLESHIP_BUTTON)
                            screen.blit(battleship_surface, BATTLESHIP_BUTTON_TEXT)
                        if cruiser_ready > 0:
                            pygame.draw.rect(screen, BLUE, CRUISER_BUTTON)
                            screen.blit(cruiser_surface, CRUISER_BUTTON_TEXT)
                        if destroyer_ready > 0:
                            pygame.draw.rect(screen, BLUE, DESTROYER_BUTTON)
                            screen.blit(destroyer_surface, DESTROYER_BUTTON_TEXT)
                    # Select Cruiser to place
                    elif col >= 400 and col <= 500 and row >= 550 and row <= 610:
                        carrier_place = False
                        battleship_place = False
                        cruiser_place = True
                        destroyer_place = False
                        if carrier_ready > 0:
                            pygame.draw.rect(screen, BLUE, CARRIER_BUTTON)
                            screen.blit(carrier_surface, CARRIER_BUTTON_TEXT)
                        if battleship_ready > 0:
                            pygame.draw.rect(screen, BLUE, BATTLESHIP_BUTTON)
                            screen.blit(battleship_surface, BATTLESHIP_BUTTON_TEXT)
                        if cruiser_ready > 0:
                            pygame.draw.rect(screen, WHITE, CRUISER_BUTTON)
                            screen.blit(cruiser_surface, CRUISER_BUTTON_TEXT)
                        if destroyer_ready > 0:
                            pygame.draw.rect(screen, BLUE, DESTROYER_BUTTON)
                            screen.blit(destroyer_surface, DESTROYER_BUTTON_TEXT)
                    # Select Destroyer to place
                    elif col >= 400 and col <= 500 and row >= 620 and row <= 680:
                        carrier_place = False
                        battleship_place = False
                        cruiser_place = False
                        destroyer_place = True
                        if carrier_ready > 0:
                            pygame.draw.rect(screen, BLUE, CARRIER_BUTTON)
                            screen.blit(carrier_surface, CARRIER_BUTTON_TEXT)
                        if battleship_ready > 0:
                            pygame.draw.rect(screen, BLUE, BATTLESHIP_BUTTON)
                            screen.blit(battleship_surface, BATTLESHIP_BUTTON_TEXT)
                        if cruiser_ready > 0:
                            pygame.draw.rect(screen, BLUE, CRUISER_BUTTON)
                            screen.blit(cruiser_surface, CRUISER_BUTTON_TEXT)
                        if destroyer_ready > 0:
                            pygame.draw.rect(screen, WHITE, DESTROYER_BUTTON)
                            screen.blit(destroyer_surface, DESTROYER_BUTTON_TEXT)

                    if carrier_place:
                        if carrier_ready > 0:
                            if vertical:
                                if grid_x >= 0 and grid_x <= 9 and grid_y >= 11 \
                                    and grid_y + CARRIER_SIZE-1 <= 20:
                                    if not board.ship_present(grid_x, grid_y, CARRIER_SIZE, vertical):
                                        coord = []
                                        for i in range(CARRIER_SIZE):
                                            board.update(grid_x, grid_y + i, 3)
                                            coord.append([grid_x, grid_y + i - 11])
                                        ship = Ship(coord, CARRIER_SIZE, CARRIER_SIZE, 'Carrier', ship_id)
                                        ship_id += 1
                                        ship_collection.append(ship)
                                        carrier_ready-=1
                            else:
                                if grid_x >= 0 and grid_x + CARRIER_SIZE-1 <= 9 \
                                    and grid_y >= 11 and grid_y <= 20:
                                    if not board.ship_present(grid_x, grid_y, CARRIER_SIZE, vertical):
                                        coord = []
                                        for i in range(CARRIER_SIZE):
                                            board.update(grid_x + i, grid_y, 3)
                                            coord.append([grid_x + i, grid_y - 11])
                                        ship = Ship(coord, CARRIER_SIZE, CARRIER_SIZE, 'Carrier', ship_id)
                                        ship_id += 1
                                        ship_collection.append(ship)
                                        carrier_ready-=1
                            if carrier_ready == 0:
                                pygame.draw.rect(screen, BLACK, CARRIER_BUTTON)
                    if battleship_place:
                        if battleship_ready > 0:
                            if vertical:
                                if grid_x >= 0 and grid_x <= 9 and grid_y >= 11 \
                                    and grid_y + BATTLESHIP_SIZE-1 <= 20:
                                    if not board.ship_present(grid_x, grid_y, BATTLESHIP_SIZE, vertical):
                                        coord = []
                                        for i in range(BATTLESHIP_SIZE):
                                            board.update(grid_x, grid_y + i, 3)
                                            coord.append([grid_x, grid_y + i - 11])
                                        ship = Ship(coord, BATTLESHIP_SIZE, BATTLESHIP_SIZE, 'Battleship', ship_id)
                                        ship_id += 1
                                        ship_collection.append(ship)
                                        battleship_ready-=1
                            else:
                                if grid_x >= 0 and grid_x + BATTLESHIP_SIZE-1 <= 9 \
                                    and grid_y >= 11 and grid_y <= 20:
                                    if not board.ship_present(grid_x, grid_y, BATTLESHIP_SIZE, vertical):
                                        coord = []
                                        for i in range(BATTLESHIP_SIZE):
                                            board.update(grid_x + i, grid_y, 3)
                                            coord.append([grid_x + i, grid_y - 11])
                                        ship = Ship(coord, BATTLESHIP_SIZE, BATTLESHIP_SIZE, 'Battleship', ship_id)
                                        ship_id += 1
                                        ship_collection.append(ship)
                                        battleship_ready-=1
                            if battleship_ready == 0:
                                pygame.draw.rect(screen, BLACK, BATTLESHIP_BUTTON)
                    if cruiser_place:
                        if cruiser_ready > 0:
                            if vertical:
                                if grid_x >= 0 and grid_x <= 9 and grid_y >= 11 \
                                    and grid_y + CRUISER_SIZE-1 <= 20:
                                    if not board.ship_present(grid_x, grid_y, CRUISER_SIZE, vertical):
                                        coord = []
                                        for i in range(CRUISER_SIZE):
                                            board.update(grid_x, grid_y + i, 3)
                                            coord.append([grid_x, grid_y + i - 11])
                                        ship = Ship(coord, CRUISER_SIZE, CRUISER_SIZE, 'Cruiser', ship_id)
                                        ship_id += 1
                                        ship_collection.append(ship)
                                        cruiser_ready-=1
                            else:
                                if grid_x >= 0 and grid_x + CRUISER_SIZE-1 <= 9 \
                                    and grid_y >= 11 and grid_y <= 20:
                                    if not board.ship_present(grid_x, grid_y, CRUISER_SIZE, vertical):
                                        coord = []
                                        for i in range(CRUISER_SIZE):
                                            board.update(grid_x + i, grid_y, 3)
                                            coord.append([grid_x + i, grid_y - 11])
                                        ship = Ship(coord, CRUISER_SIZE, CRUISER_SIZE, 'Cruiser', ship_id)
                                        ship_id += 1
                                        ship_collection.append(ship)
                                        cruiser_ready-=1
                            if cruiser_ready == 0:
                                pygame.draw.rect(screen, BLACK, CRUISER_BUTTON)
                    if destroyer_place:
                        if destroyer_ready > 0:
                            if vertical:
                                if grid_x >= 0 and grid_x <= 9 and grid_y >= 11 \
                                    and grid_y + DESTROYER_SIZE-1 <= 20:
                                    if not board.ship_present(grid_x, grid_y, DESTROYER_SIZE, vertical):
                                        coord = []
                                        for i in range(DESTROYER_SIZE):
                                            board.update(grid_x, grid_y + i, 3)
                                            coord.append([grid_x, grid_y + i - 11])
                                        ship = Ship(coord, DESTROYER_SIZE, DESTROYER_SIZE, 'Destroyer', ship_id)
                                        ship_id += 1
                                        ship_collection.append(ship)
                                        destroyer_ready-=1
                            else:
                                if grid_x >= 0 and grid_x + DESTROYER_SIZE-1 <= 9 \
                                    and grid_y >= 11 and grid_y <= 20:
                                    if not board.ship_present(grid_x, grid_y, DESTROYER_SIZE, vertical):
                                        coord = []
                                        for i in range(DESTROYER_SIZE):
                                            board.update(grid_x + i, grid_y, 3)
                                            coord.append([grid_x + i, grid_y - 11])
                                        ship = Ship(coord, DESTROYER_SIZE, DESTROYER_SIZE, 'Destroyer', ship_id)
                                        ship_id += 1
                                        ship_collection.append(ship)
                                        destroyer_ready-=1
                            if destroyer_ready == 0:
                                pygame.draw.rect(screen, BLACK, DESTROYER_BUTTON)

                else:
                    if turn:
                        if grid_x >=0 and grid_x < 10 and grid_y >=0 and grid_y < 10:
                            shot = str(grid_x) + ', ' + str(grid_y)
                            print(shot)
                            message.append("Fire at: " + str(GRID_COORD[grid_x]) + "" + str(grid_y+1))
                            connection.send(shot.encode())
                            if len(message[-2]) > 4:
                                if message[-2][-4:]=='miss':
                                    board.update(grid_x, grid_y, 1)
                            if len(message[-2]) > 3:
                                if message[-2][-3:]=='hit':
                                    board.update(grid_x, grid_y, 2)
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

    def hit(self, column, row):
        self.local_grid[row][column] = 2

    def update(self, column, row, value):
        '''Updates client board to display server information'''
        print("Click Grid Coordinates: ", column, row)
        if value == 3:
            if row > self.size and not column > self.size-1 and not row > (self.size * 2):
                self.local_grid[row-(self.size+1)][column] = value
        #Checks that positioning is within grid bounds
        if not row > self.size-1 and not column > self.size-1:
            self.target_grid[row][column] = value

    def ship_present(self, column, row, ship_size, vertical):
        '''Checks for ships in current placement'''
        grid_y = column
        grid_x = row - self.size - 1
        if grid_y >= 0 and grid_y < self.size and grid_x >= 0 and grid_x < self.size:
            for i in range(ship_size):
                if vertical:
                    if self.local_grid[grid_x + i][grid_y] == 3:
                        return True
                else:
                    if self.local_grid[grid_x][grid_y + i] == 3:
                        return True
        return False

class Ship(object):
    '''Ship class'''
    def __init__(self, coordinates, size, hp, name, ship_id):
        self.name = name
        self.coordinates = coordinates
        self.size = size
        self.hp = hp
        self.ship_id = ship_id


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
