import random, time, threading 
from mininet import *
from mininet.log import *
from mininet.net import *
from mininet.node import *
from mininet.link import *


class Environment(object):
    def __init__(self):
        "[NET-DEF] Creating Network..."

        # Controller management
        info("[NET-DEF] Starting controller\n")

        self.net = Mininet(controller=RemoteController, link=TCLink)
        c1 = self.net.addController( 'c1', controller=RemoteController, port=6653, ip='127.0.0.1') #Controller
        c1.start()

        info("[NET-DEF] Adding hosts and switches\n")

        # Host definition
        self.h1 = self.net.addHost('h1', mac= '00:00:00:00:00:01', ip= '10.0.0.1')
        self.h2 = self.net.addHost('h2', mac= '00:00:00:00:00:02', ip= '10.0.0.2')
        self.h3 = self.net.addHost('h3', mac= '00:00:00:00:00:03', ip= '10.0.0.3')
        self.h4 = self.net.addHost('h4', mac= '00:00:00:00:00:04', ip= '10.0.0.4')

        # Switch definition
        self.s1 = self.net.addSwitch('s1')
        self.s2 = self.net.addSwitch('s2')
        self.Up = self.net.addSwitch('s3')
        self.Dw = self.net.addSwitch('s4')


        info("[NET-DEF] Connecting hosts\n")

        # Connection of hosts
        self.net.addLink(self.h1, self.s1, bw=10, port1=1, port2=1)
        self.net.addLink(self.h2, self.s1, bw=10, port1=1, port2=2)
        self.net.addLink(self.h3, self.s2, bw=10, port1=1, port2=3)
        self.net.addLink(self.h4, self.s2, bw=10, port1=1, port2=4)

        # Connection of Upper Slice (Link with fiber cable with lenght of 5 km)
        self.net.addLink(self.s1, self.Up, bw=10, delay='3ms', port1=3, port2=1)
        self.net.addLink(self.Up, self.s2, bw=10, delay='3ms', port1=2, port2=1)

        # Connection of Lower Slice
        self.net.addLink(self.s1, self.Dw, bw=1, delay='3ms', port1=4, port2=1)
        self.net.addLink(self.Dw, self.s2, bw=1, delay='3ms', port1=2, port2=2)

        info("[NET-DEF] Starting network\n")
        self.net.build()
        self.net.start()
