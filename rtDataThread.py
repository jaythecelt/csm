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

SIMPLE_SIM = True

RTDATA_UPDATE_PERIOD = 3  # In seconds
RTDATA_PRIORITY = 1

scheduleRunning = False
curEvent = None

'''
    Starts the real time data update to the Data Injection Point.
'''
def startRTData():
    global curEvent
    global rtSched

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
    print("rtThread stopped")
    return


'''
    Periodically queries the Data Injector client for new data.
    Parses the received data and updates the BLE GATT profile 
'''
def rtDataHandler(a = 'default'):
    #TODO: Add error handling
    global curEvent
    global rtSched
    #TODO Need more accurate way to schedule next event.... this way adds about 
    #     10ms per invocation.
    
    # Schedule new event, if still running
    if (scheduleRunning): # Check prevents race condition
        curEvent = rtSched.enter(RTDATA_UPDATE_PERIOD,  RTDATA_PRIORITY, rtDataHandler)
   
   
    if SIMPLE_SIM :
        ssc = simpleSimClient.SimpleSimClient()
        jsonStr = ssc.getRTData()
    else:
        jsonStr = dipClient.getRTData()
    
    bleHandler.updateRTData(jsonStr)

    return


