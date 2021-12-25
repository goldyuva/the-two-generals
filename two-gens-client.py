import socket


# The IP address of the client
#hostname = socket.gethostname()
#host = socket.gethostbyname(hostname)
host = '127.0.0.1'

# Define the port on which you want to connect
port = 13117
addr = (host, port)

udpRecvSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, socket.IPPROTO_UDP)
udpRecvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    udpRecvSocket.bind(('', port))
except socket.error as e:
    print(e)

# connect to server on local computer
#udpRecvSocket.connect((host,port))

print("Client Started, listening for offer requests...")
# message received from server
data = udpRecvSocket.recv(1024).decode()
# print the received message
print('Received offer from {0}, Attempting to connect'.format(data))
tcpSendSocket = socket.socket()
try:
    tcpSendSocket.connect((data, port))
except socket.error as e:
    print(e)
dataReq = tcpSendSocket.recv(1024).decode()
name = input(dataReq)
tcpSendSocket.send(name.encode())
    # Start the game
# close the connection
tcpSendSocket.close()