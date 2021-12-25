import socket
import struct
import threading
import time
from _thread import *

host = '127.0.0.1'
brPort = 13117
tcpPort = 107
strFormat = '>IBH'
tcpAddr = (host, tcpPort)
MAX_USER_SIZE = 2
thread = [None] * MAX_USER_SIZE
names = [None] * MAX_USER_SIZE
bufSize = 1024

def start_game(connection, equation, solution, names, index):
    startTime = time.time()
    connection.send(equation.encode())
    ans = connection.recv(bufSize).decode()
    if ans == solution:
        return names[index]
    else:
        return names[1 - index]


def clientThread(connection, index, equation, solution, names):
    cv.acquire()
    connection.send(b"Welcome to Quick Maths.")
    names[index] = connection.recv(bufSize).decode()
    cv.release()
    print("Team {0}: {1}".format(index + 1, names[index]))
    names[index] = start_game(connection, equation, solution, names, index)
    # Close connection
    connection.close()
    print("Client connection closed.")

def recieve_Thread(cv):
    clientCount = 0
    
    tcpRecvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcpRecvSocket.bind(tcpAddr)
    except socket.error as e:
        print(e)
    tcpRecvSocket.listen(5)

    equation = "2+2"
    solution = 4
    cv.acquire()
    while True and clientCount < MAX_USER_SIZE:
        client,address = tcpRecvSocket.accept()
        # Print client connected
        print("connected to {0}, {1}".format(address[0], str(address[1])))
        # Start a new thread for client
        thread[clientCount] = threading.Thread(target = clientThread, args = (client, clientCount, equation, solution, names))
        thread[clientCount].start()
        # Update the number of clients
        clientCount += 1
        print("Thread count =", clientCount)
    # And now we let the games begin
    time.sleep(10)
    print("Starting game...")
    cv.release()
    for i in range(0, MAX_USER_SIZE):
        thread[i].join()
    min = 10
    winner = ""
    for [t, ans, name] in names:
        if t < min and ans == solution:
            min = t
            winner = name
    print("The winner is {0}".format(winner))

    tcpRecvSocket.close()

def sendUDP():
    udpSendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udpSendSocket.connect((host, brPort))
    except socket.error as e:
        print(e)

    while True:
        packedBr = struct.pack(strFormat, 0xabcddcba, 0x2, tcpPort)
        udpSendSocket.sendall(packedBr)
        time.sleep(1)

cv = threading.Condition()
threadUDP = threading.Thread(target = sendUDP, args = ())
threadUDP.start()
recieve_Thread(cv)



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
#           buffer = connection.recv(bufSize)
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