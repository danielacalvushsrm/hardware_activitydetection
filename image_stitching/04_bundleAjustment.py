import cv2 as cv
import numpy as np
import sys
from pickle_helper import *
from functools import reduce

persisted_files_folder="./persisted_files"

# creates a text file containing the values for the bundle Adjustment using ceres solver
# either with param: prepare to create the file or
# without param to read the solved solution and update the Homographies in the pickle file

# replace with own system
keyNumber = {"drone-2-1__drone-2-0": 0, 
             "drone-2-1__drone-3-1": 1, 
             "drone-2-1__drone-E-1": 2, 
             "drone-2-1__drone-2-2": 3, 
             "drone-3-1__drone-3-0": 4, 
             "drone-3-1__drone-3-2": 5, 
             "drone-2-0__drone-1-0": 6, 
             "drone-1-0__drone-0-0": 7, 
             "drone-2-2__drone-1-2": 8, 
             "drone-E-1__drone-1-2": 9, 
             "drone-E-1__drone-1-0": 10, 
             "drone-2-2__drone-3-2": 11, 
             "drone-1-2__drone-0-2": 12 }

def matchKeyToNumber(key):
    return keyNumber[key]
    
def matchNumberToKey(number):
    keys = [k for k, v in keyNumber.items() if v == number]
    #we know the number is also unique
    return keys[0]

def writeToPickle(cameralist):
    """Determines the key according to order in list and create a dict, write to pickle format"""
    i=0
    camdict={}
    for camset in cameralist:
        key = matchNumberToKey(i)
        print( key,i)
        print(camset)
        camdict[key]=camset
        i=i+1
    writeBESTHContent(persisted_files_folder, "bestH_ba.pickle", camdict)


def prepareCameras(content):
    """Set all values form the Homographies to the cameras"""
    h_list = []
    number_dict={}
    for key in content.keys():
        number = matchKeyToNumber(key)
        print(key, number)
        H=content[key][0]
        print(H)
        H = H.reshape(-1)
        number_dict[number]=H

    for number in sorted(number_dict):
        for item in number_dict[number]:
            h_list.append(item)
    return h_list

def preparePointsAndObervations(content):
    """create points and observations lists in the respective format"""
    pointlist=[]
    pointidx=0
    observationlist=[]

    for key in content.keys():
        camera_idx=matchKeyToNumber(key)
        kp1=content[key][1]
        kp2 = content[key][2]
        matches = content[key][3]

        sum_distance = 0
        max_distance =-1
        for match in matches:
            if match.distance > max_distance:
                max_distance =match.distance
            sum_distance = sum_distance+match.distance

        for match in matches:
            basepoint = kp1[match.queryIdx]
            observation = kp2[match.trainIdx]
            relative_inverse_distance =1- (match.distance/max_distance)
            observationlist.append(str(camera_idx)+" "+str(pointidx)+"     "+str(observation.pt[0])+" "+str(observation.pt[1])+ " "+str(relative_inverse_distance))
            pointlist.append(basepoint.pt[0])
            pointlist.append(basepoint.pt[1])
            pointlist.append(1)
            pointidx=pointidx+1
    return pointlist, observationlist

def writeIntoFile(filename, num_cameras, num_points, num_observations, camera_list, point_list, observation_list):
    """writes the text file in the format for the ceres solver"""
    f = open(filename, "w")
    f.write(str(num_cameras)+" "+str(num_points)+" "+str(num_observations)+"\n")
    for o in observation_list:
        f.write(o+"\n")
    for c in camera_list:
        f.write(str(c)+"\n")
    for p in point_list:
        f.write(str(p)+"\n")
    f.close()

def readFromFile(filename):
    """reads the file with the optimized points and observations"""
    f = open(filename, "r")
    firstline=f.readline()
    parts = firstline.split(" ")
    num_cameras = int(parts[0])
    num_points = int(parts[1])
    num_observations = int(parts[2])
    str_observation=[]
    for i in range(0, num_observations):
        #read all observations
        str_observation.append(f.readline())
    
    cameras=[]
    for i in range(0, num_cameras*9):
        cameras.append(float(f.readline()))
    np_cam = np.array(cameras)
    np_cam = np.reshape(np_cam, (len(keyNumber.keys()),3,3))
    
    points=[]
    for i in range(0, num_points*3):
        points.append(float(f.readline()))
    
    return str_observation, np_cam, points

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1]=="prepare":
        #read the best homographies
        content= getBESTContent(persisted_files_folder, "bestH.pickle")
        camera_list=prepareCameras(content)
        num_cameras = len(keyNumber.keys())
        #create a points and observations list
        point_list, observation_list = preparePointsAndObervations(content)
        num_points = int(len(point_list)/3)
        num_observations = len(observation_list)
        #writes the data into the text file
        writeIntoFile("problem_avgrid.txt", num_cameras, num_points, num_observations, camera_list, point_list, observation_list)
    else:
        observation_list, camera_list, point_list=readFromFile("problem_avgrid_solved_weights.txt")
        writeToPickle(camera_list)

