#!/usr/bin/env python3

###### Imports ###########

import rtdQueue
import formulaTimer

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array

try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import sys

from random import randint


###### Vars and constants ###########
mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'


dataValChrc = None


###### Exceptions ###########


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'

class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'

class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'

class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'

    
    

####### GATT Interface Implementations  ###############

class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(RealTimeDataService(bus, 0))
        #self.add_service(HeartRateService(bus, 0))
        #self.add_service(BatteryService(bus, 1))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        print("Adding service: " + str(service))
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """
    PATH_BASE = '/com/hyperwave/csm/rtd/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_SERVICE_IFACE: {
                        'UUID': self.uuid,
                        'Primary': self.primary,
                        'Characteristics': dbus.Array(
                                self.get_characteristic_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print ('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()


        
##### Real Time Data Service and Characteristics ###################                
        
        
class RealTimeDataService(Service):
    """
    Service that provides characteristics and descriptors for 
    the test platform read time data "stream"
    """
    RTD_SVC_UUID = '79d9c22a-5c68-40d8-9d03-bc5cc58013e9'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.RTD_SVC_UUID, True)
        dataValChrc = DataValueCharacteristic(bus, 0, self)
        self.add_characteristic(dataValChrc)
        

class DataValueCharacteristic(Characteristic):
    """
    Data Value characteristic the holds a real time value from the test platform
    Contains "extended properties", as well as a descriptor.

    """
    DATA_VAL_CHRC_UUID = 'cd062ebb-e951-44eb-9f65-de08db0b6307'
    rtdQ = None

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.DATA_VAL_CHRC_UUID,
                ['read', 'notify'],
                service)
        self.rtdQ = rtdQueue.RTDQueue()
        self.value = []
        self.notifying = False
        print("init characteristic ... notifying = ", self.notifying)
#        self.add_descriptor(RTDCharacteristicDataDeclaration(bus, 0, self))
#        self.add_descriptor(
#                RTDClientCharacteristicConfigurationDescriptor(bus, 0, self))
    
    def rtd_val_cb(self):
        while True:
            v = self.rtdQ.get()
            if v is not None:
                self.value = v
                self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': self.value }, [])
            else:
                break;
        return self.notifying

    def rtd_poll_queue(self):
        if not self.notifying:
            return
        GObject.timeout_add(1000, self.rtd_val_cb)

    def ReadValue(self, options):
        print('DataValueCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('DataValueCharacteristic Write: ' + repr(value))
        self.value = value

    def StartNotify(self):
        print('Called StartNotify!')
        if self.notifying:
            print('Already notifying, nothing to do')
            return
        print('Enabling rtdQ')
        self.rtdQ.enable()
        self.notifying = True
        self.rtd_poll_queue()
        # Start the timer!
        ft = formulaTimer.FormulaTimer()
        ft.start()

    def StopNotify(self):
        print('Called StopNotify')
        if not self.notifying:
            print('Not notifying, nothing to do')
            return
        self.rtdQ.disable()
        self.notifying = False
        self.rtd_poll_queue()
        



class RTDCharacteristicDataDeclaration(Descriptor):
    """
    Characteristic Data Declaration Descriptor for the DataValueCharacteristic.

    """
    CDDD_DESC_UUID = '531eeeb5-ad9d-41c3-9fc7-3aaf27bb3263'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
                self, bus, index,
                self.CDDD_DESC_UUID,
                ['notify'],
                characteristic)

    def ReadValue(self, options):
        print("ReadValue in RTDCharacteristicDataDeclaration")
        value = []
        bArray = bytearray('cd062ebb-e951-44eb-9f65-de08db0b6307')
        for v in bArray:
            value.append(dbus.Byte(v))
        return value

class RTDClientCharacteristicConfigurationDescriptor(Descriptor):
    """
    CCCD descriptor.

    """
    CCCD_UUID = '2902'

    def __init__(self, bus, index, characteristic):
        self.value = []
        # 16 bit value to indicate notifications are enabled.
        self.value.append(dbus.Byte(0))
        self.value.append(dbus.Byte(1))
        self.writable = True
        Descriptor.__init__(
                self, bus, index,
                self.CCCD_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        print("ReadValue in CCCD ... RTDClientCharacteristicConfigurationDescriptor")
        return self.value

    def WriteValue(self, value, options):
        print("Write Value in CCCD ... ", str(value))
        if not self.writable:
            raise NotPermittedException()
        self.value = value

############################################################################


        
class DataValDescriptor(Descriptor):
    """
    Descriptor for the DataValueCharacteristic. Returns a static value.

    """
    #DATA_VAL_DESC_UUID = '12345678-1234-5678-1234-56789abcdef2'
    DATA_VAL_DESC_UUID = '531eeeb5-ad9d-41c3-9fc7-3aaf27bb3263'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
                self, bus, index,
                self.DATA_VAL_DESC_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('D'), dbus.Byte('a'), dbus.Byte('t'), dbus.Byte('a'), dbus.Byte(' '), dbus.Byte('V'), dbus.Byte('a'), dbus.Byte('l')
        ]


class CharacteristicUserDescriptionDescriptor(Descriptor):
    """
    Writable CUD descriptor.

    """
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        self.value = array.array('B', b'This is a characteristic for testing')
        self.value = self.value.tolist()
        Descriptor.__init__(
                self, bus, index,
                self.CUD_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value

        
        
        
############################        
        
def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None




    
##########################        
        

def main():
    global mainloop
    
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    app = Application(bus)
    
    mainloop = GObject.MainLoop()

    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                    reply_handler=register_app_cb,
                                    error_handler=register_app_error_cb)
    mainloop.run()

    
if __name__ == '__main__':
    main()
