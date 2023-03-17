# CSCI 4211
# Authors:
    # Hamza Khan
    # CSCI 4211 S23 staff
# B.py creates a class B which allows A<->B communication.
# The Stop and Wait and Go Back N receiver (B) implementations are the same.

from pj2.simulator import to_layer_five, to_layer_three
from pj2.packet import packet, send_ack, checksum_valid

# class B will receive data from class A. Class B will send the ACKs.
class B:
    def __init__(self, *, debug_msgs: bool=False):
        """Instantiate a B (receiver) class. If debug_msgs is set to True, information will be printed to the console."""
        self.seqnum = 0
        self.debug_msgs = debug_msgs
        self.dbg_num = 0

    def B_input(self, pkt: packet):
        """Process the packet received from the layer 3.
        Verify the packet's info and send ACK/NAK through the network as needed."""
        # verify checksum
        if not checksum_valid(pkt):
            self.show_debug_msg(f'--B{self.dbg_num}-- Received corrupted (bad checksum) packet from A. Sending NAK.')
            self.B_send_nak()
            return 
        
        # B just received an old packet from A. Resend the ACK for the previous packet we received.
        if pkt.seqnum != self.seqnum:
            message = f'--B{self.dbg_num}-- Received out of order pkt from A, pkt.seqnum {pkt.seqnum if pkt else "NONE"} != self.seqnum {self.seqnum}, resending ACK with acknum {self.seqnum - 1}'
            self.show_debug_msg(message)
            send_ack("B", self.seqnum - 1)

        else:
            # send an ACK and the received data to the application side.
            self.show_debug_msg(f'--B{self.dbg_num}-- Received valid packet from A (data: {pkt.payload.data}), sending ACK with acknum {pkt.seqnum}.')
            send_ack("B", pkt.seqnum)
            to_layer_five("B", pkt.payload.data)
            self.seqnum += 1

    
    def B_send_nak(self):
        """Send a NAK packet across the network. NAKs are indicated by sending a packet with acknum== self.seqnum - 1."""
        nak_pkt = packet(acknum=self.seqnum - 1)
        to_layer_three("B", nak_pkt)

    def show_debug_msg(self, message: str) -> None:
        """Print the message to the screen if self.debug_msgs is True (and increment self.dbg_num) else do nothing."""
        if self.debug_msgs:
            print(message)
            self.dbg_num += 1

    def B_output(self, m):
        # All ACK / NAK logic is in B_input()
        return

    def B_handle_timer(self):
        # Only the sender side (A) should have a timer to resend messages.
        return


# to enable debug messages, create "b" like this instead: b = B(debug_msgs=True)
b = B(debug_msgs=False)
