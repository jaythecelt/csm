'''
    - Manage the BLE connection
    - Send real time data updates
    - Receive commands from the Android device
    
'''
import json



def updateRTData (rtDataJson):
    rtDict = json.loads(rtDataJson)
    tcDict = rtDict['TC']
    aiDict = rtDict['AI']
    diDict = rtDict['DI']
    
    
    
    
    
    print(tcDict['TC0'], tcDict['TC1'], tcDict['TC2'])
    
    
    
    
    return


