import pickle
import random
import sys
import os.path
import csv
import cv2 as cv

from homography_helper import *
from rawToImgConverter import convertImage
from pickle_helper import *

displayInputImages = True
displayMatches=True
displayHomography=True
displayMasks=False
margin =500

persisted_files_folder="./persisted_files"
executedPairs_header =["filename_source", "filename_target", "h00", "h01", "h02", "h10", "h11", "h12", "h20", "h21", "h22"]


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

def printNoOfPairs(cam_source, cam_target):
    filename = "pairImages_"+cam_source+"_"+cam_target+".pickle"
    foundPairs=getFileContent(persisted_files_folder, filename)
    print("gefundene Bildpaare", len(foundPairs))


def findNextHomography(cam_source, cam_target, noOfFilesToProcess):
    "determines homographies for noOfFilesToProcess image pairs"
    filename = "pairImages_"+cam_source+"_"+cam_target+".pickle"
    csource = getEnum(cam_source)
    ctarget= getEnum(cam_target)
    foundPairs=getFileContent(persisted_files_folder, filename)
    print("found #image pairs: ", len(foundPairs))
    i =0
    noOfProcessedPairs=0
    while(noOfProcessedPairs < noOfFilesToProcess):
        i = random.randint(0, len(foundPairs)-1) # select an pair per random
        row = foundPairs[i]
        if len(row) == 2:
            sourcename =row[0].replace("/", "\\")
            targetname = row[1].replace("/", "\\")
            # then we have a pair and no matrix was generated yet
            try:
                source = convertImage(sourcename)
                target = convertImage(targetname)
                rotation= getRotationOrder(csource, ctarget)
                img1 = crop(source,CROP_SIDE.RIGHT, rotation, margin) 
                img2 = crop(target, CROP_SIDE.LEFT, rotation, margin)
                gray2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
                gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
                print("processed image pair with index: "+str(i))


                if displayInputImages:
                    f,(ax1, ax2) = plt.subplots(1,2)
                    ax1.imshow(source, cmap='gray')
                    ax2.imshow(target, cmap='gray')
                    plt.show()
                
                # 2. Step: find the keypoints and descriptors with SIFT
                kp1, des1, kp2, des2 = findKeypoints(gray1, gray2)

                # 3. Step: Find matches
                matches = findMatches(des1, des2)
                if displayMatches:
                    img3 = cv.drawMatches(img1,kp1,img2,kp2,onlyMatches(matches),None)
                    plt.imshow(img3)
                    plt.show()

                # 4. Step Apply ratio test to keep only the good matches
                good = ratioTest(matches)
                if displayMatches:
                    blackimg1 =np.full((gray1.shape[0], gray1.shape[1], 3),255, dtype = np.uint8)
                    blackimg2 =np.full((gray1.shape[0], gray1.shape[1], 3),255, dtype = np.uint8)

                    img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
                    img3black = cv.drawMatches(blackimg1,kp1,blackimg2,kp2,good,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
                    f,(ax1, ax2) = plt.subplots(1,2)
                    ax1.imshow(img3, cmap='gray')
                    ax2.imshow(img3black, cmap='gray')
                    plt.show()

                # 5. Step prepare and find homography
                maxDistance, minDistance=300, 10
                scene, obj, good =Filter(good, kp1, kp2, maxDistance, minDistance, 5, margin, True, False)

                if displayMatches:
                    blackimg1 =np.full((gray1.shape[0], gray1.shape[1], 3),255, dtype = np.uint8)
                    blackimg2 =np.full((gray1.shape[0], gray1.shape[1], 3),255, dtype = np.uint8)

                    img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
                    img3black = cv.drawMatches(blackimg1,kp1,blackimg2,kp2,good,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
                    f,(ax1, ax2) = plt.subplots(1,2)
                    ax1.imshow(img3, cmap='gray')
                    ax2.imshow(img3black, cmap='gray')
                    plt.show()

                scene, obj, good =Filter(good, kp1, kp2, maxDistance, minDistance, 5, margin, False, True)
                
                if displayMatches:
                    blackimg1 =np.full((gray1.shape[0], gray1.shape[1], 3),255, dtype = np.uint8)
                    blackimg2 =np.full((gray1.shape[0], gray1.shape[1], 3),255, dtype = np.uint8)

                    img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
                    img3black = cv.drawMatches(blackimg1,kp1,blackimg2,kp2,good,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
                    f,(ax1, ax2) = plt.subplots(1,2)
                    ax1.imshow(img3, cmap='gray')
                    ax2.imshow(img3black, cmap='gray')
                    plt.show()
            

                if len(good) > 3:
                    yvalues=[]
                    for match in good:
                        yvalues.append(kp1[match.queryIdx].pt[1])
                    yvalues=np.array(yvalues)
                    std=np.std(yvalues)

                    H, _ = cv.findHomography(obj, scene, cv.RANSAC, 1)
                    if displayHomography:
                        print(H)
                        #reduce save amount, only save keypoints which are relevant
                    good, kp1, kp2=addElementsToLists(good, kp1, kp2, [],[],[])
                    row.extend([len(good), std/(img1.shape[0]/2), H, good, kp1, des1, kp2, des2])
                else:
                    row.extend([len(good)])
                foundPairs[i]= row
                print(len(foundPairs[i]))
                noOfProcessedPairs=noOfProcessedPairs+1
            except:
                continue
        i=i+1

if __name__ == '__main__':
    print("Determine all Pairs")
    listOfPairs=[("drone-2-1", "drone-2-0")
              ]
        #... to be determined for own system
    for pair in listOfPairs:
        cam_source = pair[0]
        cam_target = pair[1]
        print("Process will be started with "+cam_source+ " to "+cam_target)
        n=1000
        #define how many imagepairs you would like to process
        findNextHomography(cam_source, cam_target, n)