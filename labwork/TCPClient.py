from socket import *
from time import time
serverName = '127.0.0.1'
serverPort = int(input("Choose server port: "))
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
sentence = input('Input a lower case sentence : ')
clientSocket.send(sentence.encode())
print('From Server :')
start = time()
while time() < start + 1:
    modifiedSentence = clientSocket.recv(2048)
    print(modifiedSentence.decode(), end="")

clientSocket.close()

