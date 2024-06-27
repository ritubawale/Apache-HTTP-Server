#!/usr/bin/python3
from socket import *

serverName = '127.0.0.1'
serverPort = 8080
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

print("------------------Client Side--------------------")

while True:
	print("Client:")
	client_input = ''
	line = input()
	while line != '':
		client_input = client_input + line + '\n'
		line = input()
	clientSocket.send(client_input.encode())
	if client_input.lower() == "quit":
		break

	server_input = clientSocket.recv(1024)
	file_content = clientSocket.recv(1024)
	print("Server:")
	print(server_input.decode())
	print(file_content.decode())


