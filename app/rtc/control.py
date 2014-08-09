import pywapi
import pprint
import rfc822
from datetime import datetime

result = pywapi.get_weather_from_noaa('KBDU')

location = result['location']
dt		 =  datetime.fromtimestamp(rfc822.mktime_tz(rfc822.parsedate_tz(result['observation_time_rfc822'])))
temp_c	 = float(result['temp_c'])

print 'location: \t', location
print 'datetime: \t', str(dt)
print 'temp (c): ', temp_c
