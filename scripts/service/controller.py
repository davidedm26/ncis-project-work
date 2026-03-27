from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types, ipv4, udp, ipv6, tcp, arp

ARP_ETH_TYPE = 0x0806
IPV4_ETH_TYPE = 0x0800
IP_PROTO_UDP = 17
UDP_PORT_STREAMING = 9999

class RyuController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuController, self).__init__(*args, **kwargs)

        self.h1 = '00:00:00:00:00:01'
        self.h2 = '00:00:00:00:00:02'
        self.h3 = '00:00:00:00:00:03'
        self.h4 = '00:00:00:00:00:04'

        self.mac_to_port = {}

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, flag=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority,
            match=match, instructions=inst,
            idle_timeout = idle_timeout, flags=flag
        )
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        self.logger.info(f"[FEATURES HANDLER] dpid={dpid}")

        if dpid == 1:
            port_up, port_dw = 3, 4
            port_h1, port_h2 = 1, 2

            for host_port in [port_h1, port_h2]:
                match = parser.OFPMatch(
                    in_port=host_port,
                    eth_type=0x0800,
                    ip_proto=17,
                    udp_dst=UDP_PORT_STREAMING
                )
                actions = [parser.OFPActionOutput(port_up)]
                self.add_flow(datapath, priority=100, match=match, actions=actions)

        elif dpid == 2:
            port_up, port_dw = 1, 2
            port_h3, port_h4 = 3, 4

            for host_port in [port_h3, port_h4]:
                match = parser.OFPMatch(
                    in_port=host_port,
                    eth_type=0x0800,
                    ip_proto=17,
                    udp_dst=UDP_PORT_STREAMING
                )
                actions = [parser.OFPActionOutput(port_up)]
                self.add_flow(datapath, priority=100, match=match, actions=actions)

        elif dpid == 3:
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ip_proto=17, udp_dst=UDP_PORT_STREAMING
            )
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, priority=100, match=match, actions=actions)

            match = parser.OFPMatch(
                in_port=2, eth_type=0x0800, ip_proto=17, udp_dst=UDP_PORT_STREAMING
            )
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, priority=100, match=match, actions=actions)

        elif dpid == 4:
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, priority=1, match=match, actions=actions)

            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, priority=1, match=match, actions=actions)

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, priority=0, match=match, actions=actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth is None:
            return

        dst = eth.dst
        src = eth.src

        self.mac_to_port.setdefault(dpid, {})

        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
            self.logger.info(f"[LEARNING] dpid={dpid}, {src} -> {dst}, out_port={out_port}")
            actions = [parser.OFPActionOutput(out_port)]
        else:
            host_ports = {
                1: {1,2},
                2: {3,4},
                3: set(),
                4: set()
            }

            interswitch_links = {
                1: {4},
                2: {2},
            }

            actions = []
            for p in host_ports.get(dpid, set()):
                if p != in_port:
                    actions.append(parser.OFPActionOutput(p))

            for p in interswitch_links.get(dpid, set()):
                if p != in_port:
                    actions.append(parser.OFPActionOutput(p))

            self.logger.info(f"[CONTROLLED FLOOD via dw] dpid={dpid}, {src} -> {dst}, out_ports={[a.port for a in actions]}")

        if len(actions) == 1:
            match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
            self.add_flow(datapath, priority=1, match=match, actions=actions)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )
        datapath.send_msg(out)