'''

Kailash Reddy Nandaluri - 2003123
VishnuTejesh Movva - 2003122

'''



# SimPy model for the Reliable Data Transport (rdt) Protocol 2.2 (Using ACK and NAK)

#
# Sender-side (rdt_Sender)
#	- receives messages to be delivered from the upper layer 
#	  (SendingApplication) 
#	- Implements the protocol for reliable transport
#	 using the udt_send() function provided by an unreliable channel.
#
# Receiver-side (rdt_Receiver)
#	- receives packets from the unrealible channel via calls to its
#	rdt_rcv() function.
#	- implements the receiver-side protocol and delivers the collected
#	data to the receiving application.

# Author: Neha Karanjkar


import simpy
import random
from Packet import Packet
import sys
import time

# Here the sender is going to have 4 states where it waits for ack 0 or 1 
# and wait for call 0 or call 1
WAITING_FOR_CALL_FROM_ABOVE_0 =0
WAIT_FOR_ACK_0=1
WAITING_FOR_CALL_FROM_ABOVE_1 = 2
WAIT_FOR_ACK_1 = 3


#states for receiver
WAITING_FOR_CALL_FROM_BELOW_0 = 4
WAITING_FOR_CALL_FROM_BELOW_1 = 5



class rdt_Sender(object):


    def __init__(self,env):
		# Initialize variables
        self.env=env 
        self.channel=None
		
		# some state variables
        self.state = WAITING_FOR_CALL_FROM_ABOVE_0
        self.seq_num=0
        self.packet_to_be_sent=None
	
    def rdt_send(self,msg):
        if self.state==WAITING_FOR_CALL_FROM_ABOVE_0:
			# create a packet, and save a copy of this packet
			# for retransmission, if needed
            self.packet_to_be_sent = Packet(seq_num=0, payload=msg)
			
			# send it over the channel
            self.channel.udt_send(self.packet_to_be_sent)
			# wait for an ACK 0
            self.state=WAIT_FOR_ACK_0
            return True
        elif self.state == WAITING_FOR_CALL_FROM_ABOVE_1:
            # create a packet, and save a copy of this packet
			# for retransmission, if needed
            self.packet_to_be_sent = Packet(seq_num=1, payload=msg)
			
			# send it over the channel
            self.channel.udt_send(self.packet_to_be_sent)
			# wait for an ACK 1
            self.state=WAIT_FOR_ACK_1
            return True
        else:
            return False

	
    def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		# when an ACK0  or ACK 1 arrives
        assert(self.state==WAIT_FOR_ACK_0 or self.state == WAIT_FOR_ACK_1)

        if (packt.corrupted and (self.state == WAIT_FOR_ACK_0 or self.state== WAIT_FOR_ACK_1)) :
			#resend the packet
            self.channel.udt_send(self.packet_to_be_sent)
		#if rdt_rcv receive ACK_0
        elif(packt.payload=="ACK" and packt.seq_num==0):
			#if the sender is waiting for ACK_0			
            if self.state == WAIT_FOR_ACK_0:
				#change the state
                self.state=WAITING_FOR_CALL_FROM_ABOVE_1
			#if the sender is waiting for ACK_1
            elif self.state == WAIT_FOR_ACK_1:
				#resend the packet
                self.channel.udt_send(self.packet_to_be_sent)

		#if we  receive ACK_1		
        elif(packt.payload=="ACK" and packt.seq_num==1):
			#if the sender is waiting for ACK_0			
            if self.state == WAIT_FOR_ACK_0:
				#resend the packet				
                self.channel.udt_send(self.packet_to_be_sent)
			#if the sender is waiting for ACK_1
            elif self.state == WAIT_FOR_ACK_1:
				#change the state
                self.state = WAITING_FOR_CALL_FROM_ABOVE_0
        else:
            print("ERROR! rdt_rcv() was expecting an ACK_0 or ACK_1 but did not receive any packet.")
            print("Halting simulation...")
            sys.exit(0)

			

class rdt_Receiver(object):
    def __init__(self,env):
		# Initialize variables
        self.env=env 
        self.receiving_app=None
        self.channel=None
		
        #New
        self.state= WAITING_FOR_CALL_FROM_BELOW_0
        self.state = WAITING_FOR_CALL_FROM_BELOW_1
        self.seq_num = 0

    def rdt_rcv(self,packt):
		# This function is called by the lower-layer when a packet arrives
		# at the receiver
        assert(self.state == WAITING_FOR_CALL_FROM_BELOW_0 or self.state == WAITING_FOR_CALL_FROM_BELOW_1)


		# check whether the packet is corrupted
        if(packt.corrupted):

            if self.state == WAITING_FOR_CALL_FROM_BELOW_1:
                response = Packet(payload = "ACK",seq_num =0)
                self.channel.udt_send(response)
            else:
                response = Packet(payload = "ACK",seq_num =1)
                self.channel.udt_send(response)
			
    
        elif ((packt.seq_num == 0) or (packt.seq_num ==1)):
            if (packt.seq_num == 0) :
                #sending ACK 0
                response = Packet(payload ="ACK",seq_num = 0)
                self.channel.udt_send(response)
                if self.state == WAITING_FOR_CALL_FROM_BELOW_0 :
                    #recieved expected packet
                    self.receiving_app.deliver_data(packt.payload)
                    self.state = WAITING_FOR_CALL_FROM_BELOW_1
                
            else:
                #sending ACK 1
                response = Packet(payload="ACK",seq_num =1)
                self.channel.udt_send(response)
                if self.state == WAITING_FOR_CALL_FROM_BELOW_1 :
                    #recived expected packet
                    self.receiving_app.deliver_data(packt.payload)
                    self.state = WAITING_FOR_CALL_FROM_BELOW_0

        else:
            print("ERROR! rdt_rcv() did not receive any packet.")
            print("Halting simulation...")
            sys.exit(0)
        


