
import yaml
class Configuration():
	"""Loads the config from the config.yaml"""

	def __init__(self, configfilename):
		"""Loads the configuration from the given file"""
		filecontent = open(configfilename, "r")
		
		self.config=yaml.safe_load(filecontent)
		self.mqtt_ip = self.config["mqtt_ip"]
		self.mqtt_port=self.config["mqtt_port"]
		self.mqtt_keepalive=self.config["mqtt_keepalive"]
		self.db_host= self.config["db_host"]
		self.db_database= self.config["db_database"]
		self.db_user= self.config["db_user"]
		self.db_password= self.config["db_password"]

	def configuration(self):
		"""returns the full configuration as dict"""
		return self.config

