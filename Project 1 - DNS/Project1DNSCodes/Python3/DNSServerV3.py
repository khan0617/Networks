# Spring 2023 CSci4211: Introduction to Computer Networks
# This program serves as the server of DNS query.
# Written in Python v3.

import sys, threading, os, random
from socket import *

def main():
	host = "localhost" # Hostname. It can be changed to anything you desire.
	port = 5001 # Port number.

	#create a socket object, SOCK_STREAM for TCP

	#bind socket to the current address on port

	#Listen on the given socket maximum number of connections queued is 20
	

	monitor = threading.Thread(target=monitorQuit, args=[])
	monitor.start()

	print("Server is listening...")

	while 1:
		#blocked until a remote machine connects to the local port
		connectionSock, addr = sSock.accept()
		server = threading.Thread(target=dnsQuery, args=[connectionSock, addr[0]])
		server.start()

def dnsQuery(connectionSock, srcAddress):
	#check the DNS_mapping.txt to see if the host name exists
	#set local file cache to predetermined file.
        #create file if it doesn't exist 
        #if it does exist, read the file line by line to look for a
        #match with the query sent from the client
        #If match, use the entry in cache.
            #However, we may get multiple IP addresses in cache, so call dnsSelection to select one.
	#If no lines match, query the local machine DNS lookup to get the IP resolution
	#write the response in DNS_mapping.txt
	#print response to the terminal
	#send the response back to the client
	#Close the server socket.
  
def dnsSelection(ipList):
	#checking the number of IP addresses in the cache
	#if there is only one IP address, return the IP address
	#if there are multiple IP addresses, select one and return.
	##optional: return the IP address according to the Ping value for better performance (lower latency)

def monitorQuit():
	while 1:
		sentence = input()
		if sentence == "exit":
			os.kill(os.getpid(),9)

main()
