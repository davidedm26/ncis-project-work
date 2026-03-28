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
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION] # specifica la versione di OpenFlow supportata

    def __init__(self, *args, **kwargs): # inizializzazione della classe
        super(RyuController, self).__init__(*args, **kwargs) # chiamata al costruttore della classe base
        
        self.h1 = '00:00:00:00:00:01' # definizione degli indirizzi MAC degli host
        self.h2 = '00:00:00:00:00:02' # definizione degli indirizzi MAC degli host
        self.h3 = '00:00:00:00:00:03' # definizione degli indirizzi MAC degli host
        self.h4 = '00:00:00:00:00:04' # definizione degli indirizzi MAC degli host

    # Installa una flow rule OpenFlow nello switch
    # Una flow rule è composta da: match (corrispondenza dei pacchetti), actions (azioni da eseguire sui pacchetti), priority (priorità della regola), idle_timeout (tempo di inattività prima di rimuovere la regola) e flag (opzioni aggiuntive)
    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, flag=0):
        ofproto = datapath.ofproto # definizione del protocollo OpenFlow utilizzato dallo switch
        parser = datapath.ofproto_parser # definizione del parser OpenFlow

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)] # definizione delle istruzioni da eseguire sui pacchetti che corrispondono alla regola (in questo caso, applica le azioni specificate)

        mod = parser.OFPFlowMod( # creazione del messaggio di modifica della flow rule 
            datapath=datapath, priority=priority,
            match=match, instructions=inst,
            idle_timeout = idle_timeout, flags=flag
        )

        datapath.send_msg(mod) # invia il messaggio di modifica della flow rule allo switch

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER) # Questa funzione viene attivata una sola volta per ogni switch non appena stabilisce una connessione con il controller Ryu .
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath # ricava datapath (rappresenta la connessione tra il controller e lo switch)
        ofproto = datapath.ofproto # ricava protocollo OpenFlow utilizzato dallo switch
        parser = datapath.ofproto_parser # ricava definizione del parser OpenFlow
        dpid = datapath.id # ricava identificatore univoco dello switch (Datapath ID)

        self.logger.info(f"[FEATURES HANDLER] Configuration dpid={dpid}\n")

        # Il controller riconosce lo switch in base al suo DPID (Datapath ID) e configura le flow rules di conseguenza
        
        if dpid == 1: # switch 1 
            # -----> [UP flow configuration] <----- #
            port_out_Up = 3 # porta di uscita per il flusso in uscita verso l'alto (switch 3)
            port_in_Up = 1 # porta di ingresso per il flusso in ingresso proveniente dall'alto (switch 3)

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

        elif dpid == 2: # switch 2
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

        elif dpid == 3: # switch 3
            port_1 = 1
            port_2 = 2

            self.add_mac_flow(datapath, self.h1, self.h3, port_2)
            self.add_arp_flow(datapath, self.h1, port_2)

            self.add_mac_flow(datapath, self.h3, self.h1, port_1)
            self.add_arp_flow(datapath, self.h3, port_1)
        
        elif dpid == 4: # switch 4
            port_1 = 1
            port_2 = 2

            self.add_mac_flow(datapath, self.h2, self.h4, port_2)
            self.add_arp_flow(datapath, self.h2, port_2)

            self.add_mac_flow(datapath, self.h4, self.h2, port_1)
            self.add_arp_flow(datapath, self.h4, port_1)    
        

    def add_mac_flow(self, datapath, src, dst, out_port, priority=10): # aggiunge una flow rule basata sugli indirizzi MAC di origine e destinazione, specificando la porta di uscita e la priorità della regola
        parser = datapath.ofproto_parser # definizione del parser OpenFlow

        match = parser.OFPMatch(eth_src=src, eth_dst=dst) # definizione del match per la flow rule (corrispondenza dei pacchetti in base agli indirizzi MAC di origine e destinazione)
        actions = [parser.OFPActionOutput(out_port)] # definizione delle azioni da eseguire sui pacchetti che corrispondono alla regola (in questo caso, inoltra i pacchetti alla porta specificata)
        self.add_flow(datapath, priority, match, actions) # chiama la funzione add_flow per installare la flow rule nello switch
    
    
    def add_arp_flow(self, datapath, eth_src, out_port): # aggiunge una flow rule specifica per i pacchetti ARP, basata sull'indirizzo MAC di origine e sulla porta di uscita
        parser = datapath.ofproto_parser # definizione del parser OpenFlow
        
        match = parser.OFPMatch(eth_src=eth_src, eth_dst="ff:ff:ff:ff:ff:ff", eth_type=0x0806) # definizione del match per la flow rule (corrispondenza dei pacchetti in base all'indirizzo MAC di origine e al tipo di protocollo)

        actions = [] # definizione delle azioni da eseguire sui pacchetti che corrispondono alla regola
        if not isinstance(out_port, list): # se out_port non è una lista, lo converte in una lista
            out_port = [out_port]

        for port in out_port: # aggiunge un'azione di output per ogni porta specificata nella lista out_port
            actions.append(parser.OFPActionOutput(port)) # aggiunge un'azione di output per inoltrare i pacchetti alla porta specificata
        self.add_flow(datapath, priority=20, match=match, actions=actions) # chiama la funzione add_flow per installare la flow rule nello switch, con una priorità più alta rispetto alle regole basate sugli indirizzi MAC


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER) # Questa funzione viene attivata ogni volta che uno switch invia un messaggio Packet-In al controller Ryu, indicando che ha ricevuto un pacchetto che non corrisponde a nessuna flow rule installata.
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
        
        self.logger.info("[NEW FLOW UNRECOGNIZED] From Here we continue") # logga l'arrivo di un nuovo pacchetto che non corrisponde a nessuna flow rule installata, indicando che il controller Ryu deve decidere come gestire questo pacchetto (ad esempio, installando una nuova flow rule o inoltrandolo a una porta specifica)

        return