import math
import cv2 as cv
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from numpy import linalg as LA

class CROP_SIDE(Enum):
    LEFT=1
    RIGHT=2
    TOP=3
    BOTTOM=4

class CAM_SOURCE(Enum):
    DRONE00=1
    DRONE01=2
    DRONE02=3
    DRONE10=4
    DRONEE1=5
    DRONE12=6
    DRONE20=7
    DRONE21=8
    DRONE22=9
    DRONE30=10
    DRONE31=11
    DRONE32=12

def getEnum(source):
    if source == "drone-0-0":
        return CAM_SOURCE.DRONE00
    elif source == "drone-0-1":
        return CAM_SOURCE.DRONE01
    elif source == "drone-0-2":
        return CAM_SOURCE.DRONE02
    elif source == "drone-1-0":
        return CAM_SOURCE.DRONE10
    elif source == "drone-E-1":
        return CAM_SOURCE.DRONEE1
    elif source == "drone-1-2":
        return CAM_SOURCE.DRONE12
    elif source == "drone-2-0":
        return CAM_SOURCE.DRONE20
    elif source == "drone-2-1":
        return CAM_SOURCE.DRONE21
    elif source == "drone-2-2":
        return CAM_SOURCE.DRONE22
    elif source == "drone-3-0":
        return CAM_SOURCE.DRONE30
    elif source == "drone-3-1":
        return CAM_SOURCE.DRONE31
    elif source == "drone-3-2":
        return CAM_SOURCE.DRONE32
    
def getNameOfEnume(source):
    if source ==CAM_SOURCE.DRONE00:
        return "drone-0-0"
    elif source ==CAM_SOURCE.DRONE01:
        return "drone-0-1" 
    elif source ==  CAM_SOURCE.DRONE02:
        return "drone-0-2"
    elif source == CAM_SOURCE.DRONE10:
        return "drone-1-0"
    elif source == CAM_SOURCE.DRONEE1:
        return "drone-E-1"
    elif source ==CAM_SOURCE.DRONE12:
        return "drone-1-2"
    elif source ==  CAM_SOURCE.DRONE20:
        return "drone-2-0"
    elif source ==  CAM_SOURCE.DRONE21:
        return "drone-2-1"
    elif source ==  CAM_SOURCE.DRONE22:
        return "drone-2-2"
    elif source ==  CAM_SOURCE.DRONE30:
        return "drone-3-0"
    elif source ==  CAM_SOURCE.DRONE31:
        return "drone-3-1"
    elif source ==  CAM_SOURCE.DRONE32:
        return "drone-3-2"
    
def getRotationOrder(source, target):
    "returns the amount of rotation for the images depending on the position in the gigaImage"
    if (source==CAM_SOURCE.DRONE10 and target == CAM_SOURCE.DRONE00) or (source==CAM_SOURCE.DRONE12 and target == CAM_SOURCE.DRONE02) or(source==CAM_SOURCE.DRONE22 and target == CAM_SOURCE.DRONE12) or (source==CAM_SOURCE.DRONE21 and target == CAM_SOURCE.DRONEE1) or (source==CAM_SOURCE.DRONE20 and target == CAM_SOURCE.DRONE10):
        return None
    if (source==CAM_SOURCE.DRONE22 and target == CAM_SOURCE.DRONE32)or(source==CAM_SOURCE.DRONE21 and target == CAM_SOURCE.DRONE31) or (source==CAM_SOURCE.DRONE20 and target == CAM_SOURCE.DRONE30):
        return cv.ROTATE_180
    if(source ==CAM_SOURCE.DRONEE1 and target ==CAM_SOURCE.DRONE10) or (source ==CAM_SOURCE.DRONE21 and target ==CAM_SOURCE.DRONE20) or (source ==CAM_SOURCE.DRONE31 and target ==CAM_SOURCE.DRONE30):
        return cv.ROTATE_90_CLOCKWISE
    if (source ==CAM_SOURCE.DRONE21 and target ==CAM_SOURCE.DRONE22) or(source ==CAM_SOURCE.DRONE31 and target ==CAM_SOURCE.DRONE32) or (source ==CAM_SOURCE.DRONEE1 and target ==CAM_SOURCE.DRONE12):
        return cv.ROTATE_90_COUNTERCLOCKWISE
    else:
        raise NotImplementedError("This pair is not yet implemented")


   #assume the following order: 21 31, 30

