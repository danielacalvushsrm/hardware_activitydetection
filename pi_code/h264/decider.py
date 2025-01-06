from astral import LocationInfo
from astral.sun import sun
import datetime
from datetime import timedelta
from datetime import date
import zoneinfo
class Decider():
	"""Decides if its night or day. And calculates the time until change of day/night"""
	DAY=1
	NIGHT=2
	SUNRISE="sunrise"
	DUSK="dusk"
	def __init__(self, configuration):
		self.city = LocationInfo(configuration.decider_city, configuration.decider_country, configuration.decider_region, configuration.decider_longitute, configuration.decider_latitude)
		self.zoneinfo = zoneinfo.ZoneInfo(configuration.decider_region)
		self.date = None
		self.date_tomorrow = None
		self.s = None
		self.s_tomorrow= None
		self.margin_minutes=configuration.decider_margin_minutes
		self.updateSunInfo()

	def updateSunInfo(self):
		"""Updates the values when the day changes"""
		now = date.today()
		#if new day, gather the values
		if now != self.date:
			self.date =now
			self.s = sun(self.city.observer, date = self.date, tzinfo=self.zoneinfo)
		tomorrow = date.today()+ datetime.timedelta(days=1)
		if tomorrow != self.date_tomorrow:
			self.date_tomorrow = tomorrow
			self.s_tomorrow =sun(self.city.observer, date = self.date_tomorrow, tzinfo=self.zoneinfo)
		

	def dayOrNight(self):
		"""returns day or night depending on the values from astral"""
		self.updateSunInfo()
		now=datetime.datetime.now(self.zoneinfo)
		if now > (self.s[Decider.SUNRISE]-timedelta(minutes=self.margin_minutes)) and now < (self.s[Decider.DUSK]+timedelta(minutes =self.margin_minutes)):
			return Decider.DAY
		else:
			return Decider.NIGHT
	
			
	def timeTo(self, value):
		"""returns the time until it will be value (dusk or sunrise) again. Adding 1 Second to be sure that the time has passend after sleep"""
		self.updateSunInfo()
		now=datetime.datetime.now(self.zoneinfo)
		timeto= (self.s[value]+timedelta(minutes =self.margin_minutes)) - now
		if timeto < timedelta(minutes=0):
			#if dusk/sunrise was in the past, we need the value from the next day
			timetomorrow = (self.s_tomorrow[value]-timedelta(minutes=self.margin_minutes)) - now
			return timetomorrow.total_seconds()+1
		else:
			return timeto.total_seconds()+1
		
	def __str__(self):
		return 'Margin:    '+str(self.margin_minutes)+'Minutes\nDawn:    '+str(self.s["dawn"])+'\nSunrise: '+str(self.s["sunrise"])+'\nNoon:    '+str(self.s["noon"])+'\nSunset:  '+str(self.s["sunset"])+'\nDusk:    '+str(self.s["dusk"])
	
