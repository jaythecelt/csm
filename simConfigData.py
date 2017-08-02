'''
Constants and Configuration data for simulation

{"TC": {"TC0": [78.9337934710637, "F"]}, "AI": {"AI0": [5.102922332635204, "V"]}, "DI": {"DI0": 1}}

'''
################ Constants #########################
#Units
DEGREES_F = 'F'
DEGREES_C = 'C'
VOLTS = 'V'
AMPS = 'A'


############ Sensor Configuration Data ################################################

### Thermocouple configuration (Python dictionary of tuples) ###
#                    Value     Randomize  Units       Mute
tcConfig = {'TC0': [ 100.0,    True,      DEGREES_F,  False],
}

### Humidity Sensor Inputs
#                       Value    Randomize   Mute
hmConfig = { 'H0': [ 99000,  True,       False ]
}            





### Analog Inputs
#                            Value    Randomize      Units    Mute
analogInConfig  = { 'AI0': [ 2.5,       True,        VOLTS ,  True]
}

### Analog Outputs
#                            Value    Randomize      Units    Mute
analogOutConfig  = { 'AO0': [ 2.5,       True,       VOLTS ,  True]
}

### Digital Inputs
#                       Value    Randomize   Mute
digInConfig = { 'DI0': [ 0,      True,      True ]
}            

### Digital Outputs
#                       Value    Randomize   Mute
digOutConfig = {'DO3': [ 1,      False,      True ]
}            

####################################################################################


