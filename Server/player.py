class Player:
    # Player attributes
    #   connection --> a socket connection for sending and receiving data
    #   boardMap --> a dictionary mapping coordinate pairs to ships on the game board
    #   shipCount --> number of remaining ships player still has
    def __init__ (self, connection = None):
        self.connection = connection

    def getGameBoard (self):
        return 0

    # Sends a msg to the client socket
    def send (self, msg):
        self.connection.send(msg.encode())

    # Receives a msg on the client socket as a string
    def recv (self, size):
        return self.connection.recv(size).decode("utf-8")
