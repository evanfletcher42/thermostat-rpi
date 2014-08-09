import pywapi
import pprint

result = pywapi.get_weather_from_noaa('KBDU')

print 'location: ', result['location']
print 'temp (c): ', float(result['temp_c'])
