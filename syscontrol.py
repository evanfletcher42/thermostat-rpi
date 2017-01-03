# Implements system-level controls. States, state transitions, IR controls, etc.
# Imported as a module into a high-level controller (which determines setpoint and schedule).

#import LIRCCmd
import LIRCCmd
import os
import time


# ---- Utility functions ---
# function that converts Celsius to Fahrenheit
def cToF(tempC): 
    return float(tempC)*9/5 + 32
    
# function that converts Fahrenheit to Celsius
def fToC(tempF): 
    return (float(tempF) - 32)*5/9

# ---- Behavior Constants ----

# If AC mode and temp > setpoint, AC will turn on.
# AC will turn off when temp drops below setpoint - T_COOL_THRESH_C
T_COOL_HYST_C     = 0.5

# If HEAT mode and temp < setpoint, HEAT will turn on.
# AC will turn off when temp climbs above setpoint + T_HEAT_THRESH_C
T_HEAT_HYST_C     = 0.05

# The PID controller will be overridden if temp < (setpoint - T_HEAT_PERMIT_OFFSET)
T_HEAT_PERMIT_OFFSET = 2.0

# When using PID control, the PWM period is this many seconds long.
PWM_PERIOD_S = 60*20;

# ---- State Transition Stuff ---
# timer variable for COOL_FAN state
__timeStartCoolCoil = 0 

# How long in seconds to remain in COOL_FAN state before turning off
TIME_COOL_COIL = 60

# enum describing thermostat state
class thermoState:
    INIT,       \
    COOL_OFF,   \
    COOL_EXT,   \
    COOL_FAN,   \
    COOL_MED,   \
    COOL_HIGH,  \
    HEAT_OFF,   \
    HEAT_EXT,   \
    HEAT_ON     = range(9)

# dict containing the human-readable form of the above states
thermoStateStr = {
    thermoState.INIT        : "INIT",
    thermoState.COOL_OFF    : "OFF (C)",
    thermoState.COOL_EXT    : "OFF (Ext)",
    thermoState.COOL_FAN    : "AC (Fan)",
    thermoState.COOL_MED    : "AC (Med)",
    thermoState.COOL_HIGH   : "AC (High)",
    thermoState.HEAT_OFF    : "OFF (H)",
    thermoState.HEAT_EXT    : "OFF (Ext)",
    thermoState.HEAT_ON     : "HEAT"
}

# --- State Transition Functions ---
# These all take (tInt, tExt, tSet) as arguments and return the next state.
# If stately real-time functions need to happen on a state edge (i.e. AC unit on_stop),
# they should go in these functions.  Otherwise let the config test in nextState() take
# care of things.

