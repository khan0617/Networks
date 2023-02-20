# Spring 2023 CSci4211: Introduction to Computer Networks
# This program serves as the server of DNS query.
# Written in Python v3.
# Authors: 
# 	Skeleton provided by CSCI 4211 staff.
#	Hamza Khan

import sys, threading, os, random, json
import fcntl, csv
from socket import *
from typing import List, Tuple

DNS_CACHE = None
DNS_CACHE_FILENAME = 'DNS_CACHE.json'
SERVER_LOG_FILENAME = 'dns-server-log.csv'

def main():
	host = 'localhost' # Hostname. It can be changed to anything you desire.
	port = 9889 # Port number.

	# create a socket object, SOCK_STREAM for TCP
	serverSock = socket(AF_INET, SOCK_STREAM)

	# bind socket to the current address on port
	serverSock.bind((host, port))

	# Listen on the given socket maximum number of connections queued is 20
	serverSock.listen(20)

	monitor = threading.Thread(target=monitorQuit, args=[])
	monitor.start()

	print('Server is listening...')

	while 1:
		# blocked until a remote machine connects to the local port
		connectionSock, addr = serverSock.accept()
		server = threading.Thread(target=dnsQuery, args=[connectionSock, addr[0]])
		server.start()

def dnsQuery(connectionSock: socket, srcAddress: Tuple[str, str]):
	global DNS_CACHE

	# check the DNS_CACHE to see if the host name exists
	ipAddrs = []
	clientHostname, clientPort = connectionSock.getpeername()
	if clientHostname in DNS_CACHE:
		ipAddrs = DNS_CACHE[clientHostname]
	else:
		pass

	bestIp = dnsSelection(ipAddrs)

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
	pass
  
def dnsSelection(ipList: List[str]):
	#checking the number of IP addresses in the cache
	#if there is only one IP address, return the IP address
	if len(ipList) == 1:
		return ipList[0]
	# TODO
	#if there are multiple IP addresses, select one and return.
	##optional: return the IP address according to the Ping value for better performance (lower latency)
	pass

def monitorQuit() -> None:
	while 1:
		sentence = input()
		if sentence == 'exit':
			updateDNSCache()
			os.kill(os.getpid(),9)

def loadDNSCache() -> None:
	"""Load the DNS_CACHE global variable with the contents of the
	DNS_CACHE.json file. Each key: value pair is as follows: \n
	{hostname: [ipaddr1, ipaddr2, ...]}"""
	global DNS_CACHE

	if not os.path.isfile(DNS_CACHE_FILENAME):
		DNS_CACHE = {}

	else:
		with open(DNS_CACHE_FILENAME) as f:
			DNS_CACHE = json.load(f)

def updateDNSCache() -> None:
	"""Update the DNS_CACHE.json file with the up to date
	DNS_CACHE global variable. Call this before exiting the program."""
	with open(DNS_CACHE_FILENAME, 'w') as f:
		fcntl.flock(f, fcntl.LOCK_EX)
		json.dump(DNS_CACHE, f)
		fcntl.flock(f, fcntl.LOCK_UN)

def updateServerLog(hostname: str, answer: str, resolution: str) -> None:
	"""Update the server log file in the following format:\n
	www.google.com,172.217.0.164,API"""

	with open(SERVER_LOG_FILENAME, 'a', newline='') as f:
		# lock the file and write one row to it
		fcntl.flock(f, fcntl.LOCK_EX)
		writer = csv.writer(f)
		writer.writerow([hostname, answer, resolution])
		fcntl.flock(f, fcntl.LOCK_UN)

if __name__ == "main":
	loadDNSCache()
	main()
