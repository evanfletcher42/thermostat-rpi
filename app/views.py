# -*- coding: utf-8 -*-
from flask import render_template, jsonify
from app import app
from app import db, models
from sqlalchemy import func, orm
import LIRCCmd

thermoStateStr = {
    0    : u"INIT",
    1    : u"OFF (C)",
    2    : u"EXT",
    3    : u"AC (L)",
    4    : u"AC (M)",
    5    : u"AC (H)",
    6    : u"OFF (H)",
    7    : u"OFF (Ext)",
    8    : u"HEAT"
}

ol0 = orm.aliased(models.OperationLog)
wd0 = orm.aliased(models.WeatherData)

@app.route(u'/toggle_on_off')
def toggle_on_off():
    LIRCCmd.toggleOnOff()
    return None
    
@app.route(u'/_get_current_data')
def get_current_data():
    global ol0
    global wd0
    
    #perform query
    opLog = db.session.query(ol0).filter(ol0.id==db.session.query(ol0).with_entities(func.max(ol0.id)).one()[0])[0]
    wData = db.session.query(wd0).filter(wd0.id==db.session.query(wd0).with_entities(func.max(wd0.id)).one()[0])[0]
    
    mTime  = unicode(opLog.time)
    inTemp = unicode("%.1f" % opLog.indoorTemp) + u'°'
    setPtTemp = unicode("%.1f" % opLog.setpointTemp) + u'°'
    state = unicode(thermoStateStr[opLog.state])
    
    extTemp = unicode("%.1f" % wData.extTemp) + u'°'
    
    return jsonify({
        u'inTemp'    : inTemp,
        u'outTemp'   : extTemp,
        u'setPtTemp' : setPtTemp,
        u'opMode'    : state,
        u'date'      : mTime
    })

@app.route(u'/')
@app.route(u'/index')

def index():
    title = u'Thermostat v0.1'
    return render_template(u"index.html", title=title)
