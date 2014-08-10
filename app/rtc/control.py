from datetime import datetime
import os, glob, time, sys
from metar import Metar
import urllib2

#HACK: Redirect stdout to file because regular piping isn't working for some reason.
f = file('runLog.txt', 'a')
sys.stdout = f

def cToF(tempC): #function that converts Celsius to Fahrenheit 
    return float(tempC)*9/5 + 32
    
def fToC(tempF): #function that converts Fahrenheit to Celsius
    return (float(tempF) - 32)*5/9

#The calculated setpoint will be between these two numbers
T_MAX_SETPOINT_C    = fToC(77)
T_MIN_SETPOINT_C    = fToC(70)

#If AC mode and temp > setpoint, AC will turn on.
#AC will turn off when temp drops below setpoint - T_COOL_THRESH_C
T_COOL_HYST_C     = 1

#If HEAT mode and temp < setpoint, HEAT will turn on.
#AC will turn off when temp climbs above setpoint + T_HEAT_THRESH_C
T_HEAT_HYST_C     = 1

#Mode will switch from heat to cool if temperature goes above this
T_COOL_MODE_C       = fToC(79)

#Mode will switch from cool to heat if temperature goes below this
T_HEAT_MODE_C       = fToC(65)

# enum describing thermostat state
class thermoState:
    INIT,       \
    COOL_OFF,   \
    COOL_EXT,   \
    COOL_LOW,   \
    COOL_MED,   \
    COOL_HIGH,  \
    HEAT_OFF,   \
    HEAT_EXT,   \
    HEAT_ON     = range(9)
    
thermoStateStr = {
    thermoState.INIT        : "INIT",
    thermoState.COOL_OFF    : "OFF (C)",
    thermoState.COOL_EXT    : "OFF (Ext)",
    thermoState.COOL_LOW    : "AC (Low)",
    thermoState.COOL_MED    : "AC (Med)",
    thermoState.COOL_HIGH   : "AC (High)",
    thermoState.HEAT_OFF    : "OFF (H)",
    thermoState.HEAT_EXT    : "OFF (Ext)",
    thermoState.HEAT_ON     : "HEAT"
}

#--- State Transition Functions ---
# These all take (tInt, tExt, tSet) as arguments and return the next state.
# If real-time functions need to happen on a state edge (i.e. turn on/off AC),
# they should go in these functions.
# (this is essentially a Pythonic switch-case)

def tSInit(tInt, tExt, tSet):
    #TODO consider weather forecast in initialization
    return thermoState.COOL_OFF
        
def tSCoolOff(tInt, tExt, tSet):
    #First check if we should even be in heating mode
    if tInt < T_HEAT_MODE_C:
        return thermoState.HEAT_OFF
    
    #Do we need to modify the temperature?
    if tInt > tSet:
        if tExt <= tSet:
            return thermoState.COOL_EXT
        return thermoState.COOL_MED
        
    return thermoState.COOL_OFF
    
def tSCoolExt(tInt, tExt, tSet):
    if tExt <= tSet and tInt > tSet:
        return thermoState.COOL_EXT
    
    return thermoState.COOL_OFF
    
def tSCoolLow(tInt, tExt, tSet):
    #TODO figure out if fan speed control helps AC.  Until then use medium only
    return thermoState.COOL_MED
    
def tSCoolMed(tInt, tExt, tSet):
    #check if done cooling the place off (has hysteresis to allow for air mixing)
    if tInt <= tSet - T_COOL_HYST_C:
        return thermoState.COOL_OFF
        
    #check if we should open a window rather than waste power with AC
    if tExt <= tSet:
        return thermoState.COOL_EXT
     
    return thermoState.COOL_MED
    
def tSCoolHigh(tInt, tExt, tSet):
    #TODO figure out if fan speed control helps AC.  Until then use medium only
    return thermoState.COOL_MED
    
