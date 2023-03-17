# CSCI 4211
# Authors:
    # Hamza Khan
    # CSCI 4211 S23 staff
# A.py creates a class A which allows A<->B communication.
# This is the Stop and Wait implementation.
#   in stop and wait, the receiver waits a "reasonable" time for ACK.

from pj2.simulator import sim
from pj2.simulator import to_layer_three
from pj2.event_list import evl
from pj2.packet import packet, checksum_valid
from pj2.circular_buffer import circular_buffer
from pj2.msg import msg

# class A handles the receiver logic.
class A:
    def __init__(self, *, debug_msgs: bool=False, timer_delay: int=20):
        """Create an A class. If debug_msgs is True, A's commands will be printed to the screen."""
        self.seqnum = 0 # current sequence number
        self.pkt_waiting_for_ack = None # The packet we're waiting to be ACKED by B
        self.timer_active = False # keep track of if we have a timer running
        self.event_list = evl # evl is defined in event_list.py
        self.timer_delay = timer_delay
        self.debug_msgs = debug_msgs
        self.dbg_num = 0

    def A_input(self, pkt: packet):
        # if the checksum is invalid, resend the previous packet.
        if not checksum_valid(pkt):
            self.show_debug_msg(f'**A{self.dbg_num}** Invalid checksum from b. Resending packet...')
            to_layer_three('A', self.pkt_waiting_for_ack)
        
        # see if we received ACK for the prev packet (acknum matches self.seqnum))
        # remove any timers, and update seqnum and previous packet.
        elif pkt.acknum == self.seqnum:
            self.show_debug_msg(f'**A{self.dbg_num}** Received ACK from B for prev packet: {self.pkt_waiting_for_ack.payload.data}. Updating seqnum, removing timers.')
            if self.timer_active:
                self.event_list.remove_timer()
                self.timer_active = False
            self.seqnum += 1

        # received a NAK. Resend old pkt and restart timer as needed.
        # elif pkt.payload.ACK_OR_NACK == "NAK" and pkt.acknum == abs(self.seqnum - 1):
        elif pkt.acknum == self.seqnum - 1:
            pkt_data = self.pkt_waiting_for_ack.payload.data if self.pkt_waiting_for_ack else 'NONE'
            self.show_debug_msg(f'**A{self.dbg_num}** Received NAK from B. Resending packet with data {pkt_data}...')
            self.send_packet_and_restart_timers(self.pkt_waiting_for_ack)


    def A_output(self, m: msg):
        # TODO: called from layer 5, pass the data to the other side
        # create a new packet, restart timer, and send it.
        pkt = packet(seqnum=self.seqnum, payload=m)
        self.pkt_waiting_for_ack = pkt
        self.show_debug_msg(f'**A{self.dbg_num}** In A_output, sending {pkt.payload.data} to B')
        self.send_packet_and_restart_timers(pkt)

    def send_packet_and_restart_timers(self, pkt: packet):
        # turn off the timer if necessary
        if self.timer_active:
            self.event_list.remove_timer()
            self.timer_active = False
        # print(f'in send_packet_and_restart: pkt is: {pkt}')

        # send the packet and start a timer
        to_layer_three("A", pkt)
        self.event_list.start_timer("A", self.timer_delay)
        self.timer_active = True

    def A_handle_timer(self):
        # TODO: handler for time interrupt
        # resend the packet as needed
        pkt_data = self.pkt_waiting_for_ack.payload.data if self.pkt_waiting_for_ack else 'NONE'
        self.show_debug_msg(f'**A{self.dbg_num}** timer interrupt, resending packet with data {pkt_data}')
        self.timer_active = False
        self.send_packet_and_restart_timers(self.pkt_waiting_for_ack)

    def show_debug_msg(self, message: str) -> None:
        """Print the message to the screen if self.debug_msgs is True (and increment self.dbg_num) else do nothing."""
        if self.debug_msgs:
            print(message)
            self.dbg_num += 1

# to enable debug messages, create "a" like this instead: a = A(debug_msgs=True)
a = A()
