#!/usr/bin/env python3

'''
    before running a queue must be created in the system.
    iptables -I FORWARD -j NFQUEUE --queue-num 0
    and also port forwarding
'''
import netfilterqueue
import scapy.all as scapy

def processPacket(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    print(scapy_packet.show())
    # drop the packet
    packet.drop()

# not interracting still with the queue in the system
queue = netfilterqueue.NetfilterQueue()
# bind to the queue created in the system, process packet is called for every packet
queue.bind(0, processPacket)
queue.run()


