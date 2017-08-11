'''
Real Time Data Queue

The class is designed as a Singleton
'''
import queue
from HtpLogger import HtpLogger

QUEUE_MAX_SIZE = 10
QUEUE_PUT_TIMEOUT = 0.002
QUEUE_GET_TIMEOUT = 0.002

class RTDQueue:
    instance = None
    lg = None
    
    def __init__(self):
        if not RTDQueue.instance:
            RTDQueue.instance = RTDQueue.__RTDQueue()
        self.log = HtpLogger.get()

    # Proxy for inner class
    def __getattr__(self, name):
        return getattr(self.instance, name)


    # Inner class for the singlton implementation.
    # Method implementations go here.
    class __RTDQueue:
        rtdQ = None
        
        def __init__(self):
            self.rtdQ = queue.Queue(maxsize=QUEUE_MAX_SIZE)
            self.bEnable = False
   
        def __str__(self):
            return repr(self)
        
        def put(self, v):
            if not self.bEnable:
                return
            try:
                self.rtdQ.put(v, True, QUEUE_PUT_TIMEOUT)
            except (queue.Full):
                self.log.warning("RTD Queue is full, value dropped: " + str(v))
                return
                
        def get(self):
            if not self.bEnable:
                return None
            try:
                rtn = self.rtdQ.get(True, QUEUE_GET_TIMEOUT)
            except (queue.Empty):
                rtn = None
            return rtn

        def enable(self):
            self.bEnable = True
           
        def disable(self):
            self.bEnable = False
            
        def isEnable(self):
            return self.bEnable

