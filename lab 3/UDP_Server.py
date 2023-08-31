# This is the Server program that uses UDP
#
# Sequence of steps:
#	1. create a socket  
#	2. bind the socket to a host and port address
#	3. start sending and receiving data on this socket


import socket
from datetime import datetime

#  create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# The first argument should be AF_INET
	# The second argument is SOCK_STREAM for TCP service
	#    and SOCK_DGRAM for UDP service

# bind it to a host and a port
host = '10.196.6.23'
port = 43387  # arbitrarily chosen non-privileged port number
s.bind((host,port))

print("Server started...waiting for a connection from the client")

# receive some bytes and print them
data, addr = s.recvfrom(1024) # buffer size is 1024 bytes
print("Server received MESSAGE=",data.decode(),"from ADDR=",addr)

#send something back
s.sendto("Ok".encode('utf-8'), (addr[0], addr[1]))

while (True) :
	print()
	data, addr = s.recvfrom(1024)
	print("Server received MESSAGE=",data.decode(),"from ADDR=",addr)
	date_time = datetime.now()
	date_time = datetime.isoformat(date_time)
	if (data.decode() == "SEND_DATE") :
		message = date_time[0:10]
		print("Server sent MESSAGE=",message)
		s.sendto(message.encode('utf-8'), (addr[0], addr[1]))
	elif (data.decode() == "SEND_TIME") :
		message = date_time[11:19]
		print("Server sent MESSAGE=",message)
		s.sendto(message.encode('utf-8'), (addr[0],addr[1]))

# close the connection
s.close()
