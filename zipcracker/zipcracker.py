'''
Author: Andronikos Giachanatzis
'''

import zipfile
import argparse
from threading import Thread


def extract(zfile, passwd):
    '''

    :param zfile: The password protected file
    :param passwd: The password to check
    :return: None
    '''
    try:
        zfile.extractall(pwd=passwd.encode('utf-8'))
        print("[+] Password = " + passwd + '\n')
        exit(0)
    except Exception as e:
        pass


def main():
    # add cmd arguments
    parser = argparse.ArgumentParser(description="Usage: %prog " + "-f <zipfile> -d <dictionaryfile>")
    parser.add_argument("-f", dest="zip", help="the password protected file")
    parser.add_argument("-d", dest="dict", help="the dictionary file")
    options = parser.parse_args()

    # if arguments are missing print the correct usage format and exit
    if (options.zip == None ) | (options.dict == None):
        print (parser.usage)
        exit(0)
    else:
        zname = options.zip
        dname = options.dict

    # try to guess the password of the zip with the words from the dictionary file
    # speed up the process by using threading
    zfile = zipfile.ZipFile(zname)
    dictfile = open(dname)
    for line in dictfile.readlines():
        passwd = line.strip('\n')
        t = Thread(target=extract, args=(zfile,passwd))
        t.start()

if __name__ == '__main__':
    main()

