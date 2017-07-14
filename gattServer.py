#!/usr/bin/env python3

###### Imports ###########

import rtdQueue

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
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

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
    #DATA_VAL_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef1'
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
#        self.add_descriptor(DataValDescriptor(bus, 0, self))
#        self.add_descriptor(
#                CharacteristicUserDescriptionDescriptor(bus, 1, self))
    
    def rtd_val_cb(self):
        self.value = []

        v = self.rtdQ.get()

        if v is not None:
            bArray = bytearray(v.encode())
            for v in bArray:
                self.value.append(dbus.Byte(v))
            print('Updating value: ' + repr(self.value))
            self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': self.value }, [])

        return self.notifying

    def rtd_val_simulation(self):
        print('Update RTD Simulation')
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
        print('Called StartNotify')
        if self.notifying:
            print('Already notifying, nothing to do')
            return
        self.notifying = True
        self.rtd_val_simulation()

    def StopNotify(self):
        print('Called StopNotify')
        if not self.notifying:
            print('Not notifying, nothing to do')
            return
        self.notifying = False
        self.rtd_val_simulation()
        
        
        
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
    
    resp = app.GetManagedObjects()
    for k,v in resp.items():
        print("key = ",k)
        print("val = ",v)
        print("\n")
    

    mainloop = GObject.MainLoop()

    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                    reply_handler=register_app_cb,
                                    error_handler=register_app_error_cb)

                                    
    rq = rtdQueue.RTDQueue()
    rq.put('TC0174.53F')
    rq.put('TC0175.00F')
    rq.put('TC0176.00F')
    rq.put('TC0177.00F')
    rq.put('TC0178.00F')
    rq.put('TC0179.00F')
    rq.put('TC0180.00F')
    rq.put('TC0181.00F')    
    mainloop.run()

    
    
    
    
    
    
    
    
    
    
if __name__ == '__main__':
    main()
