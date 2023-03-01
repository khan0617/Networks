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
DNS_CACHE_FILENAME = "DNS_MAPPING.txt"
SERVER_LOG_FILENAME = "dns-server-log.csv"
DEBUG_MESSAGES = True


def main():
    host = "localhost"  # Hostname. It can be changed to anything you desire.
    port = 9889  # Port number.

    # create a socket object, SOCK_STREAM for TCP
    serverSock = socket(AF_INET, SOCK_STREAM)

    # bind socket to the current address on port
    serverSock.bind((host, port))

    # Listen on the given socket, maximum number of connections queued is 20
    serverSock.listen(20)

    monitor = threading.Thread(target=monitorQuit, args=[])
    monitor.start()

    print("Server is listening...")
    displayHelpMessage()

    while 1:
        # blocked until a remote machine connects to the local port
        connectionSock, addr = serverSock.accept()
        server = threading.Thread(target=dnsQuery, args=[connectionSock, addr[0]])
        server.start()


def debugMsg(msg: str, indent: bool = False) -> None:
    """Log a msg to the console. If indent is true, add an indent to the text."""
    if not DEBUG_MESSAGES:
        return

    if indent:
        print(f"    {msg}")
    else:
        print(f"{msg}")


def displayHelpMessage() -> None:
    """Show all available commands when the user types help."""
    indent = "    "
    message = (
        "\nProgram options:\n"
        + f"{indent}exit - Terminate the program\n"
        + f"{indent}help - Show this message again\n"
        + f"{indent}clear cache - Clear the DNS Cache (reset DNS_CACHE.json)\n"
        + f"{indent}clear log - Clear the server log (reset dns-server-log.csv)\n"
        + f"{indent}debug - Toggle debug output (default is ON)\n"
    )
    print(message)


def dnsQuery(connectionSock: socket, srcAddress: Tuple[str, str]) -> None:
    """Given a connection socket to a client, receive a domainName from them,
    query the local DNS cache and local DNS server (if necessary),
    and send the ip address back to the client via sockets. \n
    This function will close the connectionSock."""
    global DNS_CACHE
    debugMsg(
        "\nIn dnsQuery(), waiting for message from client. Type exit to terminate."
    )

    # actually receive the domain name from the client
    # the client should send over something like "www.google.com"
    domainName = connectionSock.recv(1024).decode()
    debugMsg(f"Server received {domainName} from client.", indent=True)

    # we'll need to build a response like "<hostname>:<answer>:<how request was resolved>"
    responseHostname = domainName
    responseAnswer = ""
    responseResolutionMethod = ""

    # check the DNS_CACHE to see if the host name exists
    ipAddrs = []
    if domainName in DNS_CACHE:
        debugMsg(f"Cache HIT!", indent=True)
        responseResolutionMethod = "CACHE"
        ipAddrs = DNS_CACHE[domainName]

    # query the DNS and add it to the cache.
    else:
        debugMsg(f"Cache MISS.", indent=True)
        try:
            _, _, ipAddrs = gethostbyname_ex(domainName)
            DNS_CACHE[domainName] = ipAddrs

        except gaierror as e:
            debugMsg(f"Error: Failed to resolve {domainName}: {e}", indent=True)
            DNS_CACHE[domainName] = ["Host not found"]

        finally:
            responseResolutionMethod = "API"
            updateDNSCache(indentDebugMsg=True)

    # build and send the message to the client.
    responseAnswer = dnsSelection(ipAddrs) if ipAddrs else "Host not found"
    message = f"{responseHostname}:{responseAnswer}:{responseResolutionMethod}"
    debugMsg(f"Sending this message to client: {message}", indent=True)

    # send the response back to the client
    messageBytes = message.encode("utf-8")
    connectionSock.send(messageBytes)

    # write the message to the server's log file.
    updateServerLog(responseHostname, responseAnswer, responseResolutionMethod)

    # Close the server socket.
    connectionSock.close()


