from app import db

# Contains a log of what the system has been doing.
class OperationLog(db.Model):
    id              = db.Column(db.Integer, primary_key = True)
    time            = db.Column(db.DateTime, index=True, unique=True)
    indoorTemp      = db.Column(db.Float)
    setpointTemp    = db.Column(db.Float)
    state           = db.Column(db.Integer)

# Contains historical weather data.  One entry per unique observation.
class WeatherData(db.Model):
    id      = db.Column(db.Integer, primary_key = True)
    time    = db.Column(db.DateTime, index=True, unique=True)
    extTemp = db.Column(db.Float)
    
# Contains the weather forecast for the next while (in case internet goes down)
# TODO need to actually implement this
class WeatherForecast(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    time        = db.Column(db.DateTime, index=True, unique = True)
    temperature = db.Column(db.Float)
        
# Contains information about the weekly thermostat schedule.
# "events" contain a start time and a low/high setpoint temperature.
# The system queries this table for the closest time in the past and uses those settings.
# Effectively, this means that when you pass an event, those settings are used until you pass another event.
class Schedule(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    
    # Start time for the scheduled event.  
    # Use actual day/time instead of "time since Sunday 12:00" to avoid DST awkwardness.
    # Complicates controller query a little, but OH WELL.  
    day         = db.Column(db.Integer, index=True)
    time        = db.Column(db.Time, index=True)
    
    # Low/high setpoints.  
    lowSetpoint = db.Column(db.Float)
    highSetpoint = db.Column(db.Float)

# Contains SensorTag log data.  Each tag is identified by its Bluetooth address.
class SensorTagData(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    macAddr     = db.Column(db.CHAR(length=12), index=True)
    time        = db.Column(db.DateTime, index=True)
    temperature = db.Column(db.Float)
    relHumidity = db.Column(db.Float)
