import os
import numpy as np
import cv2
from datetime import datetime
import time
import os
from threading import Thread
class CompressedRawOutput():

    def __init__(self, out_directory, piname):
        self.out_directory = out_directory   
        self.piname=piname
        if not os.path.exists(self.out_directory):
            os.makedirs(self.out_directory)


    def __saveAsThread(self, f, newfolder, filename, noOfFrame, now):
        "save the image to the storage and if newfolder is true, make a subfolder for the image"
        fname = self.generateFilename(filename, noOfFrame, now)
        if newfolder:
                self.sub_directory =os.path.join(self.out_directory,fname)
                if not os.path.exists(self.sub_directory):
                    os.makedirs(self.sub_directory)
        np.save(os.path.join(self.sub_directory,fname),f)
        
    def save(self, f, newfolder, filename, noOfFrame, now):
        thread = Thread(target=self.__saveAsThread, args=(f,newfolder, filename, noOfFrame, now))
        thread.start()

    def generateFilename(self, filename, noOfFrame, now):
        """generates the filename for the image, based on timestamp"""
        newname=str(now)+"___"+filename+"___"+str(noOfFrame)
        return newname


