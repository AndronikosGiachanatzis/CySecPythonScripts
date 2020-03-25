#!/usr/bin/env python3

'''
    Author: Andronikos Giachanatzis
    Date of latest update: 21-3-2020
'''


import scapy.all as scapy
import argparse
import re

'''
    Input: -
    Function: Creates a parser instance
              Adds arguments input possibility in the command line
              Parses the given arguments from the user
    Output:   A string that contains the target IP(s) as given directly from the user
'''
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", required=True, help="IP/MASK The target IP (range) to scan")
    arguments = parser.parse_args()
    arguments = getTarget(arguments.target)
    return arguments

'''
    Input: A string that contains the argument as given from the user
    Function: Checks if the user entered the IP target in the correct format.
              If the format isn't correct it exits the program
    Output: A string that contains the IP target (and probably the mask)
'''
def getTarget(target):

    #check if the input lists a subnet mask along with the ip
    mask = re.search(r"/\d{0,2}", target)
    if (mask): # if a mask exists keep both the IP and the mask
        ip = re.search(r"\d+\.\d+\.\d+\.\d+/\d{0,2}", target)
    else: # if it doesn't exist keep just the IP
        ip = re.search(r"\d+\.\d+\.\d+\.\d+", target)

    if (not ip): #if the input format is incorrect, exit
        exit("Error: Could not read the target IP. Check the format of the input")
    else:
        return ip.group(0)

'''
    Input: A string that contains the target IP (and possibly the mask for multiple targets)
    Function: It creates an ARP Request packet and an Broadcast Ethernet frame.
              It sends the packet(s) in the network, awaits for responses and receives responses from the target IP(s)
              It creates a list that contains the couples of IPs and MACs from the clients that replied
    Output: A list that contains the IPs and MACs of the clients that replied
'''
def scan(ip):
    # build the ARP Request packet
    arp_request = scapy.ARP(pdst=ip)
    # build the broadcast ethernet frame that encapsulates the ARP packet
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    # combine the ARP and the Ethernet objects into one object
    arp_request_broadcast = broadcast/arp_request

    # send and receive packets with custom ether parts. Wait 1 second for reply and move on
    answered_list = scapy.srp(arp_request_broadcast, timeout=1)[0]

    #create the list that contains only the IPs and MACs of the clients that answered the ARP Request
    clients_list = []
    for element in answered_list:
        answers_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(answers_dict)

    return clients_list

'''
    Input: A list that contains the couples of IPs and MACs
    Function: Prints to the user the couples of IPs and MACs
    Output: - 
'''
def printClients(clients_list):
    print("IP\t\t\tMAC Address")
    print("--------------------------------------------------------")
    for client in clients_list:
        print(client["ip"] + "\t\t" + client["mac"])
        print("--------------------------------------------------------")


#read the argumets
target = getArguments()

# send and receive the ARP requests
scan_result = scan(target)

#print the results
printClients(scan_result)