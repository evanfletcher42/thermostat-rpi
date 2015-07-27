import urllib2, json, socket
from datetime import datetime
import time, rfc822
from app import db, models
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func, orm
from collections import deque
import sys

# Set this to a safe value with respect to Wunderground API limits.
__MIN_UPDATE_PERIOD_SECONDS = 5*60

# Extrapolate based on the last N data points.
# This is hard-coded linear for now.  May generalize to Nth-order polynomial later.
__EXTRAPOLATE_HISTORY_N = 2

# Only allow extrapolation for this many seconds past the last data point, then cut it off.
__EXTRAPOLATE_TIME_LIMIT_S = 60*15

# Contains the last n data points, type Models.WeatherData.
__history = deque()

# When (in system time) we last pulled data from Wunderground.  Init to 0 so we pull on first request.
__lastUpdateTime = 0;

dataIsNew = True

wd0 = orm.aliased(models.WeatherData)

def init():
    global __EXTRAPOLATE_HISTORY_N
    try:
        wData = db.session.query(wd0).order_by(wd0.time.desc()).limit(__EXTRAPOLATE_HISTORY_N)
        
        #Data comes in reversed (Newest .... Oldest), so fix that
        for x in wData:
            __history.appendleft(x)
        
    except NoResultFound:
        print "wunderground: Warning: No temperature history found."
        pass;


def update_weather():
    global __MIN_UPDATE_PERIOD_SECONDS
    global __lastUpdateTime
    global __history
    
    if time.time() - __lastUpdateTime > __MIN_UPDATE_PERIOD_SECONDS:
        # update __lastUpdateTime regardless of web success.  Don't want to hit a broken Wunderground too fast...
        __lastUpdateTime = time.time()
        
        try:
            f = urllib2.urlopen('http://api.wunderground.com/api/WUNDERGROUND_API_KEY/conditions/q/CO/Boulder.json', timeout=1)
        except (urllib2.URLError, socket.timeout) as e:
            print "Problem reading Wunderground URL:", type(e)
            return
            
        json_string = f.read()
    
        try:
            the_json = json.loads(json_string)
            
            obsTime = datetime.fromtimestamp( \
                rfc822.mktime_tz( \
                rfc822.parsedate_tz( the_json['current_observation']['observation_time_rfc822'])))
                
            obsTemp = float(the_json['current_observation']['temp_c'] )
        except (KeyError, ValueError, TypeError) as e:
            print "Got something from Wunderground but it didn't make sense.", type(e)
            return
            
        # This may not be a new data point; the DB requires unique timestamps.
        # Only create a new point if the last point in __history is old, or __history is empty.
        if len(__history) > 0 and obsTime > __history[-1].time or len(__history) == 0:
            newPoint = models.WeatherData(time=obsTime, extTemp = obsTemp)
            __history.append(newPoint)
            
            # Shouldn't be trouble, but be careful not to break things anyway.  
            try:
                db.session.add(newPoint)
                db.session.commit()
            except:
                print sys.exc_info()
                db.session.rollback()
            
            # __history shouldn't be longer than __EXTRAPOLATE_HISTORY_N
            while len(__history) > __EXTRAPOLATE_HISTORY_N:
                __history.popleft()
    else:
        pass
        
def getTempC():
    """
    Returns external temperature information for the controller.
    Call as often as you like; this handles rate-throttling for wunderground.
    Handles writing history into the database.
    Also extrapolates external temperature for up to 15 minutes past the last read.
    If *absolutely no* data can be provided (first time run ever and wunderground is down), 
    returns None.
    """
    global __history
    global __EXTRAPOLATE_TIME_LIMIT_S
    
    update_weather()
    
    if len(__history) == 0:
        # you're on your own buddy
        return None;
    elif len(__history) == 2:
        # quick and dirty linear extrapolation between last two points.
        # TODO: Generalize this with an Nth-order fit and polynomial regression.
        slope = (__history[1].extTemp - __history[0].extTemp) / ((__history[1].time - __history[0].time).total_seconds())
        dt = (datetime.now() - __history[1].time).total_seconds()
        dt = min(dt, __EXTRAPOLATE_TIME_LIMIT_S)
        est_temp = __history[1].extTemp + slope * dt;
        return est_temp;
    else:
        # history is the wrong length, for some reason.  Use last point's data.
        return __history[-1].extTemp
