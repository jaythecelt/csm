'''
    - Manage the BLE connection
    - Send real time data updates
    - Receive commands from the Android device

{"TC": {"TC0": [78.9337934710637, "F"]}, "AI": {"AI0": [5.102922332635204, "V"]}, "DI": {"DI0": 1}}

    
'''
import logging
import json
import dbus
import rtdQueue
import crc16
import formulaTimer

def queueUp(valStr):
    value = []
    bArray = bytearray(valStr.encode())

    # Add the elapsed time for the time stamp
    ft = formulaTimer.FormulaTimer()
    ftBytes = ft.getElapsedTimeBytes()
    bArray.append(ftBytes[0])
    bArray.append(ftBytes[1])
    bArray.append(ftBytes[2])
    bArray.append(ftBytes[3])

    # Populate value with valueStr and time 
    for v in bArray:
        value.append(dbus.Byte(v))
        print("0x{0:x}".format(v))
    
    # Calc the CRC and add to value array
    crc = crc16.calcCRC16(bArray)
    value.append(dbus.Byte(crc[0]))
    value.append(dbus.Byte(crc[1]))

    # Add the characteristic payload to the queue
    rtdQ = rtdQueue.RTDQueue()
    if rtdQ.isEnable(): 
        print("Queuing ", valStr)
    rtdQ.put(value)
    return


def updateRTData (rtDataJson):
    rtDict = json.loads(rtDataJson)
    tcDict = rtDict['TC']
    aiDict = rtDict['AI']
    diDict = rtDict['DI']
    
    # Analog In
    for k, v in aiDict.items():
        label = '{:#<4.4}'.format(k)
        fval = float(v[0])
        floatStr = '{:.2f}'.format(fval)
        units = '{:1.1}'.format(v[1])
        valStr = label + floatStr + units
        queueUp(valStr)
        
    # Digital In
    for k, v in diDict.items():
        label = '{:#<4.4}'.format(k)
        digVal = v
        digStr = '{:1d}'.format(digVal)
        valStr = label + digStr
        queueUp(valStr)

    # Thermocouples
    for k, v in tcDict.items():
        label = '{:#<4.4}'.format(k)
        fval = float(v[0])
        floatStr = '{:.2f}'.format(fval)
        units = '{:1.1}'.format(v[1])
        valStr = label + floatStr + units
        queueUp(valStr)


        
    return


