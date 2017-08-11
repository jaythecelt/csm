'''
Thread for periodically requesting real time data from the 
Data Injection Point

'''

import json
import sched, time
import bleHandler
from _thread import *

import dipClient
import simpleSimClient

from HtpLogger import HtpLogger

log = HtpLogger.get()

simType = None
externalData = False
dataServerIp = None

RTDATA_UPDATE_PERIOD = 3  # In seconds
RTDATA_PRIORITY = 1

scheduleRunning = False
curEvent = None

'''
    Starts the real time data update to the Data Injection Point.
'''
def startRTData(_externalData, _simType, _dataServerIp):
    global curEvent
    global rtSched
    global simType
    global externalData
    global dataServerIp

    externalData = _externalData
    simType = _simType
    dataServerIp = _dataServerIp
    
    if externalData:
        log.info("=== Using real time data. ===")
    else:
        simType = simpleSimClient.SIMPLE
        log.info("=== Using simulated data. ===")

    rtSched = sched.scheduler(time.time, time.sleep)
    curEvent = rtSched.enter(RTDATA_UPDATE_PERIOD,  RTDATA_PRIORITY, rtDataHandler)
    start_new_thread(rtThread, ())
    return

def stopRTData():
    if (scheduleRunning and curEvent):
        rtSched.cancel(curEvent)
    return
    
'''
    Thread to run the schedule to send real time updates.
'''
def  rtThread():
    #TODO: Add error handling
    global rtSched
    global scheduleRunning

    scheduleRunning = True
    #Blocks while the schedule is running
    rtSched.run()
    scheduleRunning = False
    log.warning("rtThread stopped")
    return


'''
    Periodically queries the Data Injector client for new data.
    Parses the received data and updates the BLE GATT profile 
'''
def rtDataHandler(a = 'default'):
    #TODO: Add error handling
    global curEvent
    global rtSched
    global simType
    #TODO Need more accurate way to schedule next event.... this way adds about 
    #     10ms per invocation.
    
    # Schedule new event, if still running
    if (scheduleRunning): # Check prevents race condition
        curEvent = rtSched.enter(RTDATA_UPDATE_PERIOD,  RTDATA_PRIORITY, rtDataHandler)
  
    if simType == simpleSimClient.SIMPLE:
        ssc = simpleSimClient.SimpleSimClient()
        jsonStr = ssc.getRTData()
        log.info(jsonStr)
    else:
        jsonStr = dipClient.getRTData(dataServerIp)
    
    bleHandler.updateRTData(jsonStr)

    return


