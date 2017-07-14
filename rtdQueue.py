'''
Real Time Data Queue

The class is designed as a Singleton
'''
import logging
import queue

QUEUE_MAX_SIZE = 10
QUEUE_PUT_TIMEOUT = 0.002
QUEUE_GET_TIMEOUT = 0.002

class RTDQueue:
    instance = None
    
    def __init__(self):
        if not RTDQueue.instance:
            RTDQueue.instance = RTDQueue.__RTDQueue()

    # Proxy for inner class
    def __getattr__(self, name):
        return getattr(self.instance, name)


    # Inner class for the singlton implementation.
    # Method implementations go here.
    class __RTDQueue:
        rtdQ = None

        def __init__(self):
            self.rtdQ = queue.Queue(maxsize=QUEUE_MAX_SIZE)
    
        def __str__(self):
            return repr(self)
        
        def put(self, v):
            try:
                self.rtdQ.put(v, True, QUEUE_PUT_TIMEOUT)
            except (queue.Full):
                logging.warning("RTD Queue is full, value dropped: " + str(v))
                return
                
        def get(self):
            try:
                rtn = self.rtdQ.get(True, QUEUE_GET_TIMEOUT)
            except (queue.Empty):
                logging.warning("RTD Queue is empty, nothing to get.")
                rtn = None
            return rtn