def tSInit(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    # TODO consider weather forecast in initialization
    
    # For now, if it's colder outside than inside, go into heat mode.  
    # TODO: Initialize to last state in DB, or if DB empty, use this
    if tExt < tInt:
        print "syscontrol: Starting in OFF-H"
        return thermoState.HEAT_OFF
    else:
        print "syscontrol: Starting in OFF-C"
        return thermoState.COOL_OFF
        
def tSCoolOff(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    # First check if we should switch to heat mode
    if tInt < minSetpt:
        return thermoState.HEAT_OFF
    
    # Do we need to modify the temperature?
    if tInt > tSet:
        if tExt <= tSet:
            return thermoState.COOL_EXT
            
        LIRCCmd.toggleOnOff()
        return thermoState.COOL_HIGH
        
    return thermoState.COOL_OFF
    
def tSCoolExt(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    if tExt <= tSet and tInt > tSet:
        return thermoState.COOL_EXT

    return thermoState.COOL_OFF
    
def tSCoolFan(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    # Check if the temperature needs to change.
    if tInt > tSet:
        if tExt <= tSet:
            LIRCCmd.toggleOnOff()
            return thermoState.COOL_EXT
        
        return thermoState.COOL_HIGH
        
    # Shut off the fan after TIME_COOL_COIL (coils are reasonably expected to warm up by now)
    if time.time() >= __timeStartCoolCoil + TIME_COOL_COIL:
        LIRCCmd.toggleOnOff()
        return thermoState.COOL_OFF
    
    return thermoState.COOL_FAN
    
def tSCoolMed(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    # TODO figure out if fan speed control helps AC.  Until then use high only
    return thermoState.COOL_HIGH
    
def tSCoolHigh(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    global __timeStartCoolCoil
    
    # check if done cooling the place off (has hysteresis to allow for air mixing)
    if tInt <= tSet - T_COOL_HYST_C:
        __timeStartCoolCoil = time.time()
        return thermoState.COOL_FAN
        
    # check if we should open a window rather than waste power with AC
    if tExt <= tSet:
        LIRCCmd.toggleOnOff()
        return thermoState.COOL_EXT
     
    return thermoState.COOL_HIGH
    
def tSHeatOff(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    # First check if we should even be in heating mode
    if tInt > maxSetpt:
        return thermoState.COOL_OFF
    
    # Do we need to force the heat on? (bad PID)
    if tInt < tSet - T_HEAT_PERMIT_OFFSET:
        if tExt >= tSet:
            return thermoState.HEAT_EXT
        return thermoState.HEAT_ON
        
    # Do we need to force the heat to stay off? (bad PID)
    if tInt > tSet + T_HEAT_PERMIT_OFFSET
        return thermoState.HEAT_OFF
    
    # So long as the PID controller is behaving, does it say we should be heating now?
    if pidResult*PWM_PERIOD_S > time % PWM_PERIOD_S
        if tExt >= tSet:
            return thermoState.HEAT_EXT
        return thermoState.HEAT_ON
        
    return thermoState.HEAT_OFF
    
def tSHeatExt(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    if tExt >= tSet and tInt < tSet:
        return thermoState.HEAT_EXT
    
    return thermoState.HEAT_OFF
    
def tSHeatOn(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    # check if we should open a window rather than waste power with heating
    if tExt >= tSet:
        return thermoState.HEAT_EXT
        
    # Do we need to force the heat off? (bad PID)
    if tInt >= tSet + T_HEAT_PERMIT_OFFSET:
        return thermoState.HEAT_OFF

    # Do we need to force the heat to stay on? (bad PID)
    if tInt < tSet - T_HEAT_PERMIT_OFFSET:
        return thermoState.HEAT_ON
        
    # So long as the PID controller is behaving, does it say we should be heating now?
    if pidResult*PWM_PERIOD_S > time % PWM_PERIOD_S
        return thermoState.HEAT_ON
    
    return thermoState.HEAT_OFF
  
state = thermoState.INIT  # The state variable.  This is global.

# dict mapping states to their transition functions
thermoStateTrFcn = {
    thermoState.INIT        : tSInit,
    thermoState.COOL_OFF    : tSCoolOff,
    thermoState.COOL_EXT    : tSCoolExt,
    thermoState.COOL_FAN    : tSCoolFan,
    thermoState.COOL_MED    : tSCoolMed,
    thermoState.COOL_HIGH   : tSCoolHigh,
    thermoState.HEAT_OFF    : tSHeatOff,
    thermoState.HEAT_EXT    : tSHeatExt,
    thermoState.HEAT_ON     : tSHeatOn
}

# configuration functions - contain static stuff that will always need to happen when
# entering a given state.  While calling these may result in unnecessary commands being
# sent (i.e. AC unit already in fan mode), there's some gain in consistency here.
# TODO: Consider keeping track of AC unit states in the db and only send necessary commands?
def cfgInit():
    #stub - this is a temporary state in which we figure out whether to heat or cool
    pass
    
def cfgCoolOff():
    # stub - AC unit is off in this case
    pass
    
def cfgCoolExt():
    # stub - AC unit is off in this state
    pass

def cfgCoolFan():
    # Low fan in this state since AC unit will still be cold after compressor shutdown.
    LIRCCmd.setFanMode()
    LIRCCmd.setFanLow()

def cfgCoolMed():
    LIRCCmd.setCoolMode()
    LIRCCmd.setFanMed()

def cfgCoolHigh():
    LIRCCmd.setCoolMode()
    LIRCCmd.setFanHi()

def cfgHeatOff():
    os.system("/usr/local/bin/gpio write 2 0")
    pass

def cfgHeatExt():
    os.system("/usr/local/bin/gpio write 2 0")
    pass

def cfgHeatOn():
    os.system("/usr/local/bin/gpio write 2 1")
    pass

# dict mapping states to their config functions
thermoStateCfgFcn = {
    thermoState.INIT        : cfgInit,
    thermoState.COOL_OFF    : cfgCoolOff,
    thermoState.COOL_EXT    : cfgCoolExt,
    thermoState.COOL_FAN    : cfgCoolFan,
    thermoState.COOL_MED    : cfgCoolMed,
    thermoState.COOL_HIGH   : cfgCoolHigh,
    thermoState.HEAT_OFF    : cfgHeatOff,
    thermoState.HEAT_EXT    : cfgHeatExt,
    thermoState.HEAT_ON     : cfgHeatOn
}

def nextState(tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time):
    """Computes next state given current state and temps"""
    global state
    nextState = thermoStateTrFcn[state](tInt, tExt, tSet, minSetpt, maxSetpt, pidResult, time)
    if nextState != state:
        # configure system for new state.
        thermoStateCfgFcn[nextState]()
    
    state = nextState
