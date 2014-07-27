# -*- coding: utf-8 -*-
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
	title = u'Thermostat v0.1'
	indoorTemp 	= u'73.0'
	outdoorTemp = u'68.7'
	setpointTemp = u'70.0'
	opMode = u'OFF'
	explainStrings = [ #fake array of explain messages
		u"The set point is 70.0, because I'm not allowed to make it colder.",
		u"The operating mode is OFF because it's cooler than 70.0 outside and you should just open a window."
	]
	return render_template(u"index.html", title=title, indoorTemp=indoorTemp, outdoorTemp=outdoorTemp, setpointTemp=setpointTemp, opMode = opMode, explainStrings=explainStrings )
