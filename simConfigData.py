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
tcConfig = {'TC0': [ 75.4334,  True,      DEGREES_F,  True],
            'TC1': [ 100.0,    True,      DEGREES_F,  False],
}

### Analog Inputs
#                            Value    Randomize      Units    Mute
analogInConfig  = { 'AI0': [ 2.5,       True,        VOLTS ,  False]
}

### Analog Outputs
#                            Value    Randomize      Units    Mute
analogOutConfig  = { 'AO0': [ 2.5,       True,       VOLTS ,  False]
}

### Digital Inputs
#                       Value    Randomize   Mute
digInConfig = { 'DI0': [ 0,      True,      False ]
}            

### Digital Outputs
#                       Value    Randomize   Mute
digOutConfig = {'DO3': [ 1,      False,      True ]
}            

####################################################################################