def getRotationOrder_stitch(source, target):
    if (source==CAM_SOURCE.DRONE21 and target == CAM_SOURCE.DRONE31):
        return cv.ROTATE_180
    if (source == CAM_SOURCE.DRONE31 and target == CAM_SOURCE.DRONE30):
        return cv.ROTATE_90_CLOCKWISE
    else:
        print(source, target)
        raise NotImplementedError()

def getBlackNPImage(width, height):
    """returns a black image in the shape width x height"""
    return np.zeros((height, width, 3), dtype = np.uint8)

def inverseRotationOrder(rotationOrder):
    "to rotate back the images, we need the counterpart of the 90° rotations"
    if rotationOrder == cv.ROTATE_90_CLOCKWISE:
        return cv.ROTATE_90_COUNTERCLOCKWISE
    elif rotationOrder == cv.ROTATE_90_COUNTERCLOCKWISE:
        return cv.ROTATE_90_CLOCKWISE
    else:
        return rotationOrder

def crop(img1, side, rotation,margin=500):
    "rotates the image for rotation angle clockwise and then crops the image"
    if rotation is not None:
        img1=cv.rotate(img1, rotation)
    if side == CROP_SIDE.RIGHT:
        return img1[0:img1.shape[0], img1.shape[1]-margin:img1.shape[1]] 

    if side== CROP_SIDE.LEFT:
        return img1[0:img1.shape[0], 0: margin]

    if side == CROP_SIDE.BOTTOM:
        raise NotImplementedError("Bottom is not yet implemented") 
    if side == CROP_SIDE.TOP:
        raise NotImplementedError("Top is not yet implemented") 

def GetNewFrameSizeAndMatrix(HomographyMatrix, Sec_ImageShape, Base_ImageShape):
    (Height, Width) = Sec_ImageShape
    
    # Taking the matrix of initial coordinates of the corners of the secondary image
    # Stored in the following format: [[x1, x2, x3, x4], [y1, y2, y3, y4], [1, 1, 1, 1]]
    # Where (xi, yi) is the coordinate of the i th corner of the image. 
    InitialMatrix = np.array([[0, Width - 1, Width - 1, 0],
                              [0, 0, Height - 1, Height - 1],
                              [1, 1, 1, 1]])
    
    FinalMatrix = np.dot(HomographyMatrix, InitialMatrix)
    [x, y, c] = FinalMatrix
    x = np.divide(x, c)
    y = np.divide(y, c)

    # Finding the dimensions of the stitched image frame and the "Correction" factor
    min_x, max_x = int(round(min(x))), int(round(max(x)))
    min_y, max_y = int(round(min(y))), int(round(max(y)))
    New_Width = max_x
    New_Height = max_y
    Correction = [0, 0]
    if min_x < 0:
        New_Width -= min_x
        Correction[0] = abs(min_x)
    if min_y < 0:
        New_Height -= min_y
        Correction[1] = abs(min_y)
    
    # Again correcting New_Width and New_Height
    if New_Width < Base_ImageShape[1] + Correction[0]:
        New_Width = Base_ImageShape[1] + Correction[0]
    if New_Height < Base_ImageShape[0] + Correction[1]:
        New_Height = Base_ImageShape[0] + Correction[1]

    # Finding the coordinates of the corners of the image if they all were within the frame.
    x = np.add(x, Correction[0])
    y = np.add(y, Correction[1])
    OldInitialPoints = np.float32([[0, 0],
                                   [Width - 1, 0],
                                   [Width - 1, Height - 1],
                                   [0, Height - 1]])
    NewFinalPonts = np.float32(np.array([x, y]).transpose())

    # Updating the homography matrix. 
    HomographyMatrix = cv.getPerspectiveTransform(OldInitialPoints, NewFinalPonts)
    
    return [New_Height, New_Width], [min_y, min_x], HomographyMatrix

def readImages(csource, ctarget):
    img1base = cv.imread('./testimages/25-04-2023_20-30-00_'+getNameOfEnume(csource)+'.jpg') # trainImage left
    img2base = cv.imread('./testimages/25-04-2023_20-30-00_'+getNameOfEnume(ctarget)+'.jpg') # queryImage right
    return img1base, img2base

