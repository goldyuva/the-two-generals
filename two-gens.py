import socket
from _thread import *

serversocket = socket.socket()

host = "127.0.0.1"
portNum = 13117

try:
    serversocket.bind((host, portNum))
except socket.error as e:
    print(str(e))
print("Server started, listening on", serversocket.getsockname()[0])
serversocket.listen(1)

def clientThread(connection):
    print("recieved offer from", connection.getsockname()[0])
    while True:
        buffer = connection.recv(1024)
        if not buffer:
            break
    connection.close()

while True:
    client,address = serversocket.accept()
    print("connected to {}, {}", address[0], str(address[1]))
    start_new_thread(clientThread, (client,))
serversocket.close()