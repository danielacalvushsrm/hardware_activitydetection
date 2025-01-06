
import cv2
import math
import numpy as np
class Converter():
    """Can convert an raw image to grey image and is able to generate a mask image from two succeeding images"""

    def __init__(self, config):
        
        # Variable for color to draw optical flow track
        self.track_color=config.maskQueueMaskColor

        # Parameters for Shi-Tomasi corner detection
        self.feature_params = dict(maxCorners = config.shiTomashiMaxCorners, qualityLevel = config.shiTomashiqualityLevel, minDistance = config.shiTomashiMinDistance, blockSize = config.shiTomashiBlockSize)
        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict(winSize = (config.lucasCanadeWinSize,config.lucasCanadeWinSize), maxLevel = config.lucasCanadeMaxLevel, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def convertToGrey(self, frame, s1, h1, w1):
        """takes a onedimensional frame and converts it into grey image for feature tracking"""
        # reshape
        # for yuv no ,3 at reshape if rgb .reshape((self.h1, self.w1,3))
        image = frame[:s1*h1].reshape((h1, w1))
        return cv2.cvtColor(image, cv2.COLOR_YUV2GRAY_I420)        

    def generateMask(self, current, activities):
        """generates a mask with the activity"""
        x =np.arange(current.shape[0]*current.shape[1]*3)
        x = x.reshape((current.shape[0],current.shape[1],3))
        mask = np.zeros_like(x)
        mask = mask.astype(np.uint8)
        for centerpoint in activities:
                mask=cv2.circle(mask.astype(np.uint8), (int(centerpoint[0]),int(centerpoint[1])),1, self.track_color, -1)
        return mask
        

    def findActivity(self, current, prev):
        """checks if there is activity based on feature tracking"""
        features_prev = cv2.goodFeaturesToTrack(prev, mask = None, **self.feature_params)            
        activities = []
        if prev is not None and current is not None and features_prev is not None:
            features_next, status, error = cv2.calcOpticalFlowPyrLK(prev.astype(np.uint8), current.astype(np.uint8), features_prev.astype(np.float32), None, **self.lk_params)           
                    
            # Selects good feature points for previous position
            good_old = features_prev[status == 1].astype(int)
            # Selects good feature points for next position
            good_new = features_next[status == 1].astype(int)

            for i, (new, old) in enumerate(zip(good_new, good_old)):
                    # Returns a contiguous flattened array as (x, y) coordinates for new point
                    a, b = new.ravel()
                    # Returns a contiguous flattened array as (x, y) coordinates for old point
                    c, d = old.ravel()

                    if math.fabs((a-c)) > 1 and math.fabs(b-d) >1:
                        activities.append([(a+c)/2,(b+d)/2])
        return activities

