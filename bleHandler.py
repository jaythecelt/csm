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
    printStr = ""
    for v in bArray:
        value.append(dbus.Byte(v))
        printStr = printStr + " 0x{0:x}".format(v)
    
    # Calc the CRC and add to value array
    crc = crc16.calcCRC16(bArray)
    value.append(dbus.Byte(crc[0]))
    value.append(dbus.Byte(crc[1]))

    printStr = printStr + " 0x{0:x}".format(crc[0])
    printStr = printStr + " 0x{0:x}".format(crc[1])
    
    # Add the characteristic payload to the queue
    rtdQ = rtdQueue.RTDQueue()
    if rtdQ.isEnable(): 
        print("Queuing: ", valStr, "\nBytes:  ", printStr,"\n" )
#    else:
#        print("rtdQ not enabled!")
    rtdQ.put(value)
    return


def updateRTData (rtDataJson):
    rtDict = json.loads(rtDataJson)
    
    # Analog In
    if 'AI' in rtDict:
        aiDict = rtDict['AI']
        for k, v in aiDict.items():
            label = '{:<3.3}'.format(k)
            fval = float(v[0])
            floatStr = '{:06.2f}'.format(fval)
            units = '{:1.1}'.format(v[1])
            valStr = 'V' + label + floatStr + units
            queueUp(valStr)
        
    # Digital In
    if 'DI' in rtDict:
        diDict = rtDict['DI']
        for k, v in diDict.items():
            label = '{:<3.3}'.format(k)
            digVal = v
            digStr = '{:1d}'.format(digVal)
            valStr = 'D' + label + digStr
            queueUp(valStr)

    # Thermocouples
    if 'TC' in rtDict:
        tcDict = rtDict['TC']
        for k, v in tcDict.items():
            label = '{:<3.3}'.format(k)
            fval = float(v[0])
            floatStr = '{:07.2f}'.format(fval)
            units = '{:1.1}'.format(v[1])
            valStr = 'T' + label + floatStr + units
            queueUp(valStr)

    # Humidity Sensors
    if 'HM' in rtDict:
        hmDict = rtDict['HM']
        for k, v in hmDict.items():
            label = '{:<3.3}'.format(k)
            ivalStr = '{:06d}'.format(v)
            valStr = 'H' + label + ivalStr
            queueUp(valStr)
            
    # Counters
    if 'CT' in rtDict:
        ctDict = rtDict['CT']
        for k, v in ctDict.items():
            label = '{:<3.3}'.format(k)
            ivalStr = '{:08d}'.format(v)
            valStr = 'C' + label + ivalStr
            queueUp(valStr)
        
    return


