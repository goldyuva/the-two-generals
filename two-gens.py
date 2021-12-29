import socket
import struct
import threading
import select
import time
from _thread import *
from scapy.all import get_if_addr
import random
import math
import sys

host = get_if_addr('eth1')

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

colors = ['\033[95m', '\033[94m', '\033[96m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m', '\033[4m']
backgrounds = ['\u001b[41;1m']
rainbow = ['\x1b[1;{0};40m']
index = [0]
players = {}
equations = {}

tcpRecvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    tcpRecvSocket.bind(tcpAddr)
    tcpPort[0] = tcpRecvSocket.getsockname()[1]
except socket.error as e:
    cprint(e)
tcpRecvSocket.listen(5)

def sprint(s):
    prstr = ''
    for i in range(0, len(s)):
        format = rainbow[0].format(31 + i%6)
        prstr += format + s[i]
    print(prstr + '\x1b[0m')

def cprint(s):
    print(colors[index[0]] + colors[7] + s + colors[6])
    index[0] = (index[0] + 1) % 3

def tprint(s):
    print(colors[5] + colors[8] + colors[7] + s + colors[6])

def wprint(s):
    print(backgrounds[0] + colors[4] + colors[7] + colors[8] + s + colors[6])

def generateAdd():
    input1 = random.randint(1, 9)
    input2 = random.randint(0, 9 - input1)
    return "{0}+{1}".format(input1, input2), input1+input2

def generateMult():
    input1 = random.randint(1,3)
    input2 = random.randint(0, int(9/input1))
    return "{0}*{1}".format(input1, input2), input1*input2

def generateFact():
    input1 = random.randint(0,3)
    return "{0}!".format(input1), math.factorial(input1)

def generatePower():
    input1 = random.randint(1, 3)
    input2 = random.randint(0, 2)
    return "{0}^{1}".format(input1, input2), input1**input2

def generateEquation():
    funGen = [generateAdd, generateMult, generateFact, generatePower]
    idx = random.randint(0, len(funGen) - 1)
    return funGen[idx]()

def add_player_stats():
    for name in names:
        nwins = 0
        winstr = 0
        total = 0
        if name in players:
            nwins = players[name]['wins']
            winstr = players[name]['winstreak']
            total = players[name]['totalgames']
        if name == winner[0]:
            nwins += 1
            winstr += 1
        total += 1
        players[name] = {'wins': nwins, 'winstreak': winstr, 'totalgames': total}

def add_server_stats(eq, sol):
    if eq in equations:
        equations[eq] = {'times': equations[eq]["times"] + 1, 'solution': sol}
    else:
        equations[eq] = {'times': 1, 'solution': sol}

def start_game(connection, equation, solution, names, index):
    if not finish_threads_execution:
        connection.send(equation.encode())
    answer, _, _ = select.select([connection], [], [], 1)
    while winner[0] == None and finish_threads_execution == False:
        if connection in answer:
            ans = connection.recv(bufSize).decode()
            if ans == str(solution):
                winner[0] = names[index]
            else:
                winner[0] = names[1 - index]
        try:
            answer, _, _ = select.select([connection], [], [], 1)
        except:
            cprint("Connection reset...")
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
        tprint("Team {0}: {1}".format(index + 1, names[index]))
        start_game(connection, equation, solution, names, index)
    except:
        pass
    return

def recieve_Thread(cv):
    clientCount = 0
    thread = [None] * MAX_USER_SIZE
    finish_threads_execution = False
    winner[0] = None
    equation, solution = generateEquation()
    cv.acquire()
    sprint("Server started, listening on {0}".format(host))
    while True and clientCount < MAX_USER_SIZE:
        client,address = tcpRecvSocket.accept()
        client_address[clientCount] = [client, address]
        # cprint client connected
        cprint("connected to {0}, {1}".format(address[0], str(address[1])))
        # Start a new thread for client
        thread[clientCount] = threading.Thread(target = clientThread, args = (client, clientCount, equation, solution, names))
        # Update the number of clients
        clientCount += 1
        cprint("Thread count = {0}".format(clientCount))
    tcpPort[0] = 0
    # And now we let the games begin
    time.sleep(SLEEP_TIME_UNTIL_START)
    cprint("Starting game...")
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
        add_player_stats()
        add_server_stats(equation, solution)
        cv.acquire()
        finish_threads_execution = True
        wprint("Winner: {0}".format(winner[0]))
        summary = "Thanks to both teams: {0}, {1}.\nAnd the winner is...\n{2}!!".format(names[0], names[1], winner[0])
        for i in range (0, MAX_USER_SIZE):
            try:
                client_address[i][0].sendall(summary.encode())
                client_address[i][0].close()
                thread[i].join()
            except:
                cprint("Client from team: {0} disconnected.".format(names[i]))
        cv.release()

    cprint("\nPlayer statistics:")
    numOfWins = ['', -1]
    winPercentage = ['', -1]
    winstreak = ['', -1]
    for p in players.keys():
        if players[p]["wins"] > numOfWins[1]:
            numOfWins = [p, players[p]["wins"]]
        if players[p]["wins"]/players[p]["totalgames"] > winPercentage[1]:
            winPercentage = [p, players[p]["wins"]/players[p]["totalgames"]]
        if players[p]["winstreak"] > winstreak[1]:
            winstreak = [p, players[p]["winstreak"]]
    if numOfWins[1] != -1:
        wprint("Highest number of wins: {0} with {1} wins!".format(numOfWins[0], numOfWins[1]))
    if winPercentage[1] != -1:
        wprint("highest win percentage: {0} with {1}% percent win rate!".format(winPercentage[0], winPercentage[1] * 100))
    if winstreak[1] != -1:
        wprint("biggest win streak: {0} with {1} wins in a row!".format(winstreak[0], winstreak[1]))

    cprint("\nServer statistics:")
    eqCount = ['', -1]
    sols = {}
    for e in equations.keys():
        if equations[e]["times"] > eqCount[1]:
            eqCount = [e, equations[e]["times"]]
        if equations[e]["solution"] in sols:
            sols[equations[e]["solution"]] += 1
        else:
            sols[equations[e]["solution"]] = 1

    if eqCount[1] != -1:
        wprint("Most commonly shown equation is {0} with {1} times shown!".format(eqCount[0], eqCount[1]))
    if not sols:
        maxSol = ['', -1]
        for s in sols.keys():
            if sols[s] > maxSol[1]:
                maxSol = [s, sols[s]]
        wprint("Most common solution for an equation is {0} which was shown {1} times!".format(maxSol[0], maxSol[1]))
    
    cprint("")
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