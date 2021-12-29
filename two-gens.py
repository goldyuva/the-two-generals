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

#broadcast port
brPort = 13117
#TCP connection port
tcpPort = [0]
#struct string format
strFormat = '>IBH'
#TCP cnnection address tuple
tcpAddr = (host, tcpPort[0])
#max user size for the program to receive
MAX_USER_SIZE = 2
#list of threads
thread = [None] * MAX_USER_SIZE
#list of user names
names = [None] * MAX_USER_SIZE
#buffer size
bufSize = 1024
#winner
winner = [None]
#sleep time
SLEEP_TIME_UNTIL_START = 10
#client address list
client_address = [None] * MAX_USER_SIZE
#boolean that signifies if threads finished execution
finish_threads_execution = False

#colors for all prints except sprint
colors = ['\033[95m', '\033[94m', '\033[96m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m', '\033[4m']
#background color for wprint
backgrounds = ['\u001b[41;1m']
#rainbow colors for sprint
rainbow = ['\x1b[1;{0};40m']
#index for rotating cprint
index = [0]

#players dictionary for statistics
players = {}
#equations dictionary for statistics
equations = {}

#intialize tcp socket for connecting to client
tcpRecvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    #bind to ip address
    tcpRecvSocket.bind(tcpAddr)
    #initializing port with random OS port
    tcpPort[0] = tcpRecvSocket.getsockname()[1]
except socket.error as e:
    eprint(e)

#listen for users
tcpRecvSocket.listen(5)

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

#print in green bold text
def tprint(s):
    print(colors[3] + colors[8] + colors[7] + s + colors[6])

#print winners with backgrounds
def wprint(s):
    print(backgrounds[0] + colors[4] + colors[7] + colors[8] + s + colors[6])

#print errors in red
def eprint(s):
    print(colors[5] + colors[8] + colors[7] + s + colors[6])

#generate addition equation with random numbers
def generateAdd():
    input1 = random.randint(1, 9)
    input2 = random.randint(0, 9 - input1)
    return "{0}+{1}".format(input1, input2), input1+input2

#generate multiplication equation with random numbers
def generateMult():
    input1 = random.randint(1,3)
    input2 = random.randint(0, int(9/input1))
    return "{0}*{1}".format(input1, input2), input1*input2

#generate factorial equation with random numbers
def generateFact():
    input1 = random.randint(0,3)
    return "{0}!".format(input1), math.factorial(input1)

#generate power equation with random numbers
def generatePower():
    input1 = random.randint(1, 3)
    input2 = random.randint(0, 2)
    return "{0}^{1}".format(input1, input2), input1**input2

#generate equation from all methods above
def generateEquation():
    #method bank
    funGen = [generateAdd, generateMult, generateFact, generatePower]
    idx = random.randint(0, len(funGen) - 1)
    #return activation of function from the above functions
    return funGen[idx]()

#add player statistics
def add_player_stats():
    #for each player in current players list
    for name in names:
        #initialize values
        nwins = 0
        winstr = 0
        total = 0
        #giving players actual values if they exist
        if name in players:
            nwins = players[name]['wins']
            winstr = players[name]['winstreak']
            total = players[name]['totalgames']
        #if the player is the winner this round
        if name == winner[0]:
            nwins += 1
            winstr += 1
        total += 1
        #add the player to the dictionary
        players[name] = {'wins': nwins, 'winstreak': winstr, 'totalgames': total}

#add server statistics
def add_server_stats(eq, sol):
    #if equation was already written before, change it's values
    if eq in equations:
        equations[eq] = {'times': equations[eq]["times"] + 1, 'solution': sol}
    #else, add new instance to the dictionary
    else:
        equations[eq] = {'times': 1, 'solution': sol}

def start_game(connection, equation, solution, names, index):
    #if no error occured
    if not finish_threads_execution:
        connection.send(equation.encode())
    #answer holds if we recieved an answer from the connection
    answer, _, _ = select.select([connection], [], [], 1)
    while winner[0] == None and finish_threads_execution == False:
        #if there is currently an answer in queue
        if connection in answer:
            #decode the answer
            ans = connection.recv(bufSize).decode()
            #if the answer equals the solution, update the winner to the current player
            if ans == str(solution):
                winner[0] = names[index]
            #else, update the winner to be the other player
            else:
                winner[0] = names[1 - index]
        try:
            #loop again
            answer, _, _ = select.select([connection], [], [], 1)
        except:
            #connection closed and there is no availible client
            eprint("Connection reset...")
    return winner

#defines the way thread that handles the client operates
def clientThread(connection, index, equation, solution, names):
    #get lock
    cv.acquire()
    try:
        #send to client welcome message
        connection.sendall(b"Welcome to Quick Maths.")
        #recieve his name
        names[index] = connection.recv(bufSize).decode()
    except:
        #if he does return the answer the connection closed
        client_address[1 - index][0].sendall("Other player disconnected.".encode())
    #release the lock
    cv.release()
    try:
        #print team name
        tprint("Team {0}: {1}".format(index + 1, names[index]))
        #start the game
        start_game(connection, equation, solution, names, index)
    except:
        pass
    return

