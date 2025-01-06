from homography_helper import *
import numpy as np
import cv2 as cv
class HomographyTree:
    """Represents the graph determine the neighbours of the cameras"""

    def __init__(self, camera, image, gridposition, followers=None):
        self.tree_followers = followers
        self.next_x=None
        self.next_y=None
        self.camera = camera
        self.Hlist = None
        self.H = None
        self.way = None
        self.image = image
        self.warpedImage = self.image
        # [0] is correction in height 
        self.correction = [0,0]
        self.gigaImage = None
        self.mask = None
        self.gridposition= gridposition
    
    def set_next(self, next_x, next_y):
        self.next_x= next_x
        self.next_y = next_y
        
    def getAllSubNodes(self):
        nodelist = [self]
        if self.tree_followers is not None:
            for child in self.tree_followers:
                nodelist.extend(child.getAllSubNodes())
        return nodelist

    def getMaxWidthOfRow(self, currentmax):
        if self.next_y is None:
            return max(currentmax, self.warpedImage.shape[1])
        return self.next_y.getMaxWidthOfRow(max(currentmax,self.warpedImage.shape[1] ))

    def getMaxHeightOfCol(self, currentmax):
        if self.next_x is None:
            return max(currentmax, self.warpedImage.shape[0])
        return self.next_x.getMaxHeightOfCol(max(currentmax,self.warpedImage.shape[0] ))
    
    def setHomography(self, data,  way):
        "in way the last element is the current camera"
        way.append(self.camera)
        self.way = way.copy()

        self.setHomographyList(data, self.way)
        self.calculateHomography()
        if self.H is not None:
            NewFrameSize, Correction, HomographyMatrix = GetNewFrameSizeAndMatrix(self.H, self.image.shape[:2], self.image.shape[:2])
            print("Determined correction "+str(Correction)+ " for "+str(self.camera))
            self.correction = Correction
            self.H = HomographyMatrix
            self.warpedImage = cv.warpPerspective(self.image, self.H, (NewFrameSize[1], NewFrameSize[0]))
        else:
            self.warpedImage = self.image
            self.correction = [0,0]
        workingway = way.copy()
        if self.tree_followers is not None:
            for child in self.tree_followers:
                child.setHomography(data, workingway.copy())
                workingway = self.way
                
    def setHomographyList(self, data, way):
        "returns a list of homographies whoose needs to be applied to come to target"
        self.Hlist= []
        #gather the single Hs
        #append all Hs all the way long
        i=0
        j=1
        while(j < len(way)):
            csource = way[i]
            ctarget=way[j]
            self.Hlist.append(data[getNameOfEnume(csource)+"__"+getNameOfEnume(ctarget)])
            i=i+1
            j=j+1

    def calculateHomography(self):
        "go the list of homographies along and multiply them with dot"
        if len(self.Hlist) > 0:
            self.H= self.Hlist[0]
            for nexth in self.Hlist[1:]:
                self.H = np.dot(self.H, nexth)

    def generateFullImage(self, size):
        #care about the kids
        if self.tree_followers is not None:
            for child in self.tree_followers:
                child.generateGigaImage(size)
        #and myself
        #in first step generate black lines for offset x
        #tuple first height then width
        offset_height = np.zeros((0, size[1],3), dtype = np.uint8)
        #generate imageheight x offset y number of black lines
        offset_width = np.zeros((self.warpedImage.shape[0],0,3 ), dtype = np.uint8)
        #add image next to it
        imgwithOffset_width = cv.hconcat([offset_width, self.warpedImage])
        # add black cols on the right side
        fill_width_Colsize = size[1]-imgwithOffset_width.shape[1]
        fillypart=np.zeros((self.warpedImage.shape[0], fill_width_Colsize,3), dtype=np.uint8)
        imagepart = cv.hconcat([imgwithOffset_width, fillypart])
        #horizonally stich the 3 parts together to gigaimage
        upperpart = cv.vconcat([offset_height, imagepart])
        fillx = np.zeros((size[0]-upperpart.shape[0],size[1],3), dtype=np.uint8)

        self.gigaImage = cv.vconcat([upperpart, fillx])
        lower_black = np.array([1,1,1], dtype = "uint16")
        upper_black = np.array([255,255,2555], dtype = "uint16")
        self.mask = cv.inRange(self.gigaImage,lower_black,upper_black)
        self.mask = self.mask.astype(np.uint8)