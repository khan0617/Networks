# CSCI 4211
# Authors:
    # Hamza Khan
    # CSCI 4211 S23 staff
# A.py creates a class A which allows A<->B communication.
# This is the Go Back N implementation.

from pj2.simulator import sim
from pj2.simulator import to_layer_three
from pj2.event_list import evl
from pj2.packet import packet, checksum_valid
from pj2.circular_buffer import circular_buffer
from pj2.msg import msg

class A:
    def __init__(self, *, debug_msgs: bool = False, buffer_size: int = 8, estimated_rtt: int = 30):
        self.base_seqnum = 0 # the oldest sequence # in the window
        self.next_pkt_seqnum = 0 # the sequence # of the next packet we'll send
        self.buffer = circular_buffer(buffer_size) # buffer to manage packets in current window
        self.estimated_rtt = estimated_rtt # timer delay
        self.event_list = evl # event list to manage timers
        self.timer_started = False # keep track if a timer has been started.
        self.debug_msgs = debug_msgs # when True, debugging print statements will be shown.
        self.dbg_num = 0 # debug message number
    
    def A_output(self, m: msg):
        """Send a packet to B and update the sender buffer."""
        # If the buffer is full, just drop the packet
        if self.buffer.isfull():
            self.show_debug_msg(f'**A{self.dbg_num}** Buffer is full. Dropping packet with data {m.data}...')
            return
        
        # construct the packet based on the message. Make sure that the sequence number is correct
        # send the packet and save it to the circular buffer using "push()" of circular_buffer
        pkt = packet(self.next_pkt_seqnum, payload=m)
        self.show_debug_msg(f'**A{self.dbg_num}** In A_input() Sending packet with data {m.data}...')
        self.buffer.push(pkt)
        to_layer_three("A", pkt)

        # update the next packet's sequence number.
        self.next_pkt_seqnum += 1

        # Set the timer and make sure that there is only one timer started in the event list.
        self.A_restart_timer()

    def A_input(self, pkt: packet):
        """Receive a packet from B, verify it. Resend old packets and update the buffer accordingly."""
        # go back n, A_input
        # Verify that the packet is not corrupted
        if not checksum_valid(pkt):
            self.show_debug_msg(f'**A{self.dbg_num}** Invalid checksum from b. Discarding...')
            return
        
        # received ACK from B for the base of our window. Remove oldest item from buffer and slide window over.
        if pkt.acknum >= self.base_seqnum:
            # update self.base_seqnum and buffer accordingly. We may have a scenario where B get's packets with seqnum 0 AND 1 before we get the 1st ACK.
            if pkt.acknum == self.base_seqnum:
                self.base_seqnum += 1
                self.show_debug_msg(f'**A{self.dbg_num}** Received ACK from B for seqnum {pkt.acknum}. Base seqnum is now {self.base_seqnum}...')
                self.pop_oldest_buffer_item()

            else:
                # ex: base_seqnum is 1 (for bbb). We just got acknum 2 (for ccc), meaning B has received packets with (bb) and (ccc) data. Let's bump base_seqnum up to 3 (for ddd).
                    # we then also have to remove bbb and ccc packets from the buffer. 
                    # We want to remove ((pkt.acknum==2) - (base_seqnum==1) + 1) # of packets from the buffer.
                for i in range(pkt.acknum - self.base_seqnum + 1):
                    self.pop_oldest_buffer_item()
                self.base_seqnum = pkt.acknum + 1
            
        # received NAK from B. We need to resend starting from the oldest packet again.
        elif pkt.acknum == self.base_seqnum - 1:
            self.show_debug_msg(f'**A{self.dbg_num}** Received NAK from B with acknum {pkt.acknum}. Resending...')
            self.resend_packets()
            self.A_restart_timer()

        else: # pkt.acknum < self.base_seqnum - 1
            self.show_debug_msg(f'**A{self.dbg_num}** Received old ACK from B with acknum {pkt.acknum}. Discarding...')

    def A_restart_timer(self):
        """Clear and restart the timer for A."""
        if self.timer_started:
            self.event_list.remove_timer()
        self.event_list.start_timer("A", self.estimated_rtt)
        self.timer_started = True

    def A_handle_timer(self):
        """Read all the sent packet that it is not acknowledged using "read_all()" of the circular buffer and resend them."""
        # resend all packets and update the timer.
        self.resend_packets(timer_interrupt=True)
        self.event_list.start_timer("A", self.estimated_rtt)
        self.timer_started = True

    def resend_packets(self, timer_interrupt: bool = False):
        """Resend all packets in the buffer in order to B."""
        message = f'**A{self.dbg_num}** In resend_packets() {"due to timer interrupt" if timer_interrupt else ""}, sending these packets:\n'
        packets_in_buffer = self.buffer.read_all()
        if not packets_in_buffer:
            return
        
        for idx, packet in enumerate(packets_in_buffer):
            if idx == len(packets_in_buffer) - 1:
                message += f'   pkt{idx} data: {packet.payload.data}, seqnum: {packet.seqnum}'
            else:
                message += f'   pkt{idx} data: {packet.payload.data}, seqnum: {packet.seqnum}\n'
            to_layer_three("A", packet)
        self.show_debug_msg(message)

    def pop_oldest_buffer_item(self) -> packet:
        """Get the oldest item in the circular buffer. It is popped from the buffer."""
        oldest_item = self.buffer.buffer[self.buffer.read]
        self.buffer.pop()
        self.show_debug_msg(f'**A{self.dbg_num}** Removed oldest pkt from buffer with data {oldest_item.payload.data}.')
        return oldest_item

    def show_debug_msg(self, message: str) -> None:
        """Print the message to the screen if self.debug_msgs is True (and increment self.dbg_num) else do nothing."""
        if self.debug_msgs:
            print(message)
            self.dbg_num += 1

a = A()