def FilterByAngle(good, kp1, kp2, tolerance, margin):
    print("Executing filter by angle... ", end=" ")
    goodcopy = np.copy(good)
    itemstodel=[]
    angles=[]
    for i in range(len(good)):
        currentobj0 = kp1[good[i].queryIdx].pt[0]
        currentobj1=kp1[good[i].queryIdx].pt[1]
        currentscene0 = kp2[good[i].trainIdx].pt[0]+margin
        currentscene1= kp2[good[i].trainIdx].pt[1]
        rise=(currentobj1-currentscene1)/(currentobj0-currentscene0)
        angle=math.atan(rise)*180/math.pi
        angles.append(angle)
    if len(angles)>0:
        avg = sum(angles)/len(angles)
        print("Average of angles is: "+str(avg))
        avgPlusTolerance = avg+tolerance
        avgMinusTolerance = avg-tolerance
        print("Angles to delete: ")
        for i in range(len(good)):
            if angles[i] < avgMinusTolerance or angles[i] > avgPlusTolerance:
                #angle lies not in Tolerance
                itemstodel.append(i)
                print(angles[i], end=" ")
    goodcopy=np.delete(goodcopy, itemstodel)
    return goodcopy

def Filter(good, kp1, kp2, maxDistance, minDistance, angleTolerance, margin, filterbyDistance, filterbyAngle):
    goodCopy= np.copy(good)
    
    if filterbyDistance:
        goodCopy=FilterByDistance(goodCopy, kp1, kp2, maxDistance, minDistance, margin)
        
        print("No of matches after lengthfilter: "+str(len(goodCopy)))
    if filterbyAngle:
        goodCopy =FilterByAngle(good, kp1, kp2, angleTolerance, margin)
        print("No of matches after anglefilter: "+str(len(goodCopy)))
    obj = np.empty((len(goodCopy),2), dtype=np.float32)
    scene = np.empty((len(goodCopy),2), dtype=np.float32)
    for i in range(len(goodCopy)):
        obj[i,0] = kp1[good[i].queryIdx].pt[0]
        obj[i,1] = kp1[good[i].queryIdx].pt[1]
        scene[i,0] = kp2[good[i].trainIdx].pt[0]
        scene[i,1] = kp2[good[i].trainIdx].pt[1]
    return scene, obj, goodCopy

def FilterByDistance(good, kp1, kp2, maxDistance, minDistance, margin):
    print("Executing filter by distance... ", end=" ")
    goodcopy = np.copy(good)
    itemstodel=[]
    for i in range(len(good)):
        currentobj0 = kp1[good[i].queryIdx].pt[0]
        currentobj1=kp1[good[i].queryIdx].pt[1]
        currentscene0 = kp2[good[i].trainIdx].pt[0]+margin
        currentscene1= kp2[good[i].trainIdx].pt[1]
        distance = math.sqrt(math.pow(currentscene0-currentobj0,2)+math.pow(currentscene1-currentobj1,2))
        if distance > maxDistance or distance < minDistance:
            itemstodel.append(i)
    goodcopy=np.delete(goodcopy, itemstodel)

    print("remaining "+str(len(goodcopy)))
    return goodcopy

def onlyMatches(matches):
    good = []
    for m,n in matches:
        good.append(m)
    return good

def ratioTest(matches, percent=0.65):
    print("Executing ratio Test... ", end=" ")
    good = []
    for m,n in matches:
        if m.distance < percent*n.distance:
            good.append(m)
    while len(good)<= 4 and percent <1:
        percent = percent+0.1
        good = []
        for m,n in matches:
            if m.distance < percent*n.distance:
                good.append(m)

    print("remaining: "+str(len(good)))
    return good

def findMatches(des1, des2):
    print("Exceuting KNN Match ....", end=" ")
    bf = cv.BFMatcher()
    matches = bf.knnMatch(des1,des2,k=2)
    print("resulted in: "+str(len(matches)))
    return matches

def findKeypoints(gray1, gray2):
    print("find Keypoints via SIFT...", end=" ")
    sift = cv.SIFT_create()
    #is there a confidence (gesamtsumme der Gewichte muss1 sein(normiert über alle))
    kp1, des1 = sift.detectAndCompute(gray1,None)
    kp2, des2 = sift.detectAndCompute(gray2,None)
    print("... done")
    return (kp1, des1, kp2, des2)

