# This is the Server program
#
# Sequence of steps:
#	1. create a "welcome" socket for listening to new connections 
#	2. bind the socket to a host and port
#	3. start listening on this socket for new connections
#	4. accept an incoming connection from the client
#   5. send and receive data over the "connection" socket


from ast import operator
import socket

#  create a socket for listening to new connections
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# use SOCK_STREAM for TCP
				# use SOCK_DGRAM for UDP

# bind it to a host and a port
host = '10.196.6.23'
port = 43389  # arbitrarily chosen non-privileged port number
s.bind((host,port))
print("Server started...waiting for a connection from the client")

# start listening for TCP connections made to this socket
# the argument "1" is the max number of queued up clients allowed
s.listen(1) 

# accept a connection
calculator, addr = s.accept()
print("Connection initiated from ",addr)

# receive some bytes and print them
# the argument 1024 is the maximum number of characters to be read at a time
data = calculator.recv(1024)
print("SERVER RECEIVED: ", data.decode())

oper = ["+","-","*","/"]

while (True) :
	data = calculator.recv(1024)
	if (data.decode() == 'q') :
		# close the connection
		calculator.send("Connection Closed".encode('utf-8'))
		calculator.close()
		break
	
	else :
		num1, operator, num2 =(data.decode()).split()
		num1 = float(num1)
		num2 = float(num2)
		num3 = 0
		
	if operator == oper[0]:
		num3 = num1 + num2
	elif operator == oper[1]:
		num3 =  num1 - num2
	elif operator == oper[2]:
		num3 = num1 * num2
	else:
		num3 = num1 / num2
	num3 = str(num3)
	calculator.send(num3.encode('utf-8'))

