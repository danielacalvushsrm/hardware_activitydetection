
import cv2
import numpy as np


class MaskQueue:
    """A Class to store mask frames with activity in a queue """
    

    def __init__(self, framesInQueue=20, activityThresold=500, maskColor=[0,255,0]):
        """Initialises an empty Maskqueue. With no of Frames in queue and the activitiythresold"""
        #aggregarted is the variable, which includes all masks which are currently in the queue
        self.aggregatedMask = None
        self.framesInQueue = framesInQueue
        self.activityThreshold=activityThresold
        self.previousActivity=0
        self.relativeActivity=0
        self.maskColor=maskColor
        self.queue=[]
        
        self.lastGrey = None
        self.lastDiff = None

    
    def addMask(self, mask):
        """Adds a mask to the queue. If queue full the oldest will be removed"""
        #convert them all to uint8 for compatiblity
        mask = mask.astype(np.uint8)
        #reset mask and push prev mask to the queue - substract from current Mask the poped one and add the new to the mask
        if len(self.queue) == self.framesInQueue:
            removedMask=self.queue.pop(0)
            self.aggregatedMask = cv2.subtract(self.aggregatedMask, removedMask)
        self.queue.append(mask.copy())
    
        if self.aggregatedMask is not None:
            self.aggregatedMask = cv2.add(self.aggregatedMask,mask)
        else:
            self.aggregatedMask=mask
        self.updateActivity()
        return np.zeros_like(mask)
    
    def getAggregatedMask(self):
        return self.aggregatedMask
    
    def updateActivity(self):
        self.previousActivity =self.relativeActivity
    
        noOfgreenPixel=np.sum(np.all(self.aggregatedMask == self.maskColor, axis=2))
        if(len(self.queue) >0):
            self.relativeActivity=noOfgreenPixel /len(self.queue)
        else:
            self.relativeActivity=0

    def hasActivity(self):
        """returns true if there is activity in the current queue"""
        return self.relativeActivity > self.activityThreshold
    
    def getActivityLevel(self):
        return self.relativeActivity

    def hadActivity(self):
        return self.previousActivity > self.activityThreshold
        
    def getPrevGrey(self):
        """Returns the last saved grey image, (frame) form the queue (which is the newest)"""
        return self.lastGrey
        
    def setPrevGrey(self, grey):
        self.lastGrey = grey
        
    def getPrevDiff(self):
        """Returns the last saved difference image, (frame) form the queue (which is the newest)"""
        return self.lastDiff
        
    def setPrevDiff(self, diff):
        self.lastDiff = diff
