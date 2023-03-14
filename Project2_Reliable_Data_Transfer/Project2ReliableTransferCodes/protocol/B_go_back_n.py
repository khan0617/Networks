from pj2.simulator import to_layer_five
from pj2.packet import send_ack


class B:
    def __init__(self):
        # go back n, the initialization of B
        # The state only need to maintain the information of expected sequence number of packet
        return

    def B_output(self, m):
        return

    def B_input(self, pkt):
        # go back n, B_input
        # You need to verify the checksum to make sure that packet isn't corrupted
        # If the packet is the right one, you need to pass to the fifth layer using "to_layer_five(entity,payload)"
        # Send acknowledgement using "send_ack(entity, seq)" based on the correctness of received packet
        # If the packet is the correct one, in the last step, you need to update its state ( update the expected sequence number)

        return

    def B_handle_timer(self):
        return


b = B()
