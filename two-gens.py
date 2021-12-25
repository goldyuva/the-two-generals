import socket
import time
from _thread import *

host = '127.0.0.1'
port = 13117
addr = (host, port)

def clientThread(connection):
    connection.send(b"Enter team name: ")
    teamName = connection.recv(1024)
    print(teamName)
    connection.wait()
    # Close connection
    connection.close()
    print("Client connection closed.")

def recieve_Thread():
    clientCount = 0
    tcpRecvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcpRecvSocket.bind(addr)
    except socket.error as e:
        print(e)
    tcpRecvSocket.listen(5)
    # While running
    while True and clientCount <= 2:
        # Wait for clients
        client,address = tcpRecvSocket.accept()
        # Client connected
        print("connected to {0}, {1}".format(address[0], str(address[1])))
        # Start a new thread for client
        start_new_thread(clientThread, (client,))
        # Update the number of clients
        clientCount += 1
        print("Thread count =", clientCount)
        # Wait 1 second
    # And now we let the games begin
    time.sleep(10)
    # startGame()
    tcpRecvSocket.close()

def sendUDP():
    udpSendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udpSendSocket.connect((host, port))
    except socket.error as e:
        print(e)

    while True:
        udpSendSocket.sendall(host.encode('ascii'))
        time.sleep(1)

start_new_thread(sendUDP, ())
recieve_Thread()



#   udpSendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#   udpSendSocket.bind(('', 13117))
#   # The IP address of the client
#   #hostname = socket.gethostname()
#   #host = socket.gethostbyname(hostname)
#   host = '127.0.0.1'
#   
#   #The port number the server broadcasts to
#   portNum = 13117
#   udpSendSocket.connect((host, portNum))
#   #The number of active threads that checks if we can start the game
#   clientCount = 0
#   
#   # Try to start server
#   try:
#       udpSendSocket.bind((host, portNum))
#   except socket.error as e:
#       print(str(e))
#   # Server started
#   print("Server started, listening on", host)
#   # Listen for connections
#   
#   # Define what to do in thread when client is recieved
#   def clientThread(connection):
#       print("recieved offer from", connection.getsockname()[0])
#       # Run until we recieve something that is not data
#       while True:
#           # Allocate recieved data
#           connection.send(str(udpSendSocket.getsockname()[0]).encode('ascii'))
#           buffer = connection.recv(1024)
#           if not buffer:
#               break
#       # Close connection
#       connection.close()
#   
#   # While running
#   while True and clientCount <= 2:
#       # Wait for clients
#       udpSendSocket.sendall(str(host).encode('ascii'))
#       time.sleep(1)
#       #   client,address = udpSendSocket.accept()
#       #   # Client connected
#       #   print("connected to {}, {}", address[0], str(address[1]))
#       #   # Start a new thread for client
#       #   start_new_thread(clientThread, (client,))
#       #   # Update the number of clients
#       #   clientCount += 1
#       #   print("Thread count =", clientCount)
#       #   # Wait 1 second
#   # And now we let the games begin
#   time.sleep(10)
#   # startGame()
#   udpSendSocket.close()