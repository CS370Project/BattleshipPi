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
    
    # Sends a msg to both client
    def notifyAllPlayers (self, white, black, msg):
        white.send(msg)
        black.send(msg)

    # Runs the game loop between players
    def runGameLoop (self, white, black):
        # White & black follows after the chess idiom that white goes first
        whiteTurn = True
        currentPlayer = None
        while True:
            # Determine turn
            currentPlayer = white if whiteTurn else black
            otherPlayer = black if whiteTurn else white
            currentPlayer.send("It's your turn, make a move\n")
            response = currentPlayer.recv(1024)
            toPlayer = "Your move was: " + response
            toOtherPlayer = "Your opponent's move was: " + response
            currentPlayer.send(toPlayer)
            otherPlayer.send(toOtherPlayer)
            print(response)
            whiteTurn = not whiteTurn

    def startServer (self):
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
        white = Player(connection1) if playerSwitch is 'white' else Player(connection2)
        black = Player(connection1) if playerSwitch is 'black' else Player(connection2)
        # Notify players 
        self.notifyAllPlayers(white, black, 'Connected to server, both peers have connected\n')
        # Ready function
        readys = 0
        def ready (player):
            nonlocal readys
            # wait for ready
            while True:
                player.send('Are you ready to start?\n')            
                # Receive no more than 1024 bytes
                board = player.getGameBoard()
                if board is not None:
                    readys += 1
                    player.board = board
                    player.send('Ready received!\n')   
                    return
        # Use aysnc module to ask users for ready        
        async.asyncCall(ready, (white,))
        async.asyncCall(ready, (black,))
        # Wait for both clients to be ready to start
        while readys != 2:
            pass
        # Notify clients about starting
        self.notifyAllPlayers(white, black, 'Both peers ready, starting game!\n')
        # Start game
        self.runGameLoop(white, black)
        # Wait and then close connections
        time.sleep(15)
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