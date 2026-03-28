import random, time, threading 
from mininet import *
from mininet.log import *
from mininet.net import *
from mininet.node import *
from mininet.link import *


class Environment(object):
    def __init__(self):

        info("[NET-DEF] Initializing controller\n")

        self.net = Mininet(controller=RemoteController, link=TCLink) # crea un'istanza della classe Mininet, specificando che il controller sarà un RemoteController (controller esterno) e che i link tra i nodi saranno di tipo TCLink (link con controllo del traffico)
        
        c1 = self.net.addController( 'c1', controller=RemoteController, port=6653, ip='127.0.0.1')  # aggiunge un controller remoto alla rete, specificando il nome del controller (c1), il tipo di controller (RemoteController), la porta su cui il controller ascolterà le connessioni (6653) e l'indirizzo IP del controller (

        
        c1.start() # avvia il controller remoto, consentendo al controller di stabilire connessioni con gli switch della rete e di gestire il traffico in base alle flow rules installate negli switch

        info("[NET-DEF] Adding hosts and switches\n")

        # Definizione hosts
        self.h1 = self.net.addHost('h1', mac= '00:00:00:00:00:01', ip= '10.0.0.1')
        self.h2 = self.net.addHost('h2', mac= '00:00:00:00:00:02', ip= '10.0.0.2')
        self.h3 = self.net.addHost('h3', mac= '00:00:00:00:00:03', ip= '10.0.0.3')
        self.h4 = self.net.addHost('h4', mac= '00:00:00:00:00:04', ip= '10.0.0.4')

        # Definizione switch
        self.s1 = self.net.addSwitch('s1')
        self.s2 = self.net.addSwitch('s2')
        self.Up = self.net.addSwitch('s3')
        self.Dw = self.net.addSwitch('s4')
        
        
        info("[NET-DEF] Connecting hosts\n")  
        
        # Link declaration 
        # Hosts to Switches
        self.net.addLink(self.h1, self.s1, delay='0.01ms', port1=1, port2=1)
        self.net.addLink(self.h2, self.s1, delay='0.01ms', port1=1, port2=2)
        self.net.addLink(self.h3, self.s2, delay='0.01ms', port1=1, port2=3)
        self.net.addLink(self.h4, self.s2, delay='0.01ms', port1=1, port2=4)

        # Switches to Switches
        self.net.addLink(self.s1, self.Up, bw=10, delay='0.025ms', port1=3, port2=1)
        self.net.addLink(self.Up, self.s2, bw=10, delay='0.025ms', port1=2, port2=1)
        self.net.addLink(self.s1, self.Dw, bw=1, delay='0.025ms', port1=4, port2=1)
        self.net.addLink(self.Dw, self.s2, bw=1, delay='0.025ms', port1=2, port2=2)

        info("[NET-DEF] Starting network\n")
        self.net.build()
        self.net.start()
