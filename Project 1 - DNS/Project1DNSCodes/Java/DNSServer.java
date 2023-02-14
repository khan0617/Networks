/* Spring 2023 CSci4211: Introduction to Computer Networks
** This program serves as the server of DNS query.
** Written in Java. */

import java.io.*;
import java.net.*;
import java.util.Random;

class DNSServer {
	public static void main(String[] args) throws Exception {
		int port = 5001;
		ServerSocket sSock = null;

		try {
			sSock = new ServerSocket(port); // Try to open server socket 5001.
		} catch (Exception e) {
			System.out.println("Error: cannot open socket");
			System.exit(1); // Handle exceptions.
		}

		System.out.println("Server is listening...");
		new monitorQuit().start(); // Start a new thread to monitor exit signal.

		while (true) {
			new dnsQuery(sSock.accept()).start();
		}
	}
}

class dnsQuery extends Thread {
	Socket sSock = null;
    	dnsQuery(Socket sSock) {
    	this.sSock = sSock;

    }
    public String IPselection(String[] ipList){
    //checking the number of IP addresses in the cache
	//if there is only one IP address, return the IP address
	//if there are multiple IP addresses, select one and return.
	////optional: return the IP address according to the Ping value for better performance (lower latency)
    }
	@Override public void run(){
	BufferedReader inputStream;
        PrintWriter outStream;
        try {
	//Open an input stream and an output stream for the socket
	//Read requested query from socket input stream
	//Parse input from the input stream
	//Check the requested query
           
             boolean hostFound = false;
            try {
		//check the DNS_mapping.txt to see if the host name exists
		//set local file cache to predetermined file.
                //create file if it doesn't exist 
                //if it does exist, read the file line by line to look for a
                //match with the query sent from the client
                //If match, use the entry in cache.
                    //However, we may get multiple IP addresses in cache, so call IPselection to select one. 
		//If no lines match, query the local machine DNS lookup to get the IP resolution
		//write the response in DNS_mapping.txt
		//print response to the terminal
		//send the response back to the client
		//Close the server socket.
             
            
            } catch (Exception e) {
                System.out.println("exception: " + e);
            }
	//Close the input and output streams.


        } catch (IOException e) {
            e.printStackTrace();
            System.err.println("Host not found.\n" + e);
        }
	}
}

class monitorQuit extends Thread {
	@Override
	public void run() {
		BufferedReader inFromClient = new BufferedReader(new InputStreamReader(System.in)); // Get input from user.
		String st = null;
		while(true){
			try{
				st = inFromClient.readLine();
			} catch (IOException e) {
			}
            if(st.equalsIgnoreCase("exit")){
                System.exit(0);
            }
        }
	}
}
