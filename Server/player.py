import json
import pprint
import async
import socket
import time

class Player:
    # Player attributes
    #   connection --> a socket connection for sending and receiving data
    #   boardMap --> a dictionary mapping coordinate pairs to ships on the game board
    #   shipCount --> number of remaining ships player still has
    #   previousShots --> a dictionary of all the places that the opponent has fired
    def __init__ (self, connection = None):
        self.connection = connection
        self.boardMap = None
        self.previousShots = {
            'misses': [],
            'hits': []
        }
        self.shipCount = 0

    def getGameBoard (self):
        # Receive board data as a string
        boardData = self.recv(1200)
        jsonData = json.loads(boardData)
        bMap = {}
        shipCount = len (jsonData['ships'])
        for ship in jsonData['ships']:
            for coordStr in ship['coordinates']:
                coords = coordStr.strip().split(',')
                x = int(coords[0])
                y = int(coords[1])
                if not (x,y) in bMap:
                    bMap[(x,y)] = ship
                else:
                    print ('Error two ships in the same spot')
        self.boardMap = bMap
        self.shipCount = shipCount
        return bMap

    # Sends a msg to the client socket
    def send (self, msg):
        self.connection.send(msg.encode())

    # Receives a msg on the client socket as a string
    def recv (self, size):
        return self.connection.recv(size).decode("utf-8")

if __name__ == "__main__":
    fdat = None
    with open('ship.json', 'r') as fp:
        fdat = fp.read()

    def serverWCback ():      
        server = socket.socket()
        server.bind(('', 8080))
        server.listen(1)
        client, _ = server.accept()
        p = Player(client)
        pprint.pprint(p.getGameBoard())
        client.close()
        server.close()

    async.asyncCall(serverWCback)
    time.sleep(2)
    s = socket.socket()
    s.connect(('localhost', 8080))
    s.send(fdat.encode())
    s.close()