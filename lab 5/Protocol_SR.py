# SimPy models for rdt_Sender and rdt_Receiver
# implementing the Selective Repeat.
#  Protocol

# Author: Dr. Neha Karanjkar, IIT Goa

import simpy
import random
import sys
from Packet import Packet



class rdt_Sender(object):
	
	def __init__(self,env):
		
		# Initialize variables and parameters
		self.env=env 
		self.channel=None
		
		# some default parameter values
		self.data_packet_length=10 # bits
		self.timeout_value=10 # default timeout value for the sender
		self.N=5 # Sender's Window size
		self.M = 5# Receiver's Window size
		self.K=16 # Packet Sequence numbers can range from 0 to K-1

		# some state variables and parameters for the Go-Back-N Protocol
		self.base=1 # base of the current window 
		self.nextseqnum=1 # next sequence number
		self.sndpkt= {} # a buffer for storing the packets to be sent (implemented as a Python dictionary)
		
		self.acked= [] # a list to store the packets that has been acked
		
		# some other variables to maintain sender-side statistics
		self.total_packets_sent=0
		self.num_retransmissions=0

		
		# timer-related variables
		self.timer_is_running=False
		self.timer=None

			
	
	def rdt_send(self,msg):
		# This function is called by the 
		# sending application.
			
		# check if the nextseqnum lies within the 
		# range of sequence numbers in the current window.
		# If it does, make a packet and send it,
		# else, refuse this data.

				
		if(self.nextseqnum in [(self.base+i)%self.K for i in range(0,self.N)]):
			print("TIME:",self.env.now,"RDT_SENDER: rdt_send() called for nextseqnum=",self.nextseqnum," within current window. Sending new packet.")
			# create a new packet and store a copy of it in the buffer
			self.sndpkt[self.nextseqnum]= Packet(seq_num=self.nextseqnum, payload=msg, packet_length=self.data_packet_length)
			# send the packet
			self.channel.udt_send(self.sndpkt[self.nextseqnum])
			self.total_packets_sent+=1
			
			# start the timer if required
			if(self.base==self.nextseqnum):
				self.start_timer()
			# update the nextseqnum
			self.nextseqnum = (self.nextseqnum+1)%self.K
			return True
		else:
			print("TIME:",self.env.now,"RDT_SENDER: rdt_send() called for nextseqnum=",self.nextseqnum," outside the current window. Refusing data.")
			return False
		
	
	def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		# when an ACK packet arrives
		
		if (packt.corrupted==False):
			
			# check if we got an ACK for a packet within the current window.
			if (packt.seq_num in self.sndpkt.keys()):
				self.acked.append(packt.seq_num - self.base)
				del self.sndpkt[packt.seq_num]

				print("TIME:",self.env.now,"RDT_SENDER: Got an ACK",packt.seq_num)

				print(self.acked)
				while (0 in self.acked) :
					self.base = (self.base + 1)%self.K
					self.acked = [x-1 for x in self.acked]
					self.acked.remove(-1)
				# remove the acked packet from buffer
				# and slide the window right
				
				# if there are no more packets to be acked, stop the timer.
				if(self.base==self.nextseqnum):
					self.stop_timer() # no more pending ACKs. Just stop the timer.
				else:
					self.restart_timer() # restart the timer, for a pending ACK of packet at base
				
				# exit the while loop
				print("TIME:",self.env.now,"RDT_SENDER: Got an ACK",packt.seq_num,". Updated window:", [(self.base+i)%self.K for i in range(0,self.N)],"base =",self.base,"nextseqnum =",self.nextseqnum)
			else:
				print("TIME:",self.env.now,"RDT_SENDER: Got an ACK",packt.seq_num," for a packet in the old window. Ignoring it.")

	# Finally, these functions are used for modeling a Timer's behavior.
	def timer_behavior(self):
		try:
			# Wait for timeout 
			self.timer_is_running=True
			yield self.env.timeout(self.timeout_value)
			self.timer_is_running=False
			# take some actions 
			self.timeout_action()
		except simpy.Interrupt:
			# stop the timer
			self.timer_is_running=False

	# This function can be called to start the timer
	def start_timer(self):
		assert(self.timer_is_running==False)
		self.timer=self.env.process(self.timer_behavior())
		print("TIME:",self.env.now,"TIMER STARTED for a timeout of ",self.timeout_value)

	# This function can be called to stop the timer
	def stop_timer(self):
		assert(self.timer_is_running==True)
		self.timer.interrupt()
		print("TIME:",self.env.now,"TIMER STOPPED.")
	
	def restart_timer(self):
		# stop and start the timer
		assert(self.timer_is_running==True)
		self.timer.interrupt()
		#assert(self.timer_is_running==False)
		self.timer=self.env.process(self.timer_behavior())
		print("TIME:",self.env.now,"TIMER RESTARTED for a timeout of ",self.timeout_value)


	# Actions to be performed upon timeout
	def timeout_action(self):
		
		# re-send all the packets for which an ACK has been pending
		packets_to_be_resent = list(self.sndpkt.keys())
		print("TIME:",self.env.now,"RDT_SENDER: TIMEOUT OCCURED. Re-transmitting packets",packets_to_be_resent)
		for seq_num in packets_to_be_resent:
			self.channel.udt_send(self.sndpkt[seq_num])
			self.num_retransmissions+=1
			self.total_packets_sent+=1
		
		# Re-start the timer
		self.start_timer()
		
	# A function to print the current window position for the sender.
	def print_status(self):
		print("TIME:",self.env.now,"Current window:", [(self.base+i)%self.K for i in range(0,self.N)],"base =",self.base,"nextseqnum =",self.nextseqnum)
		print("---------------------")


