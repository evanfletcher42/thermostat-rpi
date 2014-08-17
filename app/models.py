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
    DISABLE_ALL,    \       # 0  = Disable system entirely (everything off)
    DISABLE_HEAT,   \       # 1  = Prevent heating
    DISABLE_COOL,   \       # 2  = Prevent cooling
    FORCE_SETPT,    \       # 3  = Force setpoint to value in argument
    FORCE_FAN_LOW,  \       # 4  = Force operating mode to FAN (Low)
    FORCE_FAN_MED,  \       # 5  = Force operating mode to FAN (Med)
    FORCE_FAN_HI,   \       # 6  = Force operating mode to FAN (High)
    FORCE_AC_LOW,   \       # 7  = Force operating mode to AC (Low)
    FORCE_AC_MED,   \       # 8  = Force operating mode to AC (Med)
    FORCE_AC_HI,    \       # 9  = Force operating mode to AC (High)
    FORCE_HEAT = range(11)  # 10 = Force operating mode to HEAT
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