def tSHeatOff(tInt, tExt, tSet):
    #First check if we should even be in heating mode
    if tInt > T_COOL_MODE_C:
        return thermoState.COOL_OFF
    
    #Do we need to modify the temperature?
    if tInt < tSet:
        if tExt >= tSet:
            return thermoState.HEAT_EXT
        return thermoState.HEAT_ON
        
    return thermoState.HEAT_OFF
    
def tSHeatExt(tInt, tExt, tSet):
    if tExt >= tSet and tInt < tSet:
        return thermoState.HEAT_EXT
    
    return thermoState.HEAT_OFF
    
def tSHeatOn(tInt, tExt, tSet):
    #check if done heating the place (has hysteresis to allow for air mixing)
    if tInt >= tSet + T_HEAT_HYST_C:
        return thermoState.COOL_OFF
        
    #check if we should open a window rather than waste power with heating
    if tExt >= tSet:
        return thermoState.HEAT_EXT
     
    return thermoState.HEAT_ON
  
state = thermoState.INIT  # The state variable.  This is global.

thermoStateTrFcn = {
    thermoState.INIT        : tSInit,
    thermoState.COOL_OFF    : tSCoolOff,
    thermoState.COOL_EXT    : tSCoolExt,
    thermoState.COOL_LOW    : tSCoolLow,
    thermoState.COOL_MED    : tSCoolMed,
    thermoState.COOL_HIGH   : tSCoolHigh,
    thermoState.HEAT_OFF    : tSHeatOff,
    thermoState.HEAT_EXT    : tSHeatExt,
    thermoState.HEAT_ON     : tSHeatOn
}

def nextState(tInt, tExt, tSet): #function that computes next state given current state and temps
    global state
    nextState = thermoStateTrFcn[state](tInt, tExt, tSet)
    #if nextState != state:
        #print thermoStateStr[state], " -> ", thermoStateStr[nextState] #TMPD debug
        #TODO update the database r/e this
    
    state = nextState;
    
    
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
        print "error reading from sensor:"
        print lines
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t='), lines[3].find('t=')
    temp = float(lines[1][equals_pos[0]+2:])/1000, float(lines[3][equals_pos[1]+2:])/1000
    return temp

def calc_setpoint(extTemp, minSet, maxSet): #computes setpoint from external temperature
	setpoint = max(minSet, extTemp)
	setpoint = min(setpoint, maxSet)
	return round(setpoint, 2)
	
iterCount = 0;
ITER_REPRINT_HEAD = 30;
while True:
    startTime = time.time();
    
    # pull the latest raw METAR data and parse it
    metar_str = ""
    data = urllib2.urlopen("http://w1.weather.gov/data/METAR/KBDU.1.txt") 
    for line in data:
        if line.startswith('METAR') or line.startswith('SPECI'):
            metar_str = line
            break
    data.close()
    
    obs = Metar.Metar(metar_str)
    
    location   = obs.station_id
    dt_weather = obs.time
    ext_temp_c = obs.temp.value(units="C")

    #print 'location: \t', location
    #print 'obs time: \t', str(dt_weather)
    #print 'ext temp: \t', ext_temp_c

    device_folder = glob.glob('/sys/bus/w1/devices/28*')
    device_file = [device_folder[0] + '/w1_slave', device_folder[1] + '/w1_slave']

    temp = read_temp() #get the temp
    dt_meas = datetime.now()
    #print 'meas time: \t', str(dt_meas)
    #print 'int temp:  \t', temp[1]
    #print 'sys temp:  \t', temp[0]

    setpt = calc_setpoint(ext_temp_c, T_MIN_SETPOINT_C, T_MAX_SETPOINT_C)
    #print '\nsetpoint: \t', setpt
    
    nextState(temp[1], ext_temp_c, setpt)
    
    if iterCount == 0:
        print "Time \t\t\t\tT_int \tT_ext \tT_set \tState"
    
    print str(dt_meas), "\t", temp[1], "\t", ext_temp_c, "\t", setpt, "\t", thermoStateStr[state]
    iterCount = (iterCount + 1) % ITER_REPRINT_HEAD
    f.flush()
    time.sleep(10-(time.time() - startTime))
#TODO update the database about all of the above