
import yaml
import socket
class Configuration():
	"""Loads the config from the config.yaml"""

	def __init__(self, configfilename):
		"""Loads the configuration from the given file"""
		filecontent = open(configfilename, "r")
		self.config=yaml.safe_load(filecontent)
		self.piname = socket.gethostname()
		self.greyimageResolutionWidth = self.config["greyimageResolutionWidth"]
		self.greyimageResolutionHeight = self.config["greyimageResolutionHeight"]
		self.mainResolutionHeight = self.config["mainResolutionHeight"]
		self.mainResolutionWidth = self.config["mainResolutionWidth"]
		self.mainStreamColorFormat = self.config["mainStreamColorFormat"]
		self.rawImageInterval = self.config["rawImageInterval"]
		self.videoOutputDirectory = self.config["videoOutputDirectory"].replace("<<hostname>>", self.piname)
		self.rawImageQutputDirectory = self.config["rawImageQutputDirectory"].replace("<<hostname>>", self.piname)
		self.pickleOutputDirectory = self.config["pickleOutputDirectory"]
		self.maskQueueActivityThreshold = self.config["maskQueueActivityThreshold"]
		self.cluster_epsilon = self.config["cluster_epsilon"]
		self.cluster_min_samples = self.config["cluster_min_samples"]
		self.diff_threshold = self.config["diff_threshold"]
		self.maskQueueMaxFrames = self.config["maskQueueMaxFrames"]
		self.maskQueueMaskColor = self.config["maskQueueMaskColor"]
		self.shiTomashiMaxCorners = self.config["shiTomashiMaxCorners"]
		self.shiTomashiqualityLevel = self.config["shiTomashiqualityLevel"]
		self.shiTomashiMinDistance = self.config["shiTomashiMinDistance"]
		self.shiTomashiBlockSize = self.config["shiTomashiBlockSize"]
		self.lucasCanadeWinSize = self.config["lucasCanadeWinSize"]
		self.lucasCanadeMaxLevel = self.config["lucasCanadeMaxLevel"]
		self.piname = socket.gethostname()
		self.server_raw_folder= self.config["server_raw_folder"]
		self.server_video_folder=self.config["server_video_folder"]
		self.mqtt_ip = self.config["mqtt_ip"]
		self.mqtt_port=self.config["mqtt_port"]
		self.mqtt_keepalive=self.config["mqtt_keepalive"]
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

