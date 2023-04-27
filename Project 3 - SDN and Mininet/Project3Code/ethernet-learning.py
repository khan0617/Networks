from pox.core import core
import pox.openflow.libopenflow_01 as of


# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()


# !!!!! PROJ3 Define your data structures here
mac_to_port = {}


# Handle messages the switch has sent us because it has no
# matching rule.
def _handle_PacketIn(event):
    global mac_to_port

    # get the port the packet came in on for the switch contacting the controller
    packetInPort = event.port

    # use POX to parse the packet data
    packet = event.parsed

    # get src and dst mac addresses
    src_mac = str(packet.src)
    dst_mac = str(packet.dst)

    # get switch ID
    switchID = str(event.connection.dpid) + str(event.connection.ID)
    log.info('Packet has arrived: SRCMAC:{} DSTMAC:{} from switch:{} in-port:{}'.format(src_mac, dst_mac, switchID, packetInPort))

    if switchID not in mac_to_port:
        mac_to_port[switchID] = {}
    mac_to_port[switchID][src_mac] = packetInPort

    # destination MAC is known, send the packet to the appropriate port
    if dst_mac in mac_to_port[switchID]:
        out_port = mac_to_port[switchID][dst_mac]
        msg = of.ofp_packet_out()
        msg.data = event.data
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = packetInPort
        event.connection.send(msg)
        log.info("Forwarding packet from {} to {} on switch {} out-port {}".format(src_mac, dst_mac, switchID, out_port))

    # destination MAC is unknown, flood the packet on all ports except the input port
    # following example from pox self learning controller github page
    else:
        msg = of.ofp_packet_out()
        msg.data = event.data
        action = of.ofp_action_output(port=of.OFPP_FLOOD)
        msg.actions.append(action)
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = packetInPort
        event.connection.send(msg)
        log.info("Flooding packet from {} to {} on switch {}".format(src_mac, dst_mac, switchID))


def launch ():
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  log.info("Pair-Learning switch running.")
