from pj2.simulator import sim
from pj2.simulator import to_layer_three
from pj2.event_list import evl
from pj2.packet import *


class A:
    def __init__(self):
        # stop and wait, the initialization of A
        # for stop and wait, the state can be "WAIT_LAYER5" or "WAIT_ACK"
        # "WAIT_LAYER5" is the state that A waits messages from application layer.
        # "WAIT_ACK" is the state that A waits acknowledgement
        # You can set the estimated_rtt to be 30, which is used as a parameter when you call start_timer

        return

    def A_output(self, m):
        # stop and wait A_output
        # msg m is the message. It should be used as payload to construct the packet.
        # You can construct the packet using the "packet(seqnum,payload)" in "packet.py".
        # call to_layer_three(entity,pkt) to send the packet
        # save the packet so that it can be resent if needed.
        # Set the timer using "evl.start_timer(entity,time)", and the time should be set to estimated_rtt. Make sure that there is only one timer started in the event list.
        # In the end, you should change the state to "WAIT_ACK"


    def A_input(self, pkt):
        # stop and wait A_input
        # p is the packet from the B
        # first verify the checksum to make sure that packet is uncorrupted
        # then verify the acknowledgement number to see whether it is the expected one
        # if not, you may need to resend the packet.
        # if the acknowledgement is the expected one, you need to update the state of A from "WAIT_ACK" to "WAIT_LAYER5" again


    def A_handle_timer(self):
        # stop and wait A_handle_timer
        # if it is triggered, it means the packet isn't delivered
        # so you need to resend the last packet "using to_layer_three()"
        # After sending the last packet, don't forget to set the timer again


a = A()
