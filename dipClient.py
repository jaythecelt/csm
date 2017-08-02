'''
Data Injection Point Client Module

'''
import socket
import rtDataThread


HOST = '192.168.1.110'
#HOST = '10.0.2.2'
PORT = 5560
HDR_LEN = 5   # Message header length
RT_CMD = "RT"


def initSocket():
    global skt
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect((HOST, PORT))
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


def getRTData():
    if rtDataThread.SIMPLE_SIM:
        return
    initSocket()
    sendMessage(RT_CMD)
    jsonPayload = receiveMessage()
    print("Rvcd: ", jsonPayload)
    return jsonPayload
    

########################################################################


    