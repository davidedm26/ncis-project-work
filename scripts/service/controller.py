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


# Droppa il traffico IPv6 allo switch per evitare che i pacchetti IPv6 multicast generino un continuo flusso di eventi PacketIn al controller
DROP_IPV6_AT_SWITCH = True

class RyuController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuController, self).__init__(*args, **kwargs)

        self.h1 = '00:00:00:00:00:01'
        self.h2 = '00:00:00:00:00:02'
        self.h3 = '00:00:00:00:00:03'
        self.h4 = '00:00:00:00:00:04'

        self.mac_to_port = {} # dizionario per memorizzare le associazioni tra indirizzi MAC e porte degli switch, utilizzato per implementare la funzionalità di apprendimento degli indirizzi MAC (MAC learning) negli switch gestiti dal controller Ryu

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

        if dpid == 1: # Switch 1
            port_up, port_dw = 3, 4 # porta verso switch 3, porta verso switch 4
            port_h1, port_h2 = 1, 2 # porte verso host h1 e h2

            for host_port in [port_h1, port_h2]: # ciclo per creare le regole di forwarding per i pacchetti in ingresso dalle porte collegate agli host h1 e h2, specificando che i pacchetti con destinazione UDP sulla porta 9999 devono essere inoltrati verso la porta collegata allo switch 3
                match = parser.OFPMatch(
                    in_port=host_port, # Porta ingresso
                    eth_type=0x0800, # IPV4
                    ip_proto=17, # UDP
                    udp_dst=UDP_PORT_STREAMING # Porta destinazione UDP
                )
                actions = [parser.OFPActionOutput(port_up)] # Azione di output verso la porta collegata allo switch 3
                self.add_flow(datapath, priority=100, match=match, actions=actions) # Aggiunta della regola di forwarding al switch 1 con priorità 100

        elif dpid == 2: # Switch 2
            port_up, port_dw = 1, 2 # porta verso switch 3, porta verso switch 4
            port_h3, port_h4 = 3, 4 # porte verso host h3 e h4

            for host_port in [port_h3, port_h4]:
                match = parser.OFPMatch(
                    in_port=host_port, # Porta ingresso
                    eth_type=0x0800, # IPV4
                    ip_proto=17, # UDP
                    udp_dst=UDP_PORT_STREAMING # Porta destinazione UDP
                )
                actions = [parser.OFPActionOutput(port_up)] # Azione di output verso la porta collegata allo switch 3
                self.add_flow(datapath, priority=100, match=match, actions=actions) # Aggiunta della regola di forwarding al switch 2 con priorità 100  

        elif dpid == 3: # Switch 3

            # Traffico in ingresso da switch 1 verso switch 2
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ip_proto=17, udp_dst=UDP_PORT_STREAMING
            )
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, priority=100, match=match, actions=actions)

            # Traffico in ingresso da switch 2 verso switch 1
            match = parser.OFPMatch(
                in_port=2, eth_type=0x0800, ip_proto=17, udp_dst=UDP_PORT_STREAMING
            )
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, priority=100, match=match, actions=actions)

        elif dpid == 4: # Switch 4

            # Traffico in ingresso da switch 1 verso switch 2
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, priority=1, match=match, actions=actions)

            # Traffico in ingresso da switch 2 verso switch 1
            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, priority=1, match=match, actions=actions)

        # Optional: drop IPv6 early to avoid continuous controller PacketIn due
        # to multicast control traffic (e.g., 33:33:..:fb, :16, :02).
        if DROP_IPV6_AT_SWITCH:
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IPV6)
            self.add_flow(datapath, priority=10, match=match, actions=[])

        # Regola di default per inoltrare tutti i pacchetti che non soddisfano le condizioni precedenti verso il controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, priority=0, match=match, actions=actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER) 
    def _packet_in_handler(self, ev): # Gestisce gli eventi di tipo PacketIn, che vengono generati quando uno switch riceve un pacchetto che non corrisponde a nessuna regola di forwarding esistente e quindi lo inoltra al controller per ulteriori istruzioni su come gestirlo
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        in_port = msg.match['in_port']

        # Se il pacchetto non è di tipo Ethernet, ignoralo
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth is None:
            return

        dst = eth.dst # Indirizzo MAC di destinazione del pacchetto
        src = eth.src # Indirizzo MAC di origine del pacchetto

        self.mac_to_port.setdefault(dpid, {}) # Controlla se esiste già una voce per lo switch identificato da dpid nella tabella di apprendimento degli indirizzi MAC (mac_to_port) e, se non esiste, ne crea una nuova con un dizionario vuoto come valore

        self.mac_to_port[dpid][src] = in_port # Aggiorna la tabella di apprendimento degli indirizzi MAC associando l'indirizzo MAC di origine del pacchetto alla porta dello switch

        if dst in self.mac_to_port[dpid]: # Controlla se l'indirizzo MAC di destinazione del pacchetto è già presente nella tabella di apprendimento degli indirizzi MAC per lo switch identificato da dpid. 
            # Se è presente, inoltra il pacchetto verso la porta associata all'indirizzo MAC di destinazione
            out_port = self.mac_to_port[dpid][dst]
            self.logger.info(f"[LEARNING] dpid={dpid}, {src} -> {dst}, out_port={out_port}")
            actions = [parser.OFPActionOutput(out_port)]
        else: # altrimenti flooding controllato: inoltra il pacchetto verso tutte le porte tranne quella di ingresso, ma solo verso le porte collegate a host o verso le porte che collegano gli switch tra loro (interswitch links). Inoltre evita loop rimuovendo l'anello nella topologia
            host_ports = {
                1: {1,2}, # switch 1 ha host h1 e h2 collegati alle porte 1 e 2
                2: {3,4}, # switch 2 ha host h3 e h4 collegati alle porte 3 e 4
                3: set(), # switch 3 non ha host collegati direttamente
                4: set() # switch 4 non ha host collegati direttamente
            }

            # Forza rotta down come da traccia, riservando la rotta up solo per il traffico UDP 
            interswitch_links = {
                1: {4}, # switch 1 è collegato a switch 4 tramite la porta 4
                2: {2}, # switch 2 è collegato a switch 4 tramite la porta 2
            }

            actions = []
            for p in host_ports.get(dpid, set()):
                if p != in_port:
                    actions.append(parser.OFPActionOutput(p)) # Aggiunge un'azione di output verso la porta p è una porta collegata a un host, escludendo la porta di ingresso del pacchetto

            for p in interswitch_links.get(dpid, set()):
                if p != in_port:
                    actions.append(parser.OFPActionOutput(p)) # Aggiunge un'azione di output verso la porta p è una porta collegata a un altro switch, escludendo la porta di ingresso del pacchetto

            self.logger.info(f"[CONTROLLED FLOOD via dw] dpid={dpid}, {src} -> {dst}, out_ports={[a.port for a in actions]}")

        
        if not actions:
            return

        if len(actions) == 1: # salva regola di forwarding se c'è una sola porta di output, altrimenti non salva regole di flooding
            match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
            self.add_flow(datapath, priority=1, match=match, actions=actions)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )
        datapath.send_msg(out) # Re-Invia messaggio allo switch aggiornato. 