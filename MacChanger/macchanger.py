#!/usr/bin/env python3

'''
    Author: Andronikos Giachanatzis
    Date of latest update: 10-3-2020
'''
import subprocess
import argparse
import re

'''
    Inputs: -
    Function: Creates a parser instance
              Adds arguments input possibility in the command line
              Parses the given arguments from the user
    Output:   a Namespace object that contains the arguments given from the user
'''
def getArguments():
    # Create the help menu and the available arguments
    parser = argparse.ArgumentParser()

    # Add help entries
    parser.add_argument("-i", "--interface", dest="interface", help="Interface to change its MAC address")
    parser.add_argument("-m", "--mac", dest="newMac", help="The new MAC address to be assigned")

    # parse arguments given
    arguments = parser.parse_args()

    if (not arguments.interface):
        parser.error("[-] Missing interface argument: You must specify an interface")
    elif (not arguments.newMac):
        parser.error("[-] Missing new MAC argument: You must specify a new MAC address")
    return arguments

'''
    Input: An interface to change its MAC address
            the new MAC address
    Function: changes the MAC address of the given interface to a new MAC  
              address 
    Output: -
'''
def changeMac(interface, newMac):
    print("[+] Changing MAC address for " + interface + " to " + newMac)

    # Disable the iterface
    subprocess.run(["ifconfig", interface, "down"])

    # Change that MAC address
    subprocess.run(["ifconfig", interface, "hw", "ether", newMac])

    # Re-enable the interface
    subprocess.run(["ifconfig", interface, "up"])

'''
    Input: An interface for getting its MAC address
    Function: Runs an ifconfig command for the interface given and keeps only 
              its MAC address
    Output: A string containing the MAC address of the interface only if the 
            interface has a MAC address. If the interface doesn't have a
            MAC address (such as lo) nothing is returned (object NoneType)
'''
def getCurrentMac(interface):
    #run the command and save the output
    ifconfigResult = str(subprocess.check_output(["ifconfig", interface]))

    #extract the part of the output that contains the current MAC address
    macResult = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", ifconfigResult)
    if (macResult):
        return(macResult.group(0))
    else:
        print("[-] Could not read MAC address")

'''
    Input: An interface and the MAC address to be checked 
    Function: 
    Output: -
'''
def verifyChanges(interface, newMac):
    currentMac = getCurrentMac(interface)
    if (currentMac == newMac):
        print("[+] MAC address has successfully changed to   " + newMac)
    else:
        print("[-] MAC address did not change")


#get the arguments from the command line
arguments = getArguments()

# initialize arguments
interface = arguments.interface
newMac = arguments.newMac

currentMac = getCurrentMac(interface)
print("Current MAC: " + str(currentMac))

#change the MAC of the interface
changeMac(interface, newMac)

#print result of change
verifyChanges(interface, newMac)