import socket
import yaml
class Configuration():
	"""Loads the config from the config.yaml"""

	def __init__(self, configfilename):
		"""Loads the configuration from the given file"""
		filecontent = open(configfilename, "r")
		
		self.config=yaml.safe_load(filecontent)
		self.piname = socket.gethostname()
		self.mqtt_ip = self.config["mqtt_ip"]
		self.mqtt_port=self.config["mqtt_port"]
		self.mqtt_keepalive=self.config["mqtt_keepalive"]
		self.updateInterval=self.config["updateInterval"]

	def configuration(self):
		"""returns the full configuration as dict"""
		return self.config

