from pj2.simulator import sim
from pj2.simulator import to_layer_three
from pj2.event_list import evl
from pj2.packet import *
from pj2.circular_buffer import circular_buffer

class A:
    def __init__(self):
        # go back n, the initialization of A
        # Initialize the initial sequence number to 0.
        # You need to initialize the circular buffer, using "circular_buffer(max)". max is the number of the packets that the buffer can hold
        # You can set the estimated_rtt to be 30, which is used as a parameter when you call start_timer
    
    def A_output(self, m):
        # go back n, A_output
        # If the buffer is full, just drop the packet
        # Construct the packet based on the message. Make sure that the sequence number is correct
        # Send the packet and save it to the circular buffer using "push()" of circular_buffer
        # Set the timer using "evl.start_timer(entity, time)", and the time should be set to estimated_rtt. Make sure that there is only one timer started in the event list

    def A_input(self, pkt):
        # go back n, A_input
        # Verify that the packet is not corrupted
        # Update the circular buffer according to the acknowledgement number using "pop()"


    def A_handle_timer(self):
        # go back n, A_handle_timer
        # Read all the sent packet that it is not acknowledged using "read_all()" of the circular buffer and resend them
        # If you need to resend packets, set a timer after that


a = A()
