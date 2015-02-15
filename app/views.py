# -*- coding: utf-8 -*-
from flask import render_template, jsonify, request
from app import app
from app import db, models
from sqlalchemy import func, orm
from sqlalchemy.orm import load_only
import LIRCCmd
from datetime import datetime, timedelta

thermoStateStr = {
    0    : u"INIT",
    1    : u"OFF-C",
    2    : u"EXT-C",
    3    : u"AC-L",
    4    : u"AC-M",
    5    : u"AC-H",
    6    : u"OFF-H",
    7    : u"EXT-H",
    8    : u"HEAT"
}

ol0 = orm.aliased(models.OperationLog)
wd0 = orm.aliased(models.WeatherData)

def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

@app.route(u'/toggle_on_off')
def toggle_on_off():
    LIRCCmd.toggleOnOff()
    return jsonify({u'Result':u'Success'})
    
@app.route(u'/_get_current_data')
def get_current_data():
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
def get_history():
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
    wDataTimes = [unix_time(x.time) for x in wData]
    wDataTemps = [x.extTemp for x in wData]
    
    return jsonify({
        u'opTimes'      : opLogTimes,
        u'opModes'      : opLogStates,
        u'indTemps'     : opLogTemps,
        u'extTempTimes' : wDataTimes,
        u'extTemps'     : wDataTemps
    })

@app.route(u'/graphs')
def graphs():
    title = u'Thermostat v0.1'
    return render_template(u"graphs.html", title=title)
    
@app.route(u'/')
@app.route(u'/index')

def index():
    title = u'Thermostat v0.1'
    return render_template(u"index.html", title=title)
