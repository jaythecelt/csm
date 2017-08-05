'''
    Timer for tracking elapsed time of a formula
    Class implemented as a Singleton.
    
    Methods provided:
    start: Start the formula elapsed timer

    getElapsedTime:  Returns the number of ms since the start of the timer
                     as a float

    getElapsedTimeByte: Returns the nummber of ms since the start of the timer
                     as an integer represented as a four byte array, big endian order.
    
    Example use:
        ft = FormulaTimer()
        ft.start()
        time.sleep(2)
        print(ft.getElapsedTime())
        time.sleep(2)
        print(ft.getElapsedTimeBytes())

'''
import time
import logging
from logging import _startTime


# TODO Catch exceptions around number formatting and timer overruns
# TODO Possible generate exception when reading time without starting timer


class FormulaTimer(object):
    instance = None

    def __init__(self):
        if not FormulaTimer.instance:
            FormulaTimer.instance = FormulaTimer.__FormulaTimer()
            
   # Proxy for inner class
    def __getattr__(self, name):
        return getattr(self.instance, name)

    # Inner class for the singlton implementation.
    # Method implementations go here.
    class __FormulaTimer:
        startTime = None
       
        def __init__(self):        
            self.startTime = None
        
        def start(self):
            self.startTime = time.time() * 1000.0
            
        def reset(self):
            print("Reset the elapsed time.")
            self.startTime = time.time() * 1000.0
            
        def stop(self):
            print("Stoppedthe elapsed time.")
            self.startTime = None
            
        def getElapsedTime(self):
            now = time.time()
            if self.startTime==None:
                #logging.warning("FormulaTimer timer not started.")
                return None
            now = now * 1000.0  # Convert to ms
            return now - self.startTime
        
        # Returns four byte array in Big Endian order representing the 
        # elapsed time in ms
        def getElapsedTimeBytes(self):
            t = self.getElapsedTime()
            if t==None:
                t = 0.0
            t = round(t)
            fourBytes = int(t).to_bytes(4, byteorder='big')
            return fourBytes


