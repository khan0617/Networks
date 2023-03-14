from pj2.simulator import sim
from pj2.simulator import to_layer_three
from pj2.event_list import evl
from pj2.packet import *
from pj2.circular_buffer import circular_buffer

class A:
    def __init__(self):
        # TODO: initialization of the state of A
        # self.estimated_rtt
        # ...
        self.seq=0
        return

    def A_input(self, pkt):
        # TODO: recive data from the other side
        # process the ACK, NACK from B
        return

    def A_output(self, m):
        # TODO: called from layer 5, pass the data to the other side
        pkt = packet(seqnum=self.seq, payload=m)
        to_layer_three("A", pkt)

    def A_handle_timer(self):
        # TODO: handler for time interrupt
        # resend the packet as needed
        return


a = A()
