# -*- coding: utf-8 -*-
from flask import render_template, jsonify, request
from flask.ext.basicauth import BasicAuth
from app import app
from app import db, models
from app import basic_auth
from sqlalchemy import func, orm
from sqlalchemy.orm import load_only
import BLECmd
from datetime import datetime, timedelta
import time
import parsedatetime as pdt
import re

thermoStateStr = {
    0    : u"INIT",
    1    : u"OFF-C",
    2    : u"EXT-C",
    3    : u"AC-FN",
    4    : u"AC-M",
    5    : u"AC-H",
    6    : u"OFF-H",
    7    : u"EXT-H",
    8    : u"HEAT"
}

ol0 = orm.aliased(models.OperationLog)
wd0 = orm.aliased(models.WeatherData)
st0 = orm.aliased(models.SensorTagData)

def unix_time(dt):
    """Utility function - get unix time."""
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

@app.route(u'/toggle_on_off')
@basic_auth.required
def toggle_on_off():
    BLECmd.toggleOnOff()
    return jsonify({u'Result':u'Success'})
    
@app.route(u'/_get_current_data')
def get_current_data():
    """Returns JSON describing the last thing in the system log."""
    
    global ol0
    global wd0
    
    #perform query
    opLog = db.session.query(ol0).filter(ol0.id==db.session.query(ol0).with_entities(func.max(ol0.id)).one()[0])[0]
    wData = db.session.query(wd0).filter(wd0.id==db.session.query(wd0).with_entities(func.max(wd0.id)).one()[0])[0]
    
    mTime  = unix_time(opLog.time)
    inTemp = opLog.indoorTemp
    setPtTemp = opLog.setpointTemp
    state = unicode(thermoStateStr[opLog.state])
    
    extTemp = wData.extTemp
    extTempTime = unix_time(wData.time)
    
    return jsonify({
        u'inTemp'      : inTemp,
        u'inTempTime'  : mTime,
        u'outTemp'     : extTemp,
        u'outTempTime' : extTempTime,
        u'setPtTemp'   : setPtTemp,
        u'opMode'      : state
    })

@app.route(u'/_get_history')
@basic_auth.required
def get_history():
    """Returns JSON containing the last n hours of log data."""
    
    global ol0
    global wd0
    
    h = float(request.args.get('hours'))
    
    #perform query
    opLog = db.session.query(ol0).filter(ol0.time >= datetime.now() - timedelta(hours=h)).all()
    wData = db.session.query(wd0).filter(wd0.time >= datetime.now() - timedelta(hours=h)).all()
    
    
    #extract data we care about
    opLogTimes = [unix_time(x.time) for x in opLog]
    opLogStates = [x.state for x in opLog]
    opLogTemps = [x.indoorTemp for x in opLog]
    opLogSetTemps  = [x.setpointTemp for x in opLog]
    wDataTimes = [unix_time(x.time) for x in wData]
    wDataTemps = [x.extTemp for x in wData]
    
    return jsonify({
        u'opTimes'      : opLogTimes,
        u'opModes'      : opLogStates,
        u'indTemps'     : opLogTemps,
        u'setTemps'     : opLogSetTemps,
        u'extTempTimes' : wDataTimes,
        u'extTemps'     : wDataTemps
    })

@app.route(u'/_get_st_history')
@basic_auth.required
def get_st_history():
    """Returns JSON containing the last n hours of SensorTag data."""

    global st0
    
    h = float(request.args.get('hours'))
    
    #perform query
    stLog = db.session.query(st0).filter(st0.time >= datetime.now() - timedelta(hours=h)).all()
    
    #parse through data and sort into lists for each tag.
    dataDict = dict()
    for x in stLog:
        if x.macAddr not in dataDict:
            dataDict[x.macAddr] = list()
            
        dataDict[x.macAddr].append((x.time, x.temperature, x.relHumidity))
    
    return jsonify(dataDict)
    
@app.route(u'/graphs')
@basic_auth.required
def graphs():
    title = u'Thermostat v0.1'
    return render_template(u"graphs.html", title=title)
    
@app.route(u'/schedule')
@basic_auth.required
def schedule():
    title = u'Thermostat v0.1'
    return render_template(u"schedule.html", title=title)
    
