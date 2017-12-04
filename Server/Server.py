import socket
import time
import async
import sys
import json
from random import randint
from player import Player

class BattleShipServer:
    
    def __init__(self, host = '', port = 8080):
        self.host = host
        self.port = port
        self.white = None
        self.black = None
    
    # Sends a msg to both client
    def notifyAllPlayers (self, msg):
        self.white.send(msg)
        self.black.send(msg)

    def getCoordsFromStr (self, moveStr):
        coords = moveStr.strip().split(',')
        x = int(coords[0])
        y = int(coords[1])
        return (x,y)

    def validateMove (self, move, player):
        return not (move in player.previousShots['hits'] or move in player.previousShots['misses'])

    # Runs the game loop between players
    def runGameLoop (self, stopEvent = None):
        # White & black follows after the chess idiom that white goes first
        whiteTurn = True
        currentPlayer = None
        while True:
            # stop the thread if told to
            if stopEvent is not None and stopEvent.is_set():
                return
            # Determine turn
            currentPlayer = self.white if whiteTurn else self.black
            otherPlayer = self.black if whiteTurn else self.white
            currentPlayer.send("It's your turn, make a move\n")
            move = self.getCoordsFromStr(currentPlayer.recv(16))
            # invalid move
            if self.validateMove(move, otherPlayer) is False:
                currentPlayer.send('You have already fired a shot at this location try somewhere else\n')
                continue
            # hit a ship
            if move in otherPlayer.boardMap:
                currentPlayer.send('hit\n')
                # Update the previous shots and ship hp          
                ship = otherPlayer.boardMap[move]
                ship['hp'] = ship['hp'] - 1
                otherPlayer.previousShots['hits'].append(move)
                # ship sunk
                if ship['hp'] is 0:
                    currentPlayer.send("You sunk your opponent's {}\n".format(ship['name']))
                    otherPlayer.send("Your opponent sunk your {}\n".format(ship['name']))
                    otherPlayer.shipCount = otherPlayer.shipCount - 1
                    # game over currentPlayer wins
                    if otherPlayer.shipCount is 0:
                        self.notifyAllPlayers('Game Over\n')
                        currentPlayer.send('Congratulations you win!\n')
                        otherPlayer.send('Sorry you lost, better luck next time!\n')
                        return
                else:
                    currentPlayer.send("You hit your opponent's {}\n".format(ship['name']))
                    otherPlayer.send("Your opponent hit your {}\n".format(ship['name']))
            # miss
            else:
                currentPlayer.send('miss\n')
                otherPlayer.previousShots['misses'].append(move)
                currentPlayer.send('You missed at coordinates: {}\n'.format(move))
                otherPlayer.send('Your opponent missed at coordinates: {}\n'.format(move))
            # Switch turns
            whiteTurn = not whiteTurn

    def gameBoardTest (self, player):
        data = None
        with open ('ship.json', 'r') as fp:
            data = json.load(fp)
        bMap = {}
        shipCount = len (data['ships'])
        for ship in data['ships']:
            for coordStr in ship['coordinates']:
                coords = coordStr.strip().split(',')
                x = int(coords[0])
                y = int(coords[1])
                if not (x,y) in bMap:
                    bMap[(x,y)] = ship
                else:
                    print ('Error two ships in the same spot')
        player.boardMap = bMap
        player.shipCount = shipCount
        return bMap

    def startServer (self, stopEvent = None):
        s = socket.socket()
        host = self.host
        port = self.port
        s.bind((host,port))
        s.listen(5)
        print ('Server listening on {}, port {}'.format(host, port))
        # Get the client connections
        # Accept first client
        connection1, addr1 = s.accept()
        print ('Client {} is connected'.format(addr1))
        connection1.send('Connected to server, waiting on your opponent\n'.encode())
        # Accept second client
        connection2, addr2 = s.accept()
        print ('Client {} is connected'.format(addr2))
        # Create players
        playerSwitch = 'white' if randint(0, 1) is 0 else 'black'
        self.white = Player(connection1) if playerSwitch is 'white' else Player(connection2)
        self.black = Player(connection1) if playerSwitch is 'black' else Player(connection2)
        # Notify players 
        self.notifyAllPlayers('Connected to server, both peers have connected\n')
        # Ready function
        readys = 0
        def ready (player):
            nonlocal readys
            # wait for ready
            while True:
                player.send('Are you ready to start?\n')    
                response = player.recv(16)    
                # Receive no more than 1024 bytes
                ''' Removed for testing: board = player.getGameBoard() '''
                board = self.gameBoardTest(player)
                ''' ---------- '''
                if board is not None:
                    readys += 1
                    player.send('Ready received!\n')   
                    return
        # Use aysnc module to ask users for ready        
        async.asyncCall(ready, (self.white,))
        async.asyncCall(ready, (self.black,))
        # Wait for both clients to be ready to start
        while readys != 2:
            pass
        # Notify clients about starting
        self.notifyAllPlayers('Both peers ready, starting game!\n')
        # Start game
        self.runGameLoop(stopEvent)
        # Wait and then close connections
        time.sleep(3)
        connection1.close()
        connection2.close()
        return;

if __name__ == "__main__":
    if len(sys.argv) is 2:
        p = int(sys.argv[1])
        server = BattleShipServer(port = p)
    else:
        server = BattleShipServer()
    server.startServer()