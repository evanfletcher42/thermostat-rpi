from datetime import datetime, date
import time
import wunderground
import thermometer
import syscontrol
import pidcontroller
import os

from app import db, models
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

# If the schedule DB isn't working, the calculated setpoint
# will be between these two numbers.
T_MAX_SETPOINT_C     = syscontrol.fToC(77)
T_MIN_SETPOINT_C     = syscontrol.fToC(70)

# this is useful for timing heater stuff.
epoch = datetime.utcfromtimestamp(0)

def calc_setpoint(extTemp, minSet, maxSet): 
    """Computes setpoint from external temperature."""
    if extTemp is not None:
        setpoint = max(minSet, extTemp)
        setpoint = min(setpoint, maxSet)
        return setpoint
    else:
        # Make a guess.
        return (maxSet + minSet)/2
    
# ensure the pin controlling the heater is set as output and is off
print "Set up GPIO...",
os.system("/usr/local/bin/gpio mode 2 out");
os.system("/usr/local/bin/gpio write 2 0")
print "Done"

print "Init Wunderground..."
wunderground.init()
print "Done"

print "Init PID"
pid = pidcontroller.PIDController()
print "Done"

print "System running"

# Main loop
while True:

    # Time each iteration to ensure things run every 10s
    startTime = time.time();
    
    # --- Weather Underground data pull ---
    ext_temp_c = wunderground.getTempC() #Note: This CAN return None.
        
    # --- Internal Local Temperature Measure - DS18B20 ---
    
    # 4x oversample air temp reading
    temp = 0
    for i in range(0, 4):
        temp += thermometer.read_temp()[1]
        
    temp = float(temp)/4
        
    # --- Pull schedule, get setpoint limits ---
    
    dt_meas = datetime.now()
    time_now = dt_meas.time()
    # datetime weekday is 0 on monday and 6 on sunday.  We need 0 on Sunday, 1 on Monday, ...
    dayOfWeekNow = (dt_meas.weekday()+1)%7
    
    # query the database in order to get the most recent setpoint in the schedule.
    minSetpt = T_MIN_SETPOINT_C
    maxSetpt = T_MAX_SETPOINT_C
    
    result = db.session.query(models.Schedule)\
    .order_by(models.Schedule.day.desc(), models.Schedule.time.desc())\
    .filter(or_(models.Schedule.day < dayOfWeekNow, and_(models.Schedule.day == dayOfWeekNow, models.Schedule.time <= time_now)))\
    .first()
    
    if result is not None:
        minSetpt = result.lowSetpoint
        maxSetpt = result.highSetpoint
    else:
        #If we get nothing, it means we've wrapped around Sunday 00:00 and need to use the "last" one.
        #If this dies too, that means the DB is empty, in which case we fall back on defaults.
        result = db.session.query(models.Schedule)\
        .order_by(models.Schedule.day.desc(), models.Schedule.time.desc())\
        .first()
        
        if result is not None:
            minSetpt = result.lowSetpoint
            maxSetpt = result.highSetpoint
        else:
            print "Warning: DB seems empty.  Using default min/max setpoint."
    
    # --- Calculate setpoint and execute system changes ---
    
    #print 'meas time: \t', str(dt_meas)
    #print 'int temp:  \t', temp[1]
    #print 'sys temp:  \t', temp[0]
    
    setpt = calc_setpoint(ext_temp_c, minSetpt, maxSetpt)
    #print '\nsetpoint: \t', setpt
    
    #update PID controller
    pidResult = pid.update(temp, setpt)
    
    #update the system state (see syscontrol.py)
    secondsSinceEpoch = (dt_meas - epoch).total_seconds()
    syscontrol.nextState(temp, ext_temp_c, setpt, minSetpt, maxSetpt, pidResult, secondsSinceEpoch)
    
    # --- Save to database ---
    
    try:
        opLog = models.OperationLog(time = dt_meas, indoorTemp = temp, setpointTemp = setpt, state = syscontrol.state)
        db.session.add(opLog)
        db.session.commit()
    except:
        # fail gracefully (just don't log this time) if the DB is busy.  Probably means someone's updating the schedule
        # Even if stuff isn't being logged, temperature control will still work.
        db.session.rollback()
     
    #run again 10 seconds after this loop started
    time.sleep(max(0,10-(time.time() - startTime)))
