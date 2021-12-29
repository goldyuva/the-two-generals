from enum import Flag
import socket
from struct import *
import struct
import select
import sys
import termios
import tty
import getch
import random
import selectors
from scapy.all import get_if_addr

#the colors for coloring the client terminal
colors = ['\033[95m', '\033[94m', '\033[96m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m', '\033[4m']
rainbow = ['\x1b[1;{0};40m']
#index for switching the colors
index = [0]
broadcast_ip = get_if_addr('eth2')

#print char-char with rainbow colors
def sprint(s):
    prstr = ''
    for i in range(0, len(s)):
        format = rainbow[0].format(31 + i%6)
        prstr += format + s[i]
    print(prstr + '\x1b[0m')

#print with cycling colors between purple blue and turquise
def cprint(s):
    print(colors[index[0]] + colors[7] + s + colors[6])
    index[0] = (index[0] + 1) % 3

#print winners with backgrounds
def wprint(s):
    print(colors[4] + colors[7] + colors[8] + s + colors[6])

#print errors in red
def eprint(s):
    print(colors[5] + colors[8] + colors[7] + s + colors[6])

#client name
name = "General Iroh {0}".format(random.randint(1, 4))

while True:
    # Define the broadcast port on which you want to connect
    brPort = 13117
    #string format
    strFormat = '>IBH'
    #print the player name, because of randomness, easier to test this way
    cprint(name)
    #initialize packet data
    data = ''
    unpackedBr = ''
    to_finish = False

    #initialize broadcast receiver socket
    udpRecvSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udpRecvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        #bind to the broadcast port
        udpRecvSocket.bind(('255.255.255.255', brPort))
    except socket.error as e:
        #else print error
        eprint(e)

    sprint("Client Started, listening for offer requests...")
    #initialize parameters
    host = ''
    invalidPacket = True
    while invalidPacket:
        try:
            # message received from server
            data = udpRecvSocket.recvfrom(1024)
            #get ip address from message received
            host = data[1][0]
            unpackedBr = struct.unpack(strFormat, data[0])
            #if packet is in format
            if unpackedBr[0] == 0xabcddcba:
                if unpackedBr[1] == 0x2:
                    invalidPacket = False
        except:
            #packet invalid
            pass
    #get port from packet
    port = unpackedBr[2]
    #get eth ip address
    host = broadcast_ip
    # print the received message
    cprint('Received offer from {0}, Attempting to connect'.format(host))
    #initialize TCP socket
    tcpSendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #connect to the ip and port the server sent
        tcpSendSocket.connect((host, port))
    except socket.error as e:
        #didn't succeed
        eprint(e)
    #send the server the client name
    tcpSendSocket.send(name.encode())

    try:
        #receive a welcome message
        welcomeMessage = tcpSendSocket.recv(1024).decode()
    except:
        #print failiure to receive message
        eprint("Failed to receive a welcome message.")
        continue
    cprint(welcomeMessage)
    if welcomeMessage.endswith('disconnected.'):
        continue

    #get equation from server
    equation = tcpSendSocket.recv(1024).decode()
    #print it to the screen
    cprint("How much is {0}? ".format(equation))
    summary = [None]

    def keyboard_input():
        try:
            ansFlag = False
            while not ansFlag:
                ch = getch.getch()
                cprint("RECEIVED CHAR: {0}".format(ch))
                if ansFlag == False:
                    tcpSendSocket.send(ch.encode())
                ansFlag = True
        except asyncio.CancelledError:
            eprint("can't read char anymore")
    def receive_message():
        while summary[0] == None:
            #receive summary
            summary[0] = tcpSendSocket.recv(1024).decode()
            wprint(summary[0])
            raise KeyboardInterrupt

    try:
        #create event handler0
        selec = selectors.DefaultSelector()
        #register both read from user and socket events
        selec.register(sys.stdin, selectors.EVENT_READ, keyboard_input)
        selec.register(tcpSendSocket, selectors.EVENT_READ, receive_message)
        #number of input for stdin, to use in changing settings
        fd = sys.stdin.fileno()
        #keeps old settings of input handling
        old_settings = termios.tcgetattr(fd)
        #input does not need newline at the end
        tty.setcbreak(fd)
        #while socket is alive
        while tcpSendSocket != None:
            #handle events with callbacks defined earlier
            events = selec.select()
            for key, mask in events:
                callback = key.data
                callback()
        #reset input handling settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        #handle exception thrown earlier so we stop all events
    except KeyboardInterrupt:
        pass
    finally:
        #close TCP socket
        tcpSendSocket.close()
        #change back to old settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        #restarting the loop
        print("restarting...")
# Start the game
# close the connection
#tcpSendSocket.close()