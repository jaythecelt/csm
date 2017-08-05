'''
Main python module for the 
Controller / Sequencer Module

'''
import json
import time
import sys, getopt
from gattServer import main as gattServerMainLoop
from rtDataThread import startRTData, stopRTData
from simpleSimClient import SIMPLE



def printHelp():
    print ('For help:               csm.py -h')
    print ('For external data:      csm.py -d <data server ip>')
    print ('For internal sim data:  csm.py -s <simulator type>')
    print ('   <simulator type> = ', SIMPLE, ' (default)')


    
def main(argv):
    
    externalData = False
    simType = None
    dataServerIp = None
    
    
    try:
        opts, args = getopt.getopt(argv,"hd:s:",[])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()

        elif opt == '-s':
            simType = arg
            externalData = False
            if simType == None:
                simType = SIMPLE
            if simType == SIMPLE:
                print("See simConfgData.py for simple sim configuration.")

        elif opt == '-d':
            dataServerIp = arg
            externalData = True

        
    startRTData(externalData, simType, dataServerIp)

    print("Entering gattServerMainLoop")
    gattServerMainLoop()


    print("Entering Loop")
    while True:
        pass

if __name__ == '__main__':
    main(sys.argv[1:])