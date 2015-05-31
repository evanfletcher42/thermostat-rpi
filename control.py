from datetime import datetime, date
import time
import wunderground
import thermometer
import syscontrol
import os

from app import db, models
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

#The calculated setpoint will be between these two numbers
T_MAX_SETPOINT_C     = syscontrol.fToC(77)
T_MIN_SETPOINT_C     = syscontrol.fToC(70)

def calc_setpoint(extTemp, minSet, maxSet): #computes setpoint from external temperature
	setpoint = max(minSet, extTemp)
	setpoint = min(setpoint, maxSet)
	return round(setpoint, 2)
	
lastObsTime = None

#ensure the pin controlling the heater is set as output and is off
print "Set up GPIO...",
os.system("gpio mode 2 out");
os.system("gpio write 2 0")
print "Done"

print "System running"

while True:
    startTime = time.time();
    
    obsTime = None
    ext_temp_c = None
    
    #pull current weather from wunderground.
    wgdata = wunderground.getTempC()
    if wgdata:
        (obsTime, ext_temp_c) = wgdata
    else:
        print "control: wunderground returned None"

    try:
        if wgdata and (not lastObsTime or lastObsTime < obsTime):
            wLog = models.WeatherData(time=obsTime, extTemp = ext_temp_c)
            db.session.add(wLog)
            db.session.commit()
    except IntegrityError, InvalidRequestError:
        #Clean up from integrity violation
        print "Cleaning up DB integrity violation...",
        db.session.rollback()
        db.session.commit()
        print "Done"
        pass
    finally:
        if obsTime:
            lastObsTime = obsTime
        
    #4x oversample air temp reading
    temp = 0
    for i in range(0, 4):
        temp += thermometer.read_temp()[1]
        
    temp = float(temp)/4
        
    dt_meas = datetime.now()
    time_now = dt_meas.time()
    #datetime weekday is 0 on monday and 6 on sunday.  We need 0 on Sunday, 1 on Monday, ...
    dayOfWeekNow = (dt_meas.weekday()+1)%7
    
    #query the database in order to get the most recent setpoint in the schedule.
    minSetpt = T_MIN_SETPOINT_C
    maxSetpt = T_MAX_SETPOINT_C
    try:
        result = db.session.query(models.Schedule)\
        .order_by(models.Schedule.day.desc(), models.Schedule.time.desc())\
        .filter(models.Schedule.time <= time_now, models.Schedule.day <= dayOfWeekNow)\
        .first()
        
        minSetpt = result.lowSetpoint
        maxSetpt = result.highSetpoint
    except NoResultFound:
        #If we get nothing, it means we've wrapped around Sunday 00:00 and need to use the "last" one.
        #If this dies too, that means the DB is empty, in which case we fall back on defaults.
        try:
            result = db.session.query(models.Schedule)\
            .order_by(models.Schedule.day.desc(), models.Schedule.time.desc())\
            .first()
            
            minSetpt = result.lowSetpoint
            maxSetpt = result.highSetpoint
        except NoResultFound:
            print "Warning: DB seems empty.  Using default min/max setpoint"
    
    #print 'meas time: \t', str(dt_meas)
    #print 'int temp:  \t', temp[1]
    #print 'sys temp:  \t', temp[0]
    
    setpt = calc_setpoint(ext_temp_c, minSetpt, maxSetpt)
    #print '\nsetpoint: \t', setpt
    
    #update the system state (see syscontrol.py)
    syscontrol.nextState(temp, ext_temp_c, setpt, minSetpt, maxSetpt)
    
    #record stuff in database
    try:
        opLog = models.OperationLog(time = dt_meas, indoorTemp = temp, setpointTemp = setpt, state = syscontrol.state)
        db.session.add(opLog)
        db.session.commit()
    except:
        #fail gracefully (just don't log this time) if the DB is busy.  Probably means someone's updating the schedule
        #note: switch to postgreSQL soon for that sweet concurrency.  Also maybe a real webserver.
        db.session.rollback()
     
    #run again 10 seconds after this loop started
    time.sleep(max(0,10-(time.time() - startTime)))