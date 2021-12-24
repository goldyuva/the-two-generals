import socket
import time
from _thread import *

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# The IP address of the server
host = "127.0.0.1"
#The port number the server broadcasts to
portNum = 13117
#The number of active threads that checks if we can start the game
clientCount = 0

# Try to start server
try:
    serverSocket.bind((host, portNum))
except socket.error as e:
    print(str(e))
# Server started
print("Server started, listening on", serverSocket.getsockname()[0])
# Listen for connections
serverSocket.listen(5)

# Define what to do in thread when client is recieved
def clientThread(connection):
    print("recieved offer from", connection.getsockname()[0])
    # Run until we recieve something that is not data
    while True:
        # Allocate recieved data
        connection.send(str(serverSocket.getsockname()[0]).encode('ascii'))
        buffer = connection.recv(1024)
        if not buffer:
            break
    # Close connection
    connection.close()

# While running
while True and clientCount <= 2:
    # Wait for clients
    client,address = serverSocket.accept()
    # Client connected
    print("connected to {}, {}", address[0], str(address[1]))
    # Start a new thread for client
    start_new_thread(clientThread, (client,))
    # Update the number of clients
    clientCount += 1
    print("Thread count =", clientCount)
    # Wait 1 second
    time.sleep(1)
# And now we let the games begin
time.sleep(10)
# startGame()
serverSocket.close()