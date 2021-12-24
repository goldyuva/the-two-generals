import socket


# The IP address of the client
host = '127.0.0.1'

# Define the port on which you want to connect
port = 13117

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# connect to server on local computer
serverSocket.connect((host,port))

print("Client Started, listening for offer requests...")
while True:

    # messaga received from server
    data = serverSocket.recv(1024)

    # print the received message
    # here it would be a reverse of sent message
    print('Received offer from {0}, Attempting to connect'.format(str(data.decode('ascii'))))
    # Start the game
# close the connection
serverSocket.close()