#==========================================================================================

class rdt_Receiver(object):
	
	def __init__(self,env):
		
		# Initialize variables
		self.env=env 
		self.receiving_app=None
		self.channel=None

		# some default parameter values
		self.ack_packet_length=10 # bits
		self.N=5 #
		self.K=16 # range of sequence numbers expected

		#initialize state variables
		self.expectedseqnum =1 #
		self.sndpkt= Packet(seq_num=0, payload="ACK",packet_length=self.ack_packet_length)
		self.buffer={}  #to store the packets that come out of order in a window
		self.total_packets_sent=0
		self.num_retransmissions=0
		self.acked = []
		

	def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		# when a packet arrives at the receiver
		
		if(packt.corrupted==False):
			print("TIME:",self.env.now,"RDT_RECEIVER: got expected packet",packt.seq_num,". Sent ACK",packt.seq_num)
			
			
			if (packt.seq_num > self.expectedseqnum and packt.seq_num < self.expectedseqnum + self.M) :
				self.sndpkt= Packet(seq_num=packt.seq_num, payload="ACK",packet_length=self.ack_packet_length)
				self.channel.udt_send(self.sndpkt)
				self.total_packets_sent+=1
				self.acked.append(packt.seq_num)
				self.receiving_app.deliver_data(packt.payload)
				print("TIME:",self.env.now,"RDT_RECEIVER: got packet",packt.seq_num,". Sent ACK",packt.seq_num)

			'''
			while (0 in self.acked) :
				# extract and deliver data
				print(reached)
				self.receiving_app.deliver_data(self.buffer[self.base]) #
				del self.buffer[self.base]
				self.base = (self.base + 1)%self.K
				self.acked = [x-1 for x in self.acked]
				self.acked.remove(-1)
	'''
		else:
			# got a corrupted or unexpected packet.
			# send the ACK for the oldest packet received successfully
			if(packt.corrupted):
				print("TIME:",self.env.now,"RDT_RECEIVER: got corrupted packet",". Sent ACK",self.sndpkt.seq_num)
		

