from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
	title = 'Thermostat v0.1'
	indoorTemp 	= '73.0°'
	outdoorTemp = '68.7°'
	setpointTemp = '70.0°'
	explainStrings = [ #fake array of explain messages
		"The set point is 70.0°, because I'm not allowed to make it colder.",
		"The operating mode is OFF because it's cooler than 70.0° outside and you should just open a window."
	]
	return render_template("index.html", title=title, indoorTemp=indoorTemp, outdoorTemp=outdoorTemp, setpointTemp=setpointTemp, explainStrings=explainStrings )
