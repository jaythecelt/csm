'''
Data Injection Point Client Module

'''
import socket
import rtDataThread
from HtpLogger import HtpLogger

DEF_HOST = '192.168.1.110'
PORT = 5560
HDR_LEN = 5   # Message header length
RT_CMD = "RT"

log = HtpLogger.get()


def initSocket(_host):
    global skt
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect((_host, PORT))
    return
    

def sendMessage(message):
    # Prepend the message with the payload length
    l = len(message)
    message = "{:0>5d}".format(l) + message
    skt.send(str.encode(message))
    return

def receiveMessage():
    x = skt.recv(HDR_LEN)
    payloadLen = int(x)
    payload = ""
    while (payloadLen>0):
        payloadBytes = skt.recv(1024)
        payloadLen -= len(payloadBytes)
        payload = payload + payloadBytes.decode('utf-8')
        skt.close()
    return payload


def getRTData(_host):
    if _host == None:
        _host = DEF_HOST
    initSocket(_host)
    sendMessage(RT_CMD)
    jsonPayload = receiveMessage()
    log.debug("Rvcd: ", jsonPayload)
    return jsonPayload
    

########################################################################


    