# -*- coding: utf-8 -*-
from flask import render_template, jsonify
from app import app
from app import db, models

thermoStateStr = {
    0    : u"INIT",
    1    : u"OFF (C)",
    2    : u"OFF (Ext)",
    3    : u"AC (Low)",
    4    : u"AC (Med)",
    5    : u"AC (High)",
    6    : u"OFF (H)",
    7    : u"OFF (Ext)",
    8    : u"HEAT"
}

@app.route('/_get_current_data')
def get_current_data():
    opLog = models.OperationLog.query.order_by(u"-id").first()
    mTime  = unicode(opLog.time)
    inTemp = unicode(opLog.indoorTemp) + u'°'
    setPtTemp = unicode(opLog.setpointTemp) + u'°'
    state = thermoStateStr[opLog.state]
    
    wData = models.WeatherData.query.order_by(u"-id").first()
    extTemp = unicode(wData.extTemp) + u'°'
    
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
    return render_template(u"index.html", title=title, explainStrings=[])
