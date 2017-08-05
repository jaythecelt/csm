'''
Simple Simulator Client

This is a very simple Data Injection Point simulator that bypasses the 
DIP socke and instead is called form csm.py.

The class is designed as a Singleton
'''

import logging
import queue
import json
import random

import simConfigData


global SIMPLE
SIMPLE = "simple"


class SimpleSimClient:
    instance = None
    
    def __init__(self):
        if not SimpleSimClient.instance:
            SimpleSimClient.instance = SimpleSimClient.__SimpleSimClient()

    # Proxy for inner class
    def __getattr__(self, name):
        return getattr(self.instance, name)


    # Inner class for the singlton implementation.
    # Method implementations go here.
    class __SimpleSimClient:
        
        def __init__(self):
            return
   
        def __str__(self):
            return repr(self)
        

        # Emulates getRTData() in dipClient
        def getRTData(self):
            rtDataDict = self.readAll()
            jsonPayload = json.dumps(rtDataDict)
            return jsonPayload

            
        def readAll(self):
            # Dictionaries to hold data
            rtData = {} # all data elements
            tcData = {} # thermocouple data
            hmData = {} # humidity data
            aiData = {} # analog input data
            diData = {} # digital input data

            # Thermocouples
            for k, v in simConfigData.tcConfig.items():
                j = self.readTCChannel(v)
                if j is not None:
                    tcData[k] = j

            # Humidity Sensors
            for k, v in simConfigData.hmConfig.items():
                j = self.readHMChannel(v)
                if j is not None:
                    hmData[k] = j
                    
            # Analog Inputs
            for k, v in simConfigData.analogInConfig.items():
                j = self.readAIChannel(v)
                if j is not None:
                    aiData[k] = j

            # Digital Inputs
            for k, v in simConfigData.digInConfig.items():
                j = self.readDIChannel(v)
                if j is not None:
                    diData[k] = j

            if len(tcData) > 0: 
                rtData['TC'] = tcData
            if len(hmData) > 0: 
                rtData['HM'] = hmData
            if len(aiData) > 0: 
                rtData['AI'] = aiData
            if len(diData) > 0: 
                rtData['DI'] = diData
           
            return rtData

    
 
        def readTCChannel(self, v):
            val = v[0]
            rndm = v[1]
            units = v[2]
            mute = v[3]
            if mute:
                return None
            if rndm:
                val = val + (random.random() * 10.0)
            rtn = val, units
            return rtn                

        def readHMChannel(self, v):
            val = v[0]
            rndm = v[1]
            mute = v[2]
            if mute:
                return None
            if rndm:
                val = val + int(random.random() * 10000)
            rtn = val
            return rtn                
            
            
            
        def readAIChannel(self, v):
            val = v[0]
            rndm = v[1]
            units = v[2]
            mute = v[3]
            if mute:
                return None
            if rndm:
                val = val + random.random()
            rtn = val, units
            return rtn                


        def readDIChannel(self, v):
            val = v[0]
            rndm = v[1]
            mute = v[2]
            if mute:
                return None
            if rndm:
                val = 0
                if random.random()>0.5:
                    val = 1
            rtn = val
            return rtn                