@app.route(u'/getSchedule')
@basic_auth.required
def getSchedule():
    """Returns JSON describing the current schedule.  
    Used to populate the schedule page on load."""
    
    sched = db.session.query(models.Schedule).all()
    
    sendJson = {}
    for x in sched:
        sendJson[x.id] = {}
        sendJson[x.id]['day']  = x.day
        sendJson[x.id]['tHour'] = x.time.hour
        sendJson[x.id]['tMinute'] = x.time.minute
        sendJson[x.id]['low']  = x.lowSetpoint
        sendJson[x.id]['high'] = x.highSetpoint
        
    return jsonify(sendJson);
    
@app.route(u'/scheduleSubmit', methods=['POST'])
@basic_auth.required
def scheduleSubmit():
    """Parses the submitted form and populates the schedule database."""
    # When we receive schedule data from a POST, it contains information like this:
    #
    # timepickerN	xx:XX(am/pm)
    # daypickerN	D
    # highTempBoxN	A
    # lowTempBoxN	B
    #
    # where:
    # N is an integer >= 0 acting as a unique identifier for a schedule row in this POST
    # D is an integer 0 <= D <= 6 representing the day of week Sunday...Saturday
    # xx:XX(am/pm) is a human-readable time in that format
    # A and B are floating point numbers representing minimum and maximum temperature setpoint in Deg. C
    #
    # These groups of 4 bits of data may not arrive in order, and may be mixed up with other sets.
    # Additionally, numbers N in the set are only guaranteed to be unique - not guaranteed to be consecutive.
    #
    # This method must parse this POST data, organize it into schedule information, and use it to replace the 
    # Schedule table in the database.  The controller will read this database and use it for setpoints.  
    
    # Loop through all the keys in the POST and organize it into a nested dict[N][attribute] = value
    entries = {}
    
    cal = pdt.Calendar()
    
    # loop through keys in POST, format them into nested dict
    for key in request.form:
        # key is a word ending in a number. We need to separate them.
        try:
            Nstr = re.search('(\d+)$', key).group(0)
            N = int(Nstr)
            attr = key[:(-1*len(Nstr))]
            
            # make a new nested dict if this is the first time we've seen this key
            if not (N in entries):
                entries[N]={}
                
            if attr == 'timepicker':
                (dtstruct, success) = cal.parse(request.form[key])
                if success:
                    eventTime = datetime.fromtimestamp(time.mktime(dtstruct)).time()
                else:
                    return u'Error: Failed to parse ' + key + u' value ' + request.form[key] + u'as time', 400
                
                entries[N][attr]=eventTime
                
            elif attr == 'daypicker':
                try:
                    dayInt = int(request.form[key])
                except ValueError:
                    return u'Error: Could not parse ' + key + u' value '+request.form[key] + u' as integer', 400
                    
                entries[N][attr]=dayInt
          
            elif attr == 'highTempBox' or attr == 'lowTempBox':
                try:
                    tVal = float(request.form[key])
                except ValueError:
                    return u'Error: Could not parse ' + key + u' value '+request.form[key] + u' as float', 400
                    
                entries[N][attr]=tVal
            else:
                return u'Error: Attribute ' + attr + u' is unexpected', 400
                
        except ValueError:
            return u'Error: Could not parse string ' + Nstr + u' in key ' + key + u' as integer', 400
        except AttributeError:
            return u'Error: String ' + key + u' does not contain a number', 400

    # Now that everything is organized, we first verify that we have all the information we need...
    for n in entries:
        if not (('timepicker' in entries[n]) and ('daypicker' in entries[n]) and ('highTempBox' in entries[n]) and ('lowTempBox' in entries[n])):
            return u'Error: Set ' + str(n) + u'does not contain all required entries', 400
            
        if entries[n]['lowTempBox'] > entries[n]['highTempBox']:
            return u'Error: Set ' + str(n) + u' low setpoint greater than high setpoint', 400
            
    try:
        # ...nuke the existing schedule table...
        nRowsDeleted = db.session.query(models.Schedule).delete()
        
        # ...then add things back appropriately.
        for n in entries:
            scheduleRow = models.Schedule(day = entries[n]['daypicker'], time = entries[n]['timepicker'], lowSetpoint = entries[n]['lowTempBox'], highSetpoint = entries[n]['highTempBox'])
            db.session.add(scheduleRow)
        
        # then make all changes at once.  
        db.session.commit()
        return u'Schedule Updated'
    except Exception as e:
       db.session.rollback()
       return u'Schedule Update Failed:'+type(e), 500
    
@app.route(u'/')
@app.route(u'/index')

def index():
    title = u'Thermostat v0.1'
    return render_template(u"index.html", title=title)
