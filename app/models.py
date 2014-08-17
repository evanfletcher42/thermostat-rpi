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
    
# Valid commands for schedule.
class Commands:
    DISABLE_ALL,    \
    DISABLE_HEAT,   \
    DISABLE_COOL,   \
    FORCE_SETPT,    \
    FORCE_FAN_LOW,  \
    FORCE_FAN_MED,  \
    FORCE_FAN_HI,   \
    FORCE_AC_LOW,   \
    FORCE_AC_MED,   \
    FORCE_AC_HI,    \
    FORCE_HEAT = range(11)
    # ... (add more here)
    
# Contains information about scheduled events (i.e. disabling stuff while away)
class Schedule(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    
    # Start and end times for the first time this event took place.
    # For repeating events, new start/end times are based on these.
    tStartFirst = db.Column(db.DateTime, index=True)
    tEndFirst   = db.Column(db.DateTime, index=True)
    
    # 0=never, 1=daily, 2=weekly, 3=monthly, 4=annual
    repeatType  = db.Column(db.Integer)
    
    # End time of the last time this will repeat.  NONE if forever.
    tEndLast    = db.Column(db.DateTime)
    
    # Start/end times for the next time this event will take place.
    # Useful for fast db lookup / must be maintained by program
    tNextStart  = db.Column(db.DateTime, index=True)
    tNextEnd    = db.Column(db.DateTime, index=True)
    
    # What this event is supposed to do.  Uses values from "commands" enum above.
    command     = db.Column(db.Integer)
    
    # Optional float argument for a command.  
    argument    = db.Column(db.Float)