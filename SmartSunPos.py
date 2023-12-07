# NTDEV - ID: 012
# VERSION: ALPHA 0.1
# This file is updated independently, it does not concern the global version of the controller.


# Imports
import math
import datetime

# Class
class SmartSunPos():
	def __init__(self, use_system_time: bool = True, man_time: tuple = (0, 0, 0, 0, 0, 0, 0), return_time: bool = True, location: tuple = None, timezone: int = None, refraction: bool = True):
		self._timezone = self.set_timezone(timezone)
		self._location = self.set_location(location)
		self._man_time = man_time
		if use_system_time:
			current_time = self.current_time()
		else:
			current_time = self.man_time
		self.data = self.get_data(current_time, self.location, refraction)
		self.sun_position = self.sunpos(current_time, self.location, refraction, return_time)

	@property
	def man_time(self):
		man_time = list(self._man_time)
		man_time[6] = self.timezone
		return tuple(man_time)
	
	@property
	def timezone(self):
		return self._timezone
	
	@property
	def location(self):
		return self._location

	def set_timezone(self, timezone):
		return 2 if timezone == None else timezone
	
	def set_location(self, location):
		return (52, 5) if location == None else location

	def get_data(self, current_time, location, refraction):
		return {'refraction':refraction, 'cucrrent_time':current_time, 'location':location, 'timezone':self.timezone}


	def current_time(self):
		curr_time = datetime.datetime.today().timetuple()
		year, mon, day, hr, mins, secs = curr_time.tm_year, curr_time.tm_mon, curr_time.tm_mday, curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec
		time_zone = self.timezone
		return (year, mon, day, hr, mins, secs, time_zone)

	
	def sunpos(self, when, location, refraction, return_time):
		def into_range(x, range_min, range_max):
			shiftedx = x - range_min
			delta = range_max - range_min
			return (((shiftedx % delta) + delta) % delta) + range_min
		
		# Extract the passed data
		year, month, day, hour, minute, second, timezone = when
		latitude, longitude = location

		# Math typing shortcuts
		rad, deg = math.radians, math.degrees
		sin, cos, tan = math.sin, math.cos, math.tan
		asin, atan2 = math.asin, math.atan2

		# Convert latitude and longitude to radians
		rlat = rad(latitude)
		rlon = rad(longitude)

		# Decimal hour of the day at Greenwich
		gmt = (
			hour - timezone
			+ minute / 60
			+ second / 3600
			)
		
		# Days from J2000, accurate from 1901 to 2099
		daynum = (
		367 * year
        - 7 * (year + (month + 9) // 12) // 4
        + 275 * month // 9
        + day
        - 730531.5
        + gmt / 24
    )
		# Mean longitude of the sun
		mean_long = (daynum * 0.01720279239 + 4.894967873)

		# Mean anomaly of the Sun
		mean_anom = (daynum * 0.01720197034 + 6.240040768)

		# Ecliptic longitude of the sun
		eclip_long = (
			mean_long
			+ 0.03342305518 * sin(mean_anom)
			+ 0.0003490658504 * sin(2 * mean_anom)
		)

		# Obliquity of the ecliptic
		obliquity = (0.4090877234 - 0.000000006981317008 * daynum)
		
		# Right ascension of the sun
		rasc = atan2(cos(obliquity) * sin(eclip_long), cos(eclip_long))
		
		# Declination of the sun
		decl = asin(sin(obliquity) * sin(eclip_long))

		# Local sidereal time
		sidereal = (4.894961213 + 6.300388099 * daynum + rlon)

		# Hour angle of the sun
		hour_ang = sidereal - rasc

		# Local elevation of the sun
		elevation = asin(sin(decl) * sin(rlat) + cos(decl) * cos(rlat) * cos(hour_ang))

		# Local azimuth of the sun
		azimuth = atan2(

        -cos(decl) * cos(rlat) * sin(hour_ang),

        sin(decl) - sin(rlat) * sin(elevation),

    	)

		# Convert azimuth and elevation to degrees
		azimuth = into_range(deg(azimuth), 0, 360)
		elevation = into_range(deg(elevation), -180, 180)

		# Refraction correction (optional)
		if refraction:
			targ = rad((elevation + (10.3 / (elevation + 5.11))))
			elevation += (1.02 / tan(targ)) / 60
		
		if return_time == True:
		# Return azimuth and elevation in degrees
			return (round(azimuth, 2), round(elevation, 2), when)
		else:
			return (round(azimuth, 2), round(elevation, 2))