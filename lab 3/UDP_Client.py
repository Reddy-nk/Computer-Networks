# This is the client program that uses UDP

# Sequence:
#
# 1. Create a socket
# 2. Send messages to it
# (We need to know the server's hostname and port.)

import socket
import time, random

# create a socket
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# The first argument should be AF_INET
	# The second argument is SOCK_STREAM for TCP service
	#    and SOCK_DGRAM for UDP service

host='10.196.6.23'
port=43387  # this is the server's port number, which the client needs to know

# send some bytes (encode the string into Bytes first)
message = "I could tell you a UDP joke but I'm not sure you'll get it."
s.sendto( message.encode('utf-8'), (host,port))


# see if the other side responds
data, addr = s.recvfrom(1024) # buffer size is 1024 bytes
print("Client received MESSAGE=",data.decode()," from ADDR=",addr)

while (True) :
	print()
	time.sleep(random.uniform(1,2))
	message = random.choice(["SEND_DATE", "SEND_TIME"])
	print("Client sent MESSAGE=",message)
	s.sendto(message.encode('utf-8'), (host,port))

	data, addr = s.recvfrom(1024) # buffer size is 1024 bytes
	print("Client received MESSAGE=",data.decode()," from ADDR=",addr)
# close the connection
s.close()
