from enum import Flag
import socket
from struct import *
import struct
import time
import select
import sys
import getch
import random

# The IP address of the client
host = ''

# Define the broadcast port on which you want to connect
brPort = 13117
strFormat = '>IBH'
name = "Admiral Greneral Aladdin {0}".format(random.randint(0, 100))
print(name)
data = ''
unpackedBr = ''

udpRecvSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, socket.IPPROTO_UDP)
udpRecvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    udpRecvSocket.bind(('', brPort))
except socket.error as e:
    print(e)

# connect to server on local computer
#udpRecvSocket.connect((host,port))

print("Client Started, listening for offer requests...")
# message received from server
invalidPacket = True
while invalidPacket:
    try:
        data = udpRecvSocket.recvfrom(1024)
        host = data[1][0]
        unpackedBr = struct.unpack(strFormat, data[0])
        if unpackedBr[0] == 0xabcddcba:
            if unpackedBr[1] == 0x2:
                invalidPacket = False
    except:
        pass

port = unpackedBr[2]
# print the received message
print('Received offer from {0}, Attempting to connect'.format(host))
tcpSendSocket = socket.socket()
try:
    tcpSendSocket.connect((host, port))
except socket.error as e:
    print(e)
tcpSendSocket.send(name.encode())
ready_sockets, _, _ = select.select([tcpSendSocket], [], [])

try:
    welcomeMessage = tcpSendSocket.recv(1024).decode()
except:
    print("Failed to receive a welcome message.")
    quit()
print(welcomeMessage)
if welcomeMessage.endswith('disconnected.'):
    quit()

def kbhit():
    ready_input, _, _ = select.select([sys.stdin], [], [], 0)
    return sys.stdin in ready_input

equation = tcpSendSocket.recv(1024).decode()
print("How much is {0}? ".format(equation))
summary = None

ready_sockets, _, _ = select.select([tcpSendSocket], [], [], 1)
while summary == None:
    if kbhit():
        ch = getch.getch()
        print("RECEIVED CHAR: {0}".format(ch))
        tcpSendSocket.send(ch.encode())
        ansFlag = True
    elif tcpSendSocket in ready_sockets:
        summary = tcpSendSocket.recv(1024).decode()
        print(summary)
        ansFlag = True
    ready_sockets, _, _ = select.select([tcpSendSocket], [], [], 1)
# Start the game
# close the connection
#tcpSendSocket.close()