def dnsSelection(ipList: List[str]) -> str:
    """Given a list of ip addresses, return the best one,
    determined by ping latency."""
    # debugMsg("Selecting best IP address to return in dnsSelection()", indent=True)
    # If there's only one IP address, return it directly
    if len(ipList) == 1:
        return ipList[0]

    # compare all ips' latency and pick the lowest one.
    bestIp = ipList[0]
    bestLatency = math.inf
    for ip in ipList:
        latency = getPingLatency(ip)
        debugMsg(f"ip addr {ip} had latency {latency}", indent=True)
        if latency < bestLatency:
            bestIp = ip
            bestLatency = latency

    debugMsg(
        f"In dnsSelection, best ip is {bestIp} with latency {bestLatency}", indent=True
    )
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
            debugMsg("Terminating server. Goodbye.")
            os.kill(os.getpid(), 9)

        elif "help" in sentence.lower():
            displayHelpMessage()

        elif "clear cache" in sentence.lower():
            clearFile(DNS_CACHE_FILENAME)

        elif "clear log" in sentence.lower():
            clearFile(SERVER_LOG_FILENAME)

        elif "debug" in sentence.lower():
            global DEBUG_MESSAGES
            DEBUG_MESSAGES = not DEBUG_MESSAGES
            print(
                "Debug messages enabled"
                if DEBUG_MESSAGES
                else "Debug messages disabled"
            )


def loadDNSCache() -> None:
    """Load the DNS_CACHE global variable with the contents of the
    DNS_CACHE.json file. Each line in the file is as follows (note the spaces and commas) \n
    hostname ipaddr1,ipaddr2,..."""
    debugMsg(f"Loading {DNS_CACHE_FILENAME} into data structure in loadDNSCache()...")
    global DNS_CACHE

    if not os.path.isfile(DNS_CACHE_FILENAME):
        DNS_CACHE = {}

    else:
        # each line in the cache is similar to the following:
        # www.google.com 142.250.191.164,142.250.191.142,...
        # there may only be one 
        with open(DNS_CACHE_FILENAME) as f:
            for line in f:
                if not line:
                    continue

                key, value = line.split(" ")
                value = value.split(',')
                DNS_CACHE[key] = value


def updateDNSCache(indentDebugMsg: bool = False) -> None:
    """Update the DNS_CACHE file with the up to date
    DNS_CACHE global variable. Call this before exiting the program.
    When indentDebugMsg is true, debugMsg will be called with(..., indent=True)"""
    debugMsg("Updating DNS cache in updateDNSCache()...", indent=indentDebugMsg)
    with open(DNS_CACHE_FILENAME, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        for key, value in DNS_CACHE.items():
            f.write(f"{key} {','.join(value)}\n")
        fcntl.flock(f, fcntl.LOCK_UN)


def clearFile(filename: str) -> None:
    """Reset the file specified by filename."""
    debugMsg(f"Clearing {filename}\n", indent=True)
    global DNS_CACHE

    if filename == DNS_CACHE_FILENAME:
        DNS_CACHE = {}
        with open(filename, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write("")
            fcntl.flock(f, fcntl.LOCK_UN)

    elif filename == SERVER_LOG_FILENAME:
        # write an empty row, and don't add any newlines to the csv.
        with open(filename, "w", newline="") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write("")
            fcntl.flock(f, fcntl.LOCK_UN)


def updateServerLog(hostname: str, answer: str, resolution: str) -> None:
    """Update the server log file in the following format:\n
    www.google.com,172.217.0.164,API"""
    debugMsg("Updating server log in updateServerLog()...", indent=True)
    with open(SERVER_LOG_FILENAME, "a", newline="") as f:
        # lock the file and write one row to it
        fcntl.flock(f, fcntl.LOCK_EX)
        writer = csv.writer(f)
        writer.writerow([hostname, answer, resolution])
        fcntl.flock(f, fcntl.LOCK_UN)


if __name__ == "__main__":
    loadDNSCache()
    main()