def getMarginIfNeeded(csource, ctarget, source, target):
    "adds a margin on the right/left or both if needed for stitching"
    print("in get Margin if needed for "+getNameOfEnume(csource)+ " "+getNameOfEnume(ctarget))
    if csource == CAM_SOURCE.DRONE21 and ctarget == CAM_SOURCE.DRONE20 or csource == CAM_SOURCE.DRONE31 and ctarget == CAM_SOURCE.DRONE30:# or ctarget == CAM_SOURCE.DRONE22):
        print("source - target", (source.shape[1]-target.shape[1]))
        black=getBlackNPImage(int(source.shape[1]-target.shape[1]),target.shape[0] )
        print("target: ", target.shape)
        print("black", black.shape)
        target= np.concatenate( (black, target ), axis=1).astype('uint8')
        print("new target" ,target.shape)
    return target

def prepareImages(im_l, im_r, shift, direction="horizontal"):
    """Adds black parts to have an image which is wide enough to match both images
        The shift informs how the right image must be moved to left and top/bottom
    """
    #add black parts left and right
    if direction== "horizontal":
        # due to the shift the black area should not be the complete width but the width - shift

        #determine the size of the final image, add black parts on the left and right side to gain same size
        fullsize_x=im_r.shape[1]+im_l.shape[1]-shift[0]
        
        print("Fullsize x  "+str(im_r.shape[1])+" + "+str(im_l.shape[1])+" - "+str(shift[0])+" = "+str(fullsize_x))
        
        black_r_x = np.zeros((im_r.shape[0], fullsize_x-im_r.shape[1], 3), dtype = np.uint8)
        print("black r must be: (",fullsize_x-im_l.shape[1],",",im_l.shape[0], ") = ",black_r_x.shape)
        print("Old shape of im_r: ",im_r.shape)
        im_r_new = cv.hconcat([black_r_x, im_r.astype('uint8')])
        print("New Shape of im_r "+str(im_r_new.shape))

        black_l_x = np.zeros((im_l.shape[0], fullsize_x-im_l.shape[1], 3), dtype = np.uint8)
        print("black im_l must be: ",black_l_x.shape)
        im_l_new = cv.hconcat([im_l.astype('uint8'), black_l_x])
        print("Shape of im_l "+str(im_l_new.shape))
    
        #as final step. Check if one image is larger in y direction than the other. Add black lines to match the same y size
        noOflines = abs(im_l.shape[0]-im_r.shape[0])
        
        black_y = np.zeros((noOflines, im_l_new.shape[1], 3), dtype=np.uint8)
        print(black_y.shape)
        print(noOflines, " lines must be added  to", end=" ")
        if im_l.shape[0] > im_r.shape[0]:
            #im_l is larger so add some lines to imr
            im_r_new = cv.vconcat([im_r_new, black_y])
            print("im r ", im_r_new.shape)
        else:
            im_l_new = cv.vconcat([im_l_new, black_y])
            print("im l ", im_l_new.shape)
    else:
        raise NotImplementedError("other directions than horizontal is not implemented")

    return (im_l_new, im_r_new)

def prepareMasks(im_l, im_r, old_im_l, old_im_r, shift):
    """Creates masks according to the images and the shift (where the image was shifted, the two masks overlap)"""
   # s1_white = (im_l.shape[0], old_im_r.shape[1])
   # print(s1_white)
    fullsize=old_im_r.shape[1]+old_im_l.shape[1]-shift[0]
    print(fullsize)
    black_r = np.zeros((old_im_r.shape[0], fullsize-old_im_l.shape[1]), dtype = np.uint8)
    print(black_r.shape)
   # s2_white = (im_l.shape[0], int(im_l.shape[1]/2))
    black_l = np.zeros((old_im_l.shape[0], fullsize-old_im_r.shape[1]), dtype = np.uint8)
    #alles was weiß ist wird eingezeichnet
    ones_l=np.ones((old_im_l.shape[0],old_im_l.shape[1]) )
    ones_r =np.ones((old_im_r.shape[0], old_im_r.shape[1]))
    im_l_mask =np.concatenate( (ones_l*255,black_r ), axis=1).astype('uint8')
    im_r_mask =np.concatenate( (black_l, ones_r*255), axis=1).astype('uint8')
    return im_l_mask, im_r_mask


