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
    
    mTime  = unicode(datetime.now() - opLog.time)
    inTemp = opLog.indoorTemp
    setPtTemp = opLog.setpointTemp
    state = unicode(thermoStateStr[opLog.state])
    
    extTemp = wData.extTemp
    
    return jsonify({
        u'inTemp'    : inTemp,
        u'outTemp'   : extTemp,
        u'setPtTemp' : setPtTemp,
        u'opMode'    : state,
        u'dataAge'   : mTime
    })

@app.route(u'/_get_history')
def get_history():
    global ol0
    global wd0
    
    h = float(request.args.get('hours'))
    
    #perform query
    opLog = db.session.query(ol0).options(load_only("time", "state")).filter(ol0.time >= datetime.now() - timedelta(hours=h)).all()
    wData = db.session.query(wd0).options(load_only("time", "extTemp")).filter(wd0.time >= datetime.now() - timedelta(hours=h)).all()
    
    
    #extract data we care about
    opLogTimes = [x.time for x in opLog]
    opLogStates = [x.state for x in opLog]
    wDataTimes = [x.time for x in wData]
    wDataTemps = [x.extTemp for x in wData]
    
    return jsonify({
        u'opTimes'      : opLogTimes,
        u'opModes'      : opLogStates,
        u'extTempTimes' : wDataTimes,
        u'extTemps'     : wDataTemps
    })
    
@app.route(u'/')
@app.route(u'/index')

def index():
    title = u'Thermostat v0.1'
    return render_template(u"index.html", title=title)
