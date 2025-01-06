import pickle
import sys
import os.path
import csv

from dbfileselector import *
from pickle_helper import writeFileContent

persisted_files_folder="./persisted_files"

def getAllImagesOfDroneFromCSVOrNASAndPersist(drone):
    "checks if the images are already in a csv file, if not, go through the NAS and collect them. Write them into a csv file"
    allImagesFilename = "allImages_"+drone+".csv"
    fullallImagesFilename = os.path.join(persisted_files_folder, allImagesFilename)
    allImages = []    
    if os.path.exists(fullallImagesFilename):
        f = open(fullallImagesFilename)
        csvreader = csv.reader(f)
        header = next(csvreader)
        for row in csvreader:
            allImages.append(row)
    else:
        print("CSV does not exist "+allImagesFilename)
        allImages=selectFilesOfDrone(drone, "K:/raw")
        csvheader= ["filename"]
        with open(fullallImagesFilename, "w", newline="") as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(csvheader)
            for image in allImages:
                csvwriter.writerow([image])
    return allImages

def getPairImageFromCSVOrDetermineAndPersist(source, target, allImages_source, allImages_target):
    """Determine Pairs of images with their timedifference from two neighbouring cameras"""
    pairImagesFilename = "pairImages_"+source+"_"+target+".pickle"
    allImagePairs = []    
    sourceImagesFromCSV=[]

    #extract all datetimes of the target images for easier access
    timestampsToFilenames={}
    for targetfilename in allImages_target:
        partstarget=targetfilename[0].split("\\")
        timestamp_target = ((partstarget[-1].split("--"))[0]).split("__")[-1]
        searchedDatetime_target = convertStringToDatetime(timestamp_target)
        if searchedDatetime_target in timestampsToFilenames:
            entry = timestampsToFilenames[searchedDatetime_target]
            entry.extend(targetfilename)
        else:
            timestampsToFilenames[searchedDatetime_target]= targetfilename

    for imgpath in allImages_source:

        if imgpath not in sourceImagesFromCSV:
            parts=imgpath[0].split("\\")
            timestamp = ((parts[-1].split("--"))[0]).split("__")[-1]
            millisecs = (((parts[-1].split("--"))[1]).split("___")[0]).split(".")[0]
            searchedDatetime = convertStringToDatetime(timestamp)
            if searchedDatetime in timestampsToFilenames:
                allTargetFilestoTimestamp = timestampsToFilenames[searchedDatetime]
                milliseclist={}
                for filename in allTargetFilestoTimestamp:
                    curparts=filename.split("\\")
                    curmillisecs = (((curparts[-1].split("--"))[1]).split("___")[0]).split(".")[0]
                    milliseclist[abs(int(millisecs)-int(curmillisecs))]=filename
                allImagePairs.append([imgpath[0], milliseclist[min(milliseclist)]])

    writeFileContent(persisted_files_folder, pairImagesFilename, allImagePairs)
    print("added "+str(len(allImagePairs))+" to pickle")
    return allImagePairs

def findImagePairs(cam_source, cam_target):
    "goes through the list of all? images of cam_source and checks if a match of target can be found"
    pairfilename = "foundPairs_"+cam_source+"_"+cam_target+".csv"

    print("Find all images of source and target")
    allImages_source=getAllImagesOfDroneFromCSVOrNASAndPersist(cam_source)
    allImages_target=getAllImagesOfDroneFromCSVOrNASAndPersist(cam_target)

    print("Find matching image to every image of source")
    matches = getPairImageFromCSVOrDetermineAndPersist(cam_source, cam_target, allImages_source, allImages_target)
    print(matches[0])


if __name__ == '__main__':
    if len(sys.argv) == 3:
        cam_source=sys.argv[1]
        cam_target=sys.argv[2]
        print("Search Pair Process will be started with "+cam_source+ " to "+cam_target)
        findImagePairs(cam_source, cam_target)
    else:
        print("Determine all Pairs")
        listOfPairs=[("drone-2-1", "drone-2-0")]
        #.... determine your own list
        for pair in listOfPairs:
            findImagePairs(pair[0], pair[1])