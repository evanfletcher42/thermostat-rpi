import pywapi
import pprint
import rfc822
from datetime import datetime
import os, glob, time, sys

MAX_SETPOINT_C = (77-32)*5/9
MIN_SETPOINT_C = (70-32)*5/9

def read_temp_raw(): #a function that grabs the raw temperature data from the sensor
    f_1 = open(device_file[0], 'r')
    lines_1 = f_1.readlines()
    f_1.close()
    f_2 = open(device_file[1], 'r')
    lines_2 = f_2.readlines()
    f_2.close()
    return lines_1 + lines_2


def read_temp(): #a function that checks that the connection was good and strips out the temperature
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES' or lines[2].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t='), lines[3].find('t=')
    temp = float(lines[1][equals_pos[0]+2:])/1000, float(lines[3][equals_pos[1]+2:])/1000
    return temp

def calc_setpoint(extTemp, minSet, maxSet): #computes setpoint from external temperature
	setpoint = max(minSet, extTemp)
	setpoint = min(setpoint, maxSet)
	return setpoint
	
result = pywapi.get_weather_from_noaa('KBDU')

location   = result['location']
dt_weather =  datetime.fromtimestamp(rfc822.mktime_tz(rfc822.parsedate_tz(result['observation_time_rfc822'])))
ext_temp_c = float(result['temp_c'])

print 'location: \t', location
print 'obs time: \t', str(dt_weather)
print 'ext temp: \t', ext_temp_c

device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = [device_folder[0] + '/w1_slave', device_folder[1] + '/w1_slave']

temp = read_temp() #get the temp
dt_meas = datetime.now()
print 'meas time: \t', str(dt_meas)
print 'int temp:  \t', temp[1]
print 'sys temp:  \t', temp[0]

setpt = calc_setpoint(ext_temp_c, MIN_SETPOINT_C, MAX_SETPOINT_C)
print '\nsetpoint: \t', setpt