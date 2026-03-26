from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types, ipv4, udp


# Estensione della classe base
class RyuController(app_manager.RyuApp):
    # OpenFlow 1.3 (Rifiuta linguaggi precedenti)
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuController, self).__init__(*args, **kwargs)
        
        self.h1 = '00:00:00:00:00:01'
        self.h2 = '00:00:00:00:00:02'
        self.h3 = '00:00:00:00:00:03'
        self.h4 = '00:00:00:00:00:04'

    # Installa una flow rule OpenFlow nello switch
    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, flag=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority,
            match=match, instructions=inst,
            idle_timeout = idle_timeout, flags=flag
        )

        # invio della regola allo switch
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        self.logger.info(f"[FEATURES HANDLER] Configuration dpid={dpid}\n")

        if dpid == 1:
            # -----> [UP flow configuration] <----- #
            port_out_Up = 3
            port_in_Up = 1

            # Flow IN
            self.add_mac_flow(datapath, self.h1, self.h3, port_out_Up)
            self.add_arp_flow(datapath, self.h1, port_out_Up)

            # Flow Back
            self.add_mac_flow(datapath, self.h3, self.h1, port_in_Up)
            self.add_arp_flow(datapath, self.h3, port_in_Up)

            # -----> [Down flow configuration] <----- #
            port_out_Dw = 4
            port_in_Dw = 2
            
            # Flow IN
            self.add_mac_flow(datapath, self.h2, self.h4, port_out_Dw)
            self.add_arp_flow(datapath, self.h2, port_out_Dw)

            # Flow Back
            self.add_mac_flow(datapath, self.h4, self.h2, port_in_Dw)
            self.add_arp_flow(datapath, self.h4, port_in_Dw)

        elif dpid == 2:
            port_out_Up = 1
            port_in_Up = 3

            self.add_mac_flow(datapath, self.h3, self.h1, port_out_Up)
            self.add_arp_flow(datapath, self.h3, port_out_Up)

            self.add_mac_flow(datapath, self.h1, self.h3, port_in_Up)
            self.add_arp_flow(datapath, self.h1, port_in_Up)

            port_out_Dw = 2
            port_in_Dw = 4
            
            self.add_mac_flow(datapath, self.h4, self.h2, port_out_Dw)
            self.add_arp_flow(datapath, self.h4, port_out_Dw)

            self.add_mac_flow(datapath, self.h2, self.h4, port_in_Dw)
            self.add_arp_flow(datapath, self.h2, port_in_Dw)

        elif dpid == 3:
            port_1 = 1
            port_2 = 2

            self.add_mac_flow(datapath, self.h1, self.h3, port_2)
            self.add_arp_flow(datapath, self.h1, port_2)

            self.add_mac_flow(datapath, self.h3, self.h1, port_1)
            self.add_arp_flow(datapath, self.h3, port_1)
        
        elif dpid == 4:
            port_1 = 1
            port_2 = 2

            self.add_mac_flow(datapath, self.h2, self.h4, port_2)
            self.add_arp_flow(datapath, self.h2, port_2)

            self.add_mac_flow(datapath, self.h4, self.h2, port_1)
            self.add_arp_flow(datapath, self.h4, port_1)    
        

    def add_mac_flow(self, datapath, src, dst, out_port, priority=10):
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(eth_src=src, eth_dst=dst)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(datapath, priority, match, actions)
    
    
    def add_arp_flow(self, datapath, eth_src, out_port):
        parser = datapath.ofproto_parser
        
        match = parser.OFPMatch(eth_src=eth_src, eth_dst="ff:ff:ff:ff:ff:ff", eth_type=0x0806)
        actions = []
        if not isinstance(out_port, list):
            out_port = [out_port]

        for port in out_port:
            actions.append(parser.OFPActionOutput(port))
        self.add_flow(datapath, priority=20, match=match, actions=actions)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ip = pkt.get_protocol(ipv4.ipv4)
        udp_pkt = pkt.get_protocol(udp.udp)
        
        self.logger.info("[NEW FLOW UNRECOGNIZED] From Here we continue")

        return