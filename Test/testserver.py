import unittest
import threading
import sys
import socket
import time
sys.path.insert(0, '../Server/')
from server import BattleShipServer
from async import asyncCall

class TestServer(unittest.TestCase):

    def setUp (self):
        self.bserver = BattleShipServer(port = 8080)

    def test_server(self):
        # Start web server
        stopServer = threading.Event()
        bThread = threading.Thread(target=self.bserver.startServer, args=(stopServer,))
        bThread.start()
        # Print socket recv values
        def printSocketRec (sockname, connection, stopEvent):
            while True:
                if stopEvent.is_set():
                    break
                try:
                    # https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
                    msg = connection.recv(254).decode('utf-8')
                except:
                    connection.close()
                    return
                for line in msg.splitlines():
                    print ('{}: {}'.format(sockname, line))
            connection.close()
        # Create socket connections
        aStop = threading.Event()
        bStop = threading.Event()
        a = socket.socket()
        b = socket.socket()
        sockThread1 = threading.Thread(target=printSocketRec, args=("A", a, aStop))
        sockThread2 = threading.Thread(target=printSocketRec, args=("B", b, bStop))
        # Connect to the server
        a.settimeout(2)
        b.settimeout(2)
        a.connect(('localhost', 8080))
        b.connect(('localhost', 8080))
        sockThread1.start()
        sockThread2.start()
        # Send Ready?
        a.send('1 1'.encode())
        b.send('1 1'.encode())
        
        time.sleep(.05)
        a.send('2 2'.encode())
        b.send('2 2'.encode())
        time.sleep(.3)
        aStop.set()
        bStop.set()
        stopServer.set()
        time.sleep(.3)         
        self.assertTrue(True)
        return

if __name__ == "__main__":
    unittest.main()