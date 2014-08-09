import pywapi
import pprint
import rfc822

result = pywapi.get_weather_from_noaa('KBDU')

location = result[location]
dt 		 = rfc822.parsedate_tz(result['observation_time_rfc822'])
temp_c	 = float(result['temp_c'])

print 'location: \t', location
print 'datetime: \t', dt
print 'RFC822:   \t', dt.rfc822()
print 'temp (c): ', temp_c
