from app import db

class OperationLog(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	time = db.Column(db.DateTime, index=True, unique=True)
	indoorTemp = db.Column(db.Float)
	outdoorTemp = db.Column(db.Float)
	outdoorHumidity = db.Column(db.Float)
	mode = db.Column(db.Integer)
	reason = db.Column(db.Integer)

class WeatherForecast(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	time = db.Column(db.DateTime, index=True, unique = True)
	temperature = db.Column(db.Float)
	humidity = db.Column(db.Float)
	
class Command(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	tStart = db.Column(db.DateTime, index=True)
	tEnd = db.Column(db.DateTime, index=True)
	command = db.Column(db.Integer)
