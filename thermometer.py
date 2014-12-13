#Implements communication with the DS18B20 thermometer.

import os, glob

device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = [device_folder[0] + '/w1_slave', device_folder[1] + '/w1_slave']

def read_temp_raw():
    """Grabs raw temperature data from the sensors."""
    
    # Uncomment this to read board temperature
    #f_1 = open(device_file[0], 'r')
    #lines_1 = f_1.readlines()
    #f_1.close()
    
    f_2 = open(device_file[1], 'r')
    lines_2 = f_2.readlines()
    f_2.close()
    
    
    return lines_2


def read_temp():
    """Checks that the sensor connection was good and strips out the temperature.
    Returns a tuple of (board temperature, air temperature)."""
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':# or lines[2].strip()[-3:] != 'YES':
        print "error reading from sensor:"
        print lines
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    temp = None, float(lines[1][equals_pos+2:])/1000
    return temp