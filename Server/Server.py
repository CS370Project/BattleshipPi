import socket
import time
import async
import sys
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
            currentPlayer.send("It's your turn, make a move")
            move = self.getCoordsFromStr(currentPlayer.recv(16))
            # invalid move
            if self.validateMove(move, otherPlayer) is False:
                currentPlayer.send('You have already fired a shot at this location try somewhere else')
                continue
            # hit a ship
            if move in otherPlayer.boardMap:
                currentPlayer.send('hit')
                # Update the previous shots and ship hp          
                ship = otherPlayer.boardMap[move]
                ship['hp'] = ship['hp'] - 1
                otherPlayer.previousShots['hits'].append(move)
                # ship sunk
                if ship['hp'] is 0:
                    currentPlayer.send("You sunk your opponent's {}".format(ship['name']))
                    otherPlayer.send("Your opponent sunk your {}".format(ship['name']))
                    otherPlayer.shipCount = otherPlayer.shipCount - 1
                    # game over currentPlayer wins
                    if otherPlayer.shipCount is 0:
                        self.notifyAllPlayers('Game Over')
                        currentPlayer.send('Congratulations you win!')
                        otherPlayer.send('Sorry you lost, better luck next time!')
                        return
                else:
                    currentPlayer.send("You hit your opponent's {}".format(ship['name']))
                    otherPlayer.send("Your opponent hit your {}".format(ship['name']))
            # miss
            else:
                currentPlayer.send('miss')
                otherPlayer.previousShots['misses'].append(move)
                currentPlayer.send('You missed at coordinates: {}'.format(move))
                otherPlayer.send('Your opponent missed at coordinates: {}'.format(move))
            # Switch turns
            whiteTurn = not whiteTurn

    def startServer (self, stopEvent = None):
        s = socket.socket()
        host = self.host
        port = self.port
        s.bind((host,port))
        s.listen(5)
        print ('Server listening on {}, port {}'.format(host, port))
        # Get the client connections
        def send_msg(sock, msg):
            # Prefix each message with a 4-byte length (network byte order)
            msg = struct.pack('>I', len(msg)) + msg.encode()
            sock.sendall(msg)
        # Accept first client
        connection1, addr1 = s.accept()
        print ('Client {} is connected'.format(addr1))
        send_msg(connection1, 'Connected to server, waiting on your opponent')
        # Accept second client
        connection2, addr2 = s.accept()
        send_msg(connection2, 'Connected to server, waiting on your opponent')
        print ('Client {} is connected'.format(addr2))
        # Create players
        playerSwitch = 'white' if randint(0, 1) is 0 else 'black'
        self.white = Player(connection1) if playerSwitch is 'white' else Player(connection2)
        self.black = Player(connection1) if playerSwitch is 'black' else Player(connection2)
        # Notify players 
        self.notifyAllPlayers('Connected to server, both peers have connected')
        # Ready function
        readys = 0
        def ready (player):
            nonlocal readys
            # wait for ready
            while True:
                player.send('Waiting on game board')            
                # Receive no more than 1024 bytes
                board = player.getGameBoard()
                if board is not None:
                    readys += 1
                    player.board = board
                    player.send('Ready received!')   
                    return
        # Use aysnc module to ask users for ready        
        async.asyncCall(ready, (self.white,))
        async.asyncCall(ready, (self.black,))
        # Wait for both clients to be ready to start
        while readys != 2:
            pass
        # Notify clients about starting
        self.notifyAllPlayers('Both peers ready, starting game!')
        # Start game
        self.runGameLoop(stopEvent)
        # Wait and then close connections
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