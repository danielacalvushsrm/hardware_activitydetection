# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
from threading import Thread
from picamera2.encoders import H264Encoder, Quality
import cv2
import time
import numpy as np
import cv2
import os
import logging

from datetime import datetime
from picamera2.outputs import FileOutput

from picamera2 import Picamera2

class PicameraStream:
    """Camera object that controls video streaming from the Picamera"""
    
    resolution=None
    
    def __init__(self,lores_resolution,resolution, mainStreamFormat, videoOutputDirectory, piname):
        # Initialize the PiCamera and the camera image stream
        self.picam2=Picamera2()
        self.config = self.picam2.create_preview_configuration(lores={"size": lores_resolution}, main={"size": resolution, "format": mainStreamFormat},
        raw=self.picam2.sensor_modes[3], buffer_count=2)
        logger=logging.getLogger("picamera2")
        logger.setLevel(logging.INFO)
        self.picam2.configure(self.config)
        self.encoder = H264Encoder(bitrate=10000000)
      #  self.picam2.encoder = self.encoder
        self.stopped = True
        self.wakeup()
        
        self.loress1=self.picam2.stream_configuration("lores")["stride"]
        self.loresw1, self.loresh1= self.picam2.stream_configuration("lores")["size"]
        
        self.s1=self.picam2.stream_configuration("main")["stride"]
        self.w1, self.h1= self.picam2.stream_configuration("main")["size"]

        self.loresresolution=lores_resolution
        self.maxValueDiff_lores=self.loresw1*self.loresh1*255
        self.resolution = resolution

        self.out_directory=videoOutputDirectory
        self.piname=piname
        #filename of the current generated file
        self.currentFilename=None
	# Variable to control when the camera is currently recording
        self.isRecording = False
        
    def getLoresResolution(self):
        return self.resolution
        
    def getLoresStride(self):
        return self.loress1
        
    def getLoresHeight(self):
        return self.loresh1
        
    def getLoresWidth(self):
        return self.loresw1

    def getResolution(self):
        return self.resolution
        
    def getStride(self):
        return self.s1
        
    def getHeight(self):
        return self.h1
        
    def getWidth(self):
        return self.w1
        
    def getCurrentFilename(self):
        return self.currentFilename
        
    def generateFilename(self):
        """generates the filename for the image, based on timestamp"""
        timestamp = datetime.now()
        filename=self.piname+"__"+timestamp.strftime("%d-%m-%Y_%H-%M-%S--%f")
        return filename

    def startVideo(self):
        self.isRecording=True
        #if the outdirectory does not exist, create it
        if not os.path.exists(self.out_directory):
            os.makedirs(self.out_directory)
        self.currentFilename=self.generateFilename()
        self.picam2.output = FileOutput(self.out_directory+"/"+self.currentFilename+".h264")
        self.picam2.start_encoder(self.encoder, self.picam2.output)

    def stopVideo(self):
        self.isRecording=False
        self.picam2.stop_encoder()
        self.currentFilename= None
            
    def read(self):
        """Return the most recent frame in max resolution"""
        return self.picam2.capture_buffer("main")
        
    def readraw(self):
        """returns the last gathered raw"""
        return self.picam2.capture_buffer("raw")

    def readlores(self):
        """Returns the most recent frame in low resolution"""
        return self.picam2.capture_buffer("lores")
        
    def sleep(self):
        if not self.stopped:
            self.stopped= True
            self.picam2.stop()
        
    def wakeup(self):
        if self.stopped:
           self.stopped = False
           self.picam2.start()
