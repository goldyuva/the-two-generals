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
from scapy.all import get_if_addr

# The IP address of the client
host = ''
colors = ['\033[95m', '\033[94m', '\033[96m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m', '\033[4m']
rainbow = ['\x1b[1;{0};40m']
index = [0]

def sprint(s):
    prstr = ''
    for i in range(0, len(s)):
        format = rainbow[0].format(31 + i%6)
        prstr += format + s[i]
    print(prstr + '\x1b[0m')

def cprint(s):
    print(colors[index[0]] + colors[7] + s + colors[6])
    index[0] = (index[0] + 1) % 3

def wprint(s):
    print(colors[4] + colors[7] + colors[8] + s + colors[6])

def eprint(s):
    print(colors[5] + colors[8] + colors[7] + s + colors[6])

# Define the broadcast port on which you want to connect
brPort = 13117
strFormat = '>IBH'
name = "General Iroh {0}".format(random.randint(1, 4))
cprint(name)
data = ''
unpackedBr = ''
to_finish = False

def kbhit():
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    return dr != []

def get_input():
    msg = None
    while msg == None and not to_finish:
        if(kbhit()):
            msg = getch.getch()
            print("got key:", msg)
            tcpSendSocket.send(msg.encode())
        time.sleep(1)
    return str(chr(msg))

async def ainput() -> str:
    return await asyncio.get_event_loop().run_in_executor(
            None, lambda: get_input())

udpRecvSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, socket.IPPROTO_UDP)
udpRecvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    udpRecvSocket.bind(('255.255.255.255', brPort))
except socket.error as e:
    eprint(e)

# connect to server on local computer
#udpRecvSocket.connect((host,port))

sprint("Client Started, listening for offer requests...")
# message received from server
invalidPacket = True
while invalidPacket:
    try:
        data = udpRecvSocket.recvfrom(1024)
        host = data[1][0]
        if host.endswith("77"):
            unpackedBr = struct.unpack(strFormat, data[0])
            if unpackedBr[0] == 0xabcddcba:
                if unpackedBr[1] == 0x2:
                    invalidPacket = False
    except:
        pass

port = unpackedBr[2]
# print the received message
cprint('Received offer from {0}, Attempting to connect'.format(host))
tcpSendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = get_if_addr('eth1')
try:
    tcpSendSocket.connect((host, port))
except socket.error as e:
    eprint(e)
tcpSendSocket.send(name.encode())
ready_sockets, _, _ = select.select([tcpSendSocket], [], [])

try:
    welcomeMessage = tcpSendSocket.recv(1024).decode()
except:
    eprint("Failed to receive a welcome message.")
    quit()
cprint(welcomeMessage)
if welcomeMessage.endswith('disconnected.'):
    quit()

equation = tcpSendSocket.recv(1024).decode()
cprint("How much is {0}? ".format(equation))
summary = [None]
async def keyboard_input():
    try:
        ansFlag = False
        while not ansFlag:
            ch = await ainput()
            cprint("RECEIVED CHAR: {0}".format(ch))
            if ansFlag == False:
                tcpSendSocket.send(ch.encode())
            ansFlag = True
    except asyncio.CancelledError:
        eprint("can't read char anymore")
async def receive_message():
    while summary[0] == None:
        summary[0] = await asyncio.get_event_loop().run_in_executor(None, lambda: tcpSendSocket.recv(1024).decode())
        wprint(summary[0])
        raise KeyboardInterrupt
tasks = [asyncio.ensure_future(keyboard_input()), asyncio.ensure_future(receive_message())]
async def main():
    try:
        gathering = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    except KeyboardInterrupt:
        gathering.cancel()
try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    cprint("finishing...")
    to_finish = True
# Start the game
# close the connection
#tcpSendSocket.close()