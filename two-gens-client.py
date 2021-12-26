import socket
from struct import *
import struct
import time
import select

# The IP address of the client
host = ''

# Define the broadcast port on which you want to connect
brPort = 13117
strFormat = '>IBH'
name = "General Zod"
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
    data = udpRecvSocket.recvfrom(1024)
    host = data[1][0]
    unpackedBr = struct.unpack(strFormat, data[0])
    if unpackedBr[0] == 0xabcddcba:
        if unpackedBr[1] == 0x2:
            invalidPacket = False

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
welcomeMessage = 'a'
while welcomeMessage == 'a':
    if ready_sockets:
        welcomeMessage = tcpSendSocket.recv(1024).decode()
        print(welcomeMessage)
    else:
        time.sleep(1)
equation = None
while equation == None:
    if tcpSendSocket in ready_sockets:
        equation = tcpSendSocket.recv(1024).decode()
        ans = input("How much is {0}?".format(equation))
        tcpSendSocket.send(ans.encode())
    else:
        time.sleep(1)
# Start the game
# close the connection
#tcpSendSocket.close()