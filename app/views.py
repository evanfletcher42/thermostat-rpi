# -*- coding: utf-8 -*-
from flask import render_template, jsonify
from app import app
from app import db, models
from sqlalchemy import func

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

#set up query objects
opLog = models.OperationLog.query.order_by(u"-id").first()
wData = models.WeatherData.query.order_by(u"-id").first()

@app.route(u'/_get_current_data')
def get_current_data():
    global oplog
    global wdata
    
    mTime  = unicode(opLog.time)
    inTemp = unicode("%.1f" % opLog.indoorTemp) + u'°'
    setPtTemp = unicode("%.1f" % opLog.setpointTemp) + u'°'
    state = unicode(thermoStateStr[opLog.state])
    
    extTemp = unicode("%.1f" % wData.extTemp) + u'°'
    
    return jsonify({
        u'inTemp'    : inTemp,
        u'outTemp'   : extTemp,
        u'setPtTemp' : setPtTemp,
        u'opMode'    : state
    })

@app.route(u'/')
@app.route(u'/index')

def index():
    title = u'Thermostat v0.1'
    return render_template(u"index.html", title=title, explainStrings=[u'Test string'])
