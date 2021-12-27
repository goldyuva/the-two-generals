import socket
import struct
import threading
import select
import time
from _thread import *
from scapy.all import get_if_addr
import random

host = get_if_addr('eth0')

brPort = 13117
tcpPort = [0]
strFormat = '>IBH'
tcpAddr = (host, tcpPort[0])
MAX_USER_SIZE = 2
thread = [None] * MAX_USER_SIZE
names = [None] * MAX_USER_SIZE
bufSize = 1024
winner = [None]
SLEEP_TIME_UNTIL_START = 10
client_address = [None] * MAX_USER_SIZE
finish_threads_execution = False

tcpRecvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    tcpRecvSocket.bind(tcpAddr)
    tcpPort[0] = tcpRecvSocket.getsockname()[1]
except socket.error as e:
    print(e)
tcpRecvSocket.listen(5)

def generateAdd():
    input1 = random.randint(1, 10)
    input2 = random.randint(0, 10 - input1)
    return "{0}+{1}".format(input1, input2), input1+input2

def start_game(connection, equation, solution, names, index):
    if not finish_threads_execution:
        connection.send(equation.encode())
    answer, _, _ = select.select([connection], [], [], 1)
    while winner[0] == None and finish_threads_execution == False:
        if connection in answer:
            ans = connection.recv(bufSize).decode()
            if ans == solution:
                winner[0] = names[index]
            else:
                winner[0] = names[1 - index]
        try:
            answer, _, _ = select.select([connection], [], [], 1)
        except:
            print("Connection reset...")
    return winner


def clientThread(connection, index, equation, solution, names):
    
    cv.acquire()
    try:
        connection.sendall(b"Welcome to Quick Maths.")
        names[index] = connection.recv(bufSize).decode()
    except:
        client_address[1 - index][0].sendall("Other player disconnected.".encode())
    cv.release()
    try:
        print("Team {0}: {1}".format(index + 1, names[index]))
        start_game(connection, equation, solution, names, index)
    except:
        pass
    return

def recieve_Thread(cv):
    clientCount = 0
    thread = [None] * MAX_USER_SIZE
    finish_threads_execution = False
    winner[0] = None
    equation, solution = generateAdd()
    cv.acquire()
    print("Server started, listening on {0}".format(host))
    while True and clientCount < MAX_USER_SIZE:
        client,address = tcpRecvSocket.accept()
        client_address[clientCount] = [client, address]
        # Print client connected
        print("connected to {0}, {1}".format(address[0], str(address[1])))
        # Start a new thread for client
        thread[clientCount] = threading.Thread(target = clientThread, args = (client, clientCount, equation, solution, names))
        # Update the number of clients
        clientCount += 1
        print("Thread count =", clientCount)
    tcpPort[0] = 0
    # And now we let the games begin
    time.sleep(SLEEP_TIME_UNTIL_START)
    print("Starting game...")
    for i in range (0, MAX_USER_SIZE):
        try:
            thread[i].start()
        except:
            client_address[1 - i][0].sendall("{0} disconnected", names[i])
    cv.release()
    countdown = 10
    while winner[0] == None and countdown > 0:
        time.sleep(1)
        countdown -= 1
    if not names[0] == None and not names[1] == None:
        if winner[0] == None:
            winner[0] = "it's a draw"
        cv.acquire()
        finish_threads_execution = True
        print("Winner: {0}".format(winner[0]))
        summary = "Thanks to both teams: {0}, {1}.\nAnd the winner is...\n{2}!!".format(names[0], names[1], winner[0])
        for i in range (0, MAX_USER_SIZE):
            try:
                client_address[i][0].sendall(summary.encode())
                client_address[i][0].close()
                thread[i].join()
            except:
                print("Client from team: {0} disconnected.".format(names[i]))
        cv.release()
    tcpPort[0] = tcpRecvSocket.getsockname()[1]

def sendUDP():
    udpSendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        if tcpPort[0] != 0:
            packedBr = struct.pack(strFormat, 0xabcddcba, 0x2, tcpPort[0])
            udpSendSocket.sendto(packedBr, ('255.255.255.255', brPort))
        time.sleep(1)

cv = threading.Condition()
threadUDP = threading.Thread(target = sendUDP, args = ())
threadUDP.start()
while True:
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