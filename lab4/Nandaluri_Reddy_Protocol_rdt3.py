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

        #timeout variables
        self.timeout_value = 3 *2
        self.timer_state = 0 #0 reprsents timer is off
        self.timer = None


        self.start_time = 0
        self.end_time = 0
        self.total_time = 0

    def timer_behavior(self):
        try:
            self.timer_state = 1
            yield self.env.timeout(self.timeout_value)
            self.timer_state = 0
            self.timeout_resend()
        except simpy.Interrupt:
            self.timer_state = 0
    
    def start_timer(self):
        assert(self.timer_state == 0)
        self.timer = self.env.process(self.timer_behavior())

    def stop_timer(self):
        assert(self.timer_state == 1)
        self.timer.interrupt()

    def timeout_resend(self):
        self.channel.udt_send(self.packet_to_be_sent)
        self.start_timer()

    def rdt_send(self,msg):
        if self.state==WAITING_FOR_CALL_FROM_ABOVE_0:
            self.start = time.time()
			# create a packet, and save a copy of this packet
			# for retransmission, if needed
            self.packet_to_be_sent = Packet(seq_num=0, payload=msg)
			#introducing delay
            #self.channel.delay = random.randint(10, 50)
			# send it over the channel
            #self.channel.udt_send(self.packet_to_be_sent)
			# wait for an ACK 0
            self.state=WAIT_FOR_ACK_0
            self.start_timer()
            return True
        elif self.state == WAITING_FOR_CALL_FROM_ABOVE_1:
            # create a packet, and save a copy of this packet
			# for retransmission, if needed
            self.start_time = time.time()
            self.packet_to_be_sent = Packet(seq_num=1, payload=msg)
			#introducing delay
            #self.channel.delay = random.randint(10, 50)
			# send it over the channel
            self.channel.udt_send(self.packet_to_be_sent)
			# wait for an ACK 1
            self.state=WAIT_FOR_ACK_1
            self.start_timer()
            return 1
        else:
            return 0

	
    def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		# when an ACK0  or ACK 1 arrives
        #assert(self.state==WAIT_FOR_ACK_0 or self.state == WAIT_FOR_ACK_1)

        if (packt.corrupted and (self.state == WAIT_FOR_ACK_0 or self.state== WAIT_FOR_ACK_1)) :
			#resend the packet
            pass

		#if rdt_rcv receive ACK_0
        elif(packt.payload=="ACK" and packt.seq_num==0):
			#if the sender is waiting for ACK_0			
            if self.state == WAIT_FOR_ACK_0:
				#change the state
                self.end_time = time.time()
                self.total_time += self.end_time - self.start_time
                self.state=WAITING_FOR_CALL_FROM_ABOVE_1
                self.stop_timer()
			#if the sender is waiting for ACK_1

            elif self.state == WAIT_FOR_ACK_1:
                pass
            else:
                print("Invalid State!")
		#if we  receive ACK_1		
        elif(packt.payload=="ACK" and packt.seq_num==1):
			#if the sender is waiting for ACK_0			
            if self.state == WAIT_FOR_ACK_0:
				#resend the packet				
                pass
                #self.channel.udt_send(self.packet_to_be_sent)
			#if the sender is waiting for ACK_1
            elif self.state == WAIT_FOR_ACK_1:
				#change the state
                self.end_time = time.time()
                self.total_time += self.end_time - self.start_time
                self.state = WAITING_FOR_CALL_FROM_ABOVE_0
                self.stop_timer()
        

            else:
                print("Invalid State!")
                print("Halting Simulation !")
                sys.exit(0)
        #timeout occured.
        elif self.state == WAIT_FOR_ACK_0 or self.state == WAIT_FOR_ACK_1:
            self.channel.udt_send(self.packet_to_be_sent)
            self.start_timer()
        else:
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
                
            elif (packt.seq_num == 1) :
                #sending ACK 1
                response = Packet(payload="ACK",seq_num =1)
                self.channel.udt_send(response)
                if self.state == WAITING_FOR_CALL_FROM_BELOW_1 :
                    #recived expected packet
                    self.receiving_app.deliver_data(packt.payload)
                    self.state = WAITING_FOR_CALL_FROM_BELOW_0
            else:
                print("Invalid State!")
                print("Halting Simulation !")

        else:
            print("ERROR! rdt_rcv() did not receive any packet.")
            print("Halting simulation...")
            sys.exit(0)
        


