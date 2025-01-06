
import yaml
import socket
class Configuration():
	"""Loads the config from the config.yaml"""

	def __init__(self, configfilename):
		"""Loads the configuration from the given file"""
		filecontent = open(configfilename, "r")
		self.config=yaml.safe_load(filecontent)
		self.piname = socket.gethostname()
		self.decider_margin_minutes=self.config["decider_margin_minutes"]
		self.decider_city=self.config["decider_city"]
		self.decider_country=self.config["decider_country"]
		self.decider_region=self.config["decider_region"]
		self.decider_longitute=self.config["decider_longitute"]
		self.decider_latitude=self.config["decider_latitude"]
		self.decider_send_to_NAS = self.config["decider_send_to_NAS"]
		
	def configuration(self):
		"""returns the full configuration as dict"""
		return self.config

