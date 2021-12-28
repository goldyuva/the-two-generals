from enum import Flag
import socket
from struct import *
import struct
import time
import select
import sys
import getch
import random
import asyncio

# The IP address of the client
host = ''

# Define the broadcast port on which you want to connect
brPort = 13117
strFormat = '>IBH'
name = "Admiral Greneral Aladdin {0}".format(random.randint(0, 100))
print(name)
data = ''
unpackedBr = ''

async def ainput() -> str:
    return await asyncio.get_event_loop().run_in_executor(
            None, lambda: sys.stdin.read(1))

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
        print(unpackedBr[2])
        if unpackedBr[0] == 0xabcddcba:
            if unpackedBr[1] == 0x2:
                invalidPacket = False
    except:
        pass

port = unpackedBr[2]
print(port)
# print the received message
print('Received offer from {0}, Attempting to connect'.format(host))
tcpSendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

equation = tcpSendSocket.recv(1024).decode()
print("How much is {0}? ".format(equation))
summary = None
async def keyboard_input():
    global summary
    ansFlag = False
    while not ansFlag and not summary:
        sleep = False
        if sleep:
            await asyncio.sleep(1)
            print("sleeping works fine")
        else:
            ch = await ainput()
            print("RECEIVED CHAR: {0}".format(ch))
            if ansFlag == False:
                tcpSendSocket.send(ch.encode())
            ansFlag = True
            print(ch)

async def receive_message():
    global summary
    while summary == None:
        summary = await asyncio.get_event_loop().run_in_executor(None, lambda: tcpSendSocket.recv(1024).decode())
        print(summary)
try:
    asyncio.get_event_loop().run_until_complete(asyncio.wait(
        [keyboard_input(), receive_message()]
    ))
except KeyboardInterrupt:
    quit()
# Start the game
# close the connection
#tcpSendSocket.close()