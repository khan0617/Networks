# Spring 2023 CSci4211: Introduction to Computer Networks
# This program serves as the server of DNS query.
# Written in Python v3.
# Authors:
# 	Skeleton provided by CSCI 4211 staff.
# 	Hamza Khan

import sys, threading, os, random, json
import fcntl, csv, subprocess, math
from socket import *
from typing import List, Tuple

DNS_CACHE = None
DNS_CACHE_FILENAME = "DNS_CACHE.json"
SERVER_LOG_FILENAME = "dns-server-log.csv"


def main():
    host = "localhost"  # Hostname. It can be changed to anything you desire.
    port = 9889  # Port number.

    # create a socket object, SOCK_STREAM for TCP
    serverSock = socket(AF_INET, SOCK_STREAM)

    # bind socket to the current address on port
    serverSock.bind((host, port))

    # Listen on the given socket maximum number of connections queued is 20
    serverSock.listen(20)

    monitor = threading.Thread(target=monitorQuit, args=[])
    monitor.start()

    print("Server is listening...")

    while 1:
        # blocked until a remote machine connects to the local port
        connectionSock, addr = serverSock.accept()
        server = threading.Thread(target=dnsQuery, args=[connectionSock, addr[0]])
        server.start()


def dnsQuery(connectionSock: socket, srcAddress: Tuple[str, str]) -> None:
    print("In dnsQuery()")
    global DNS_CACHE
    # we'll need to build a response like "hostname>:<answer>:<how request was resolved>"
    responseHostname = domainName
    responseAnswer = None
    responseResolutionMethod = None

    # actually receive the domain name from the client
    domainName = connectionSock.recv(1024).decode()

    # check the DNS_CACHE to see if the host name exists
    ipAddrs = []
    if domainName in DNS_CACHE:
        print(f"Found {domainName} in DNS cache.")
        responseResolutionMethod = "CACHE"
        ipAddrs = DNS_CACHE[domainName]

    # query the DNS and add it to the cache.
    else:
        try:
            ipFromDnsQuery = gethostbyname(domainName)
            DNS_CACHE[domainName] = [ipFromDnsQuery]

        except gaierror:
            print(f"Error: Failed to resolve {domainName}")
            DNS_CACHE[domainName] = ["Host not found"]

        finally:
            responseResolutionMethod = "API"
            updateDNSCache()

    # build and send the message to the client.
    responseAnswer = dnsSelection(ipAddrs) if ipAddrs else "Host not found"
    message = f"{domainName}:{responseAnswer}:{responseResolutionMethod}"
    print(f"Sending this message to client: {message}")

    # send the response back to the client
    messageBytes = message.encode("utf-8")
    connectionSock.send(messageBytes)

    # write the message to the server's log file.
    updateServerLog(domainName, responseAnswer, responseResolutionMethod)

    # Close the server socket.
    connectionSock.close()


def dnsSelection(ipList: List[str]) -> str:
    """Given a list of ip addresses, return the best one,
    determined by ping latency."""
    print("Selecting best IP address to return")
    # If there's only one IP address, return it directly
    if len(ipList) == 1:
        return ipList[0]

    # compare all ips' latency and pick the lowest one.
    bestIp = ipList[0]
    bestLatency = math.inf
    for ip in ipList:
        latency = getPingLatency(ip)
        print(f"ip addr {ip} had latency {latency}")
        if latency < bestLatency:
            bestIp = ip
            bestLatency = latency

    print(f"*** In dnsSelection, best ip is {bestIp} with latency {bestLatency}. ***")
    return bestIp


def getPingLatency(ip: str) -> float:
    """Given an ip address, ping it, and return the latency in ms."""
    ping_output = subprocess.run(
        ["ping", "-c", "1", ip], capture_output=True, text=True
    )
    latency_start = ping_output.stdout.find("time=") + len("time=")
    latency_end = ping_output.stdout.find(" ms", latency_start)
    latency = float(ping_output.stdout[latency_start:latency_end])
    return latency


def monitorQuit() -> None:
    while 1:
        sentence = input()
        if sentence == "exit":
            updateDNSCache()
            print("Terminating server. Goodbye...")
            os.kill(os.getpid(), 9)


def loadDNSCache() -> None:
    """Load the DNS_CACHE global variable with the contents of the
    DNS_CACHE.json file. Each key: value pair is as follows: \n
    {hostname: [ipaddr1, ipaddr2, ...]}"""
    print(f"Loading {DNS_CACHE_FILENAME} into data structure...")
    global DNS_CACHE

    if not os.path.isfile(DNS_CACHE_FILENAME):
        DNS_CACHE = {}

    else:
        with open(DNS_CACHE_FILENAME) as f:
            DNS_CACHE = json.load(f)


def updateDNSCache() -> None:
    """Update the DNS_CACHE.json file with the up to date
    DNS_CACHE global variable. Call this before exiting the program."""
    print("Updating DNS cache...")
    with open(DNS_CACHE_FILENAME, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(DNS_CACHE, f)
        fcntl.flock(f, fcntl.LOCK_UN)


def updateServerLog(hostname: str, answer: str, resolution: str) -> None:
    """Update the server log file in the following format:\n
    www.google.com,172.217.0.164,API"""
    print("Updating server log...")
    with open(SERVER_LOG_FILENAME, "a", newline="") as f:
        # lock the file and write one row to it
        fcntl.flock(f, fcntl.LOCK_EX)
        writer = csv.writer(f)
        writer.writerow([hostname, answer, resolution])
        fcntl.flock(f, fcntl.LOCK_UN)


if __name__ == "__main__":
    loadDNSCache()
    main()
