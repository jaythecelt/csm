'''
Main python module for the 
Controller / Sequencer Module

'''

from HtpLogger import HtpLogger
# Setup logger
logPrefix = "csm"
log = HtpLogger(logPrefix, HtpLogger.DEBUG, HtpLogger.DEBUG)

import json
import time
import sys, getopt
from gattServer import main as gattServerMainLoop
from rtDataThread import startRTData, stopRTData
from simpleSimClient import SIMPLE



def printHelp():
    log.info("Printing help message to console")
    print ('For help:               csm.py -h')
    print ('For external data:      csm.py -d <data server ip>')
    print ('For internal sim data:  csm.py -s <simulator type>')
    print ('   <simulator type> = ', SIMPLE, ' (default)')


    
def main(argv):
    
    externalData = False
    simType = None
    dataServerIp = None

    log.info("Arguments: %s", sys.argv[1:])
    try:
        opts, args = getopt.getopt(argv,"hd:s:",[])
    except getopt.GetoptError:
        printHelp()
        log.info("Exit!")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()

        elif opt == '-s':
            log.info("Found simulator option")
            simType = arg
            externalData = False
            if simType == None:
                log.debug("Default to simple sim.")
                simType = SIMPLE
            if simType == SIMPLE:
                log.info("See simConfgData.py for simple sim configuration.")

        elif opt == '-d':
            log.info("Found external data option")
            dataServerIp = arg
            log.info("Using external data source at %s", dataServerIp)
            externalData = True

        
    startRTData(externalData, simType, dataServerIp)

    log.info("Entering gattServerMainLoop")
    gattServerMainLoop()


    log.debug("Entering Loop")
    while True:
        pass

if __name__ == '__main__':
    main(sys.argv[1:])