#what the thread is supposed to do to receive connections
def recieve_Thread(cv):
    #number of clients currently connected
    clientCount = 0
    #number of threads that are supposed to be open
    thread = [None] * MAX_USER_SIZE
    #boolean that tells us if the threads finished execution
    finish_threads_execution = False
    #winner holder
    winner[0] = None
    #the equation we send to the players
    equation, solution = generateEquation()
    #acquire lock
    cv.acquire()
    sprint("Server started, listening on {0}".format(host))
    while True and clientCount < MAX_USER_SIZE:
        #accept connections
        client,address = tcpRecvSocket.accept()
        client_address[clientCount] = [client, address]
        # print client connected and his details
        cprint("connected to {0}, {1}".format(address[0], str(address[1])))
        # Start a new thread for client
        thread[clientCount] = threading.Thread(target = clientThread, args = (client, clientCount, equation, solution, names))
        # Update the number of clients
        clientCount += 1
        #print thread count
        cprint("Thread count = {0}".format(clientCount))
    tcpPort[0] = 0
    #sleep fo SLEEP_TIME_UNTIL_START seconds
    time.sleep(SLEEP_TIME_UNTIL_START)
    # And now we let the games begin
    cprint("Starting game...")
    #start threads
    for i in range (0, MAX_USER_SIZE):
        try:
            thread[i].start()
        except:
            #client disconnected
            client_address[1 - i][0].sendall("{0} disconnected", names[i])
    #release lock for other threads to start working
    cv.release()
    #start coundown
    countdown = 10
    #while we don't receive a winner
    while winner[0] == None and countdown > 0:
        time.sleep(1)
        countdown -= 1
    #if both players didn't disconnect
    if not names[0] == None and not names[1] == None:
        #if a thread sent a message
        if winner[0] == None:
            winner[0] = "it's a draw"
        #add player statistics
        add_player_stats()
        #add server statistics
        add_server_stats(equation, solution)
        #get lock
        cv.acquire()
        #update finished execution
        finish_threads_execution = True
        #print winner
        wprint("Winner: {0}".format(winner[0]))
        #create summary
        summary = "Thanks to both teams: {0}, {1}.\nAnd the winner is...\n{2}!!".format(names[0], names[1], winner[0])
        for i in range (0, MAX_USER_SIZE):
            try:
                #send the client summary
                client_address[i][0].sendall(summary.encode())
                client_address[i][0].close()
                thread[i].join()
            except:
                #else the client disconnected
                eprint("Client from team: {0} disconnected.".format(names[i]))
        cv.release()

    #print player statistics
    cprint("\nPlayer statistics:")
    numOfWins = ['', -1]
    winPercentage = ['', -1]
    winstreak = ['', -1]
    #calculate players for statistics
    for p in players.keys():
        if players[p]["wins"] > numOfWins[1]:
            numOfWins = [p, players[p]["wins"]]
        if players[p]["wins"]/players[p]["totalgames"] > winPercentage[1]:
            winPercentage = [p, players[p]["wins"]/players[p]["totalgames"]]
        if players[p]["winstreak"] > winstreak[1]:
            winstreak = [p, players[p]["winstreak"]]

    #print the player with the highest number of wins
    if numOfWins[1] != -1:
        wprint("Highest number of wins: {0} with {1} wins!".format(numOfWins[0], numOfWins[1]))
    #print the player with the highest win percentage
    if winPercentage[1] != -1:
        wprint("highest win percentage: {0} with {1}% percent win rate!".format(winPercentage[0], winPercentage[1] * 100))
    #print the player with the biggest win streak
    if winstreak[1] != -1:
        wprint("biggest win streak: {0} with {1} wins in a row!".format(winstreak[0], winstreak[1]))

    #print server statistics
    cprint("\nServer statistics:")
    eqCount = ['', -1]
    sols = {}
    #calculate equations and solutions
    for e in equations.keys():
        if equations[e]["times"] > eqCount[1]:
            eqCount = [e, equations[e]["times"]]
        if equations[e]["solution"] in sols:
            sols[equations[e]["solution"]] += 1
        else:
            sols[equations[e]["solution"]] = 1
    
    #print the most commonly shown equation
    if eqCount[1] != -1:
        wprint("Most commonly shown equation is {0} with {1} times shown!".format(eqCount[0], eqCount[1]))
    #if the solution dictionary is not empty
    if not sols:
        maxSol = ['', -1]
        #calculate max number of times an equation was shown
        for s in sols.keys():
            if sols[s] > maxSol[1]:
                maxSol = [s, sols[s]]
        #print the most common solution to an equation
        wprint("Most common solution for an equation is {0} which was shown {1} times!".format(maxSol[0], maxSol[1]))
    
    cprint("")
    #reassign tcp port
    tcpPort[0] = tcpRecvSocket.getsockname()[1]

def sendUDP():
    #initialize UDP socket
    udpSendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        #if we recieved a tcp port
        if tcpPort[0] != 0:
            #pack the message
            packedBr = struct.pack(strFormat, 0xabcddcba, 0x2, tcpPort[0])
            #send it
            udpSendSocket.sendto(packedBr, ('255.255.255.255', brPort))
        time.sleep(1)

#create ;pcl
cv = threading.Condition()
#create thread for sending UDP mesages every 1 second
threadUDP = threading.Thread(target = sendUDP, args = ())
#start the thread
threadUDP.start()
#recieve a thread each time to make the server continuous
while True:
    recieve_Thread(cv)