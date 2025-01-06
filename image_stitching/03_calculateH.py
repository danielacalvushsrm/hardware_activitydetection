import sys
import os.path
import csv
import cv2 as cv
import numpy as np
from homography_helper import CROP_SIDE, Filter, FilterByDistance, GetNewFrameSizeAndMatrix, crop, evaluateHomography, getEnum, getRotationOrder, readImages 
import pickle 
import matplotlib.pyplot as plt

from pickle_helper import *
persisted_files_folder="./persisted_files"
displayWarpedStepImg= False
displayWarpedImg= True

margin =500

def extractHomographies(cam_source, cam_target):
    """reads the homography from the file"""
    filename = "pairImages_"+cam_source+"_"+cam_target+".pickle"
    foundPairs=getFileContent(persisted_files_folder, filename)

    combinations = []
    for row in foundPairs:
        if len(row) ==10:
            H = row[4]
            noOfGoodPoints = int(row[2])
            stdOfGoodPoints = float(row[3])
            combinations.append([H, noOfGoodPoints, stdOfGoodPoints, row[4], row[5], row[6], row[7], row[8], row[9]])
    return combinations

def writeBestHomographie(cam_source, cam_target, H, kp1, kp2, matches):
    """Writes the best determined Homography into the file (overwrite if exists)"""
    filename = "bestH.pickle"
    data=getBESTContent(persisted_files_folder, filename)
    #set or replace H
    print("set or replace H")
    data[cam_source+"__"+cam_target]=(H, kp1, kp2, matches)
    writeBESTContent(persisted_files_folder, filename, data)

def addElementsToLists(good, kp1, kp2, goodlist, kp1list, kp2list):
    for match in good:
        #take the matching keypoints, 
        kp1point = kp1[match.queryIdx]
        kp2point = kp2[match.trainIdx]
        # add them to the lists, gather indices 
        kp1list.append(kp1point)
        kp1position=len(kp1list)-1
        kp2list.append(kp2point)
        kp2position=len(kp2list)-1
        #create a new Dmatch and add it to goodlist
        dmatch = cv.DMatch(kp1position, kp2position, match.distance)
        goodlist.append(dmatch)

    return goodlist, kp1list, kp2list

def determineBestH(hlist, img1base, img2base, cam_source, cam_target):
    #evaluate every h in list
    goodlist=[]
    kp1list=[]
    kp2list=[]
    csource=getEnum(cam_source)
    ctarget=getEnum(cam_target)
    rotation = getRotationOrder(csource, ctarget)
    img1base=cv.rotate(img1base, rotation)
    img2base=cv.rotate(img2base, rotation)

    print("no of homographies: "+str(len(hlist)))
    goodHomographies=0
    for elements in hlist:
        H=elements[0]
        goodHomographies=goodHomographies+1
        good = elements[4]
        kp1= elements[5]
        kp2 = elements[7]
        goodlist, kp1list, kp2list=addElementsToLists(good, kp1, kp2, goodlist, kp1list, kp2list)
        #sum up all kps and matches
    maxDistance, minDistance=300, 10
    scene, obj, goodlist =Filter(goodlist, kp1list, kp2list, maxDistance, minDistance, 5, margin, True, True)

    print("No of good Pairwise images: "+str(goodHomographies)+"/"+str(len(hlist)))

    H, _ = cv.findHomography(obj, scene, cv.RANSAC, 1)
    if H is not None:

        warpedImgBase = cv.warpPerspective(img2base, H, (img2base.shape[1],img2base.shape[0]))
        if displayWarpedImg:
            f,(ax1, ax2, ax3) = plt.subplots(1,3)
            ax1.imshow(img2base, cmap='gray')
            ax2.imshow(warpedImgBase, cmap='gray')
            img1 = crop(img1base,CROP_SIDE.RIGHT,None, margin) 
            gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
                
            blackimg1 =np.full((gray1.shape[0], gray1.shape[1], 3),255, dtype = np.uint8)
            blackimg2 =np.full((gray1.shape[0], gray1.shape[1], 3),255, dtype = np.uint8)
            img3black = cv.drawMatches(blackimg1,kp1list,blackimg2,kp2list,goodlist,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

            ax3.imshow(img3black, cmap='gray')    
            plt.show()   
    return H, kp1list, kp2list, len(kp1list), goodHomographies, len(hlist), goodlist

def processPair(cam_source, cam_target):
    print("Processing Pair: "+cam_source + " with "+cam_target)
    print("extract homographies")
    hlist=extractHomographies(cam_source, cam_target)
    print("read images")
    img1, img2 = readImages(getEnum(cam_source), getEnum(cam_target))

    print("determine best")
    best,kp1, kp2, noOfKeyPoints, noOfGoodHomographies, noOfHomographies, matches=determineBestH(hlist,img1, img2,cam_source, cam_target )
    if best is not None:
        writeBestHomographie(cam_source, cam_target, best, kp1, kp2, matches)
    else:
        print("No good Homography found :-(")
    return (noOfKeyPoints, noOfGoodHomographies, noOfHomographies, len(matches))

if __name__ == '__main__':
    if len(sys.argv) == 3:
        cam_source=sys.argv[1]
        cam_target=sys.argv[2]
        result=processPair(cam_source, cam_target)
        print("No of Keypoints: ",result[0])
        print("No of Matches: ", result[3])
        print("No of good Homographies: ", result[1], "/", result[2])
    else:
        listOfPairs=[("drone-2-1", "drone-2-0")]
        #... determine your own list
        
        resultlist=[]
        for pair in listOfPairs:
            cam_source = pair[0]
            cam_target = pair[1]

            resultlist.append(processPair(cam_source, cam_target))
            
            print("Processed Pair: "+cam_source + " with "+cam_target)
        for result in resultlist:
            print("No of Keypoints: ",result[0])
            print("No of Matches: ", result[3])
            print("No of good Homographies: ", result[1], "/", result[2])