from datetime import datetime, date
import time
import wunderground
import thermometer
import syscontrol
import os

from app import db, models
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, InvalidRequestError

#The calculated setpoint will be between these two numbers
T_MAX_SETPOINT_C     = syscontrol.fToC(77)
T_MIN_SETPOINT_C     = syscontrol.fToC(70)

def calc_setpoint(extTemp, minSet, maxSet): #computes setpoint from external temperature
	setpoint = max(minSet, extTemp)
	setpoint = min(setpoint, maxSet)
	return round(setpoint, 2)
	
lastObsTime = None

#ensure the pin controlling the heater is set as output and is off
os.system("gpio mode 2 out");
os.system("gpio write 2 0")

while True:
    startTime = time.time();
    
    #pull current weather from wunderground.
    (obsTime, ext_temp_c) = wunderground.getTempC()
    if not ext_temp_c:
        continue

    try:
        if not lastObsTime or lastObsTime < obsTime:
            wLog = models.WeatherData(time=obsTime, extTemp = ext_temp_c)
            db.session.add(wLog)
            db.session.commit()
    except IntegrityError, InvalidRequestError:
        #Clean up from integrity violation
        db.session.rollback()
        db.session.commit()
        pass
    finally:
        lastObsTime = obsTime
        
    #4x oversample air temp reading
    temp = 0
    for i in range(0, 4):
        temp += thermometer.read_temp()[1]
        
    temp = float(temp)/4
        
    dt_meas = datetime.now()
    #print 'meas time: \t', str(dt_meas)
    #print 'int temp:  \t', temp[1]
    #print 'sys temp:  \t', temp[0]
    
    setpt = calc_setpoint(ext_temp_c, T_MIN_SETPOINT_C, T_MAX_SETPOINT_C)
    #print '\nsetpoint: \t', setpt
    
    #update the system state (see syscontrol.py)
    syscontrol.nextState(temp, ext_temp_c, setpt)
    
    #record stuff in database
    opLog = models.OperationLog(time = dt_meas, indoorTemp = temp, setpointTemp = setpt, state = syscontrol.state)
    db.session.add(opLog)
    db.session.commit()
     
    #run again 10 seconds after this loop started
    time.sleep(max(0,10-(time.time() - startTime)))