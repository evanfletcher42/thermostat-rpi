import urllib2, json, socket
from datetime import datetime
import time, rfc822

from app import db, models
__MIN_UPDATE_PERIOD_SECONDS = 5*60
__lastUpdateTime = 0
__last_parsed_json = None
dataIsNew = True
def update_weather():

    global __last_parsed_json
    global __MIN_UPDATE_PERIOD_SECONDS
    global __lastUpdateTime
    
    json_bak = __last_parsed_json
    if time.time() - __lastUpdateTime > __MIN_UPDATE_PERIOD_SECONDS:
        try:
            __lastUpdateTime = time.time()
            f = urllib2.urlopen('http://api.wunderground.com/api/WUNDERGROUND_API_KEY/geolookup/conditions/q/CO/Boulder.json', timeout=1)
            json_string = f.read()
            __last_parsed_json = json.loads(json_string)
            justUpdated = True
        except (urllib2.URLError, socket.timeout, ValueError) as e:
            print type(e)
            __last_parsed_json = json_bak
        
        
def getTempC():
    global __last_parsed_json
    update_weather()
    if __last_parsed_json:
        return (rfc822.parsedate_tz(__last_parsed_json['current_observation']['observation_time_rfc822']), \
        float(__last_parsed_json['current_observation']['temp_c']) )
    else:
        return None