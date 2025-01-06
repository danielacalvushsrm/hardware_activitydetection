import os.path
import pickle
import cv2 as cv
#_______________________ Pickle
# functions to write, read pickle and to extract and write content into the files

def getFileContent(folder, filename):

    fullfile=os.path.join(folder,filename)
    foundPairs=[]

    if os.path.exists(fullfile):
        #load the file and find the last match
        f = open(fullfile, "rb")
        foundPairs = pickle.load(f)
        f.close()
    return depickleDMatchAndKP(foundPairs)

def getBESTContent(folder, filename):

    fullfile=os.path.join(folder,filename)
    foundPairs={}

    if os.path.exists(fullfile):
        #load the file and find the last match
        f = open(fullfile, "rb")
        foundPairs = pickle.load(f)
        f.close()
    return depickleBESTKPandMatch(foundPairs)

def getBESTHContent(folder, filename):
    """Gets a pickle file with only Hs (to use in 05 stitch)"""
    fullfile=os.path.join(folder,filename)
    foundPairs={}

    if os.path.exists(fullfile):
        #load the file and find the last match
        f = open(fullfile, "rb")
        foundPairs = pickle.load(f)
        f.close()
    return foundPairs

def writeFileContent(folder, filename, content):
    fullfile=os.path.join(folder,filename)
    file=open(fullfile, "wb")
    pickle.dump(pickleDMatchAndKP(content), file)
    file.close()

def writeBESTContent(folder, filename, content):
    fullfile=os.path.join(folder,filename)
    file=open(fullfile, "wb")
    pickle.dump(pickleBESTDMatchAndKP(content), file)
    file.close()

def writeBESTHContent(folder, filename, content):
    """To use after bundleAdjustment, we only need the Hs"""
    fullfile=os.path.join(folder,filename)
    file=open(fullfile, "wb")
    pickle.dump(content, file)
    file.close()

def depickleBESTKPandMatch(list):
    # pos 3 is Match
    #pos 4 and 5 is kp
    newlist = {}
    for key in list.keys():
        elem =list[key]
        print(len(elem))
        if len(elem) == 4:
            #todo check indices
            kp1 = depickleKeypoints(elem[1])
            kp2 = depickleKeypoints(elem[2])
            match = depickleMatch(elem[3])
            newlist[key]=(elem[0],  kp1, kp2,match)
        else:
            newlist[key]=elem
    return newlist

def depickleDMatchAndKP(list):
    # pos 3 is Match
    #pos 4 and 5 is kp
    newlist = []
    for elem in list:
        if len(elem) == 10:
            #evalvalue, h, #no, std,h, match,kp1, kp2
            match= depickleMatch(elem[5])
            kp1 = depickleKeypoints(elem[6])
            kp2 = depickleKeypoints(elem[8])
            newlist.append((elem[0], elem[1], elem[2], elem[3], elem[4],match, kp1, elem[7],kp2, elem[9]))
        else:
            newlist.append(elem)
    return newlist


def pickleBESTDMatchAndKP(content):
    newcontent={}
    for key in content.keys():
        elem = content[key]
        
        if len(elem) ==4:
            #h, kp1, kp2
            kp1 = pickleKeypoints(elem[1])
            kp2 = pickleKeypoints(elem[2])
            matches = pickleMatch(elem[3])
            newcontent[key]=(elem[0],kp1, kp2, matches)
        else:
            newcontent[key]=elem
    return newcontent

def pickleDMatchAndKP(content):
    newcontent=[]
    for elem in content:
        if len(elem) ==10:
            match= pickleMatch(elem[5])
            kp1 = pickleKeypoints(elem[6])
            des1 = elem[7]
            kp2 = pickleKeypoints(elem[8])
            des2 = elem[9]
            newcontent.append((elem[0], elem[1], elem[2], elem[3], elem[4],match, kp1, des1,kp2, des2))
        else:
            newcontent.append(elem)
    return newcontent



def pickleKeypoints(kp):
    kpelems=[]
    for point in kp:
        temp = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id)      
        kpelems.append(temp)
    return kpelems

def depickleKeypoints(kpelems):
    kp=[]
    for point in kpelems:
        kp.append(cv.KeyPoint(x=point[0][0],y=point[0][1],size=point[1], angle=point[2], 
                            response=point[3], octave=point[4], class_id=point[5]) )
    return kp

def pickleMatch(good):
    goodelems=[]
    for match in good:
        temp = (match.queryIdx, match.trainIdx, match.imgIdx, match.distance)
        goodelems.append(temp)
    return goodelems

def depickleMatch(goodelems):
    good=[]
    for match in goodelems:
        good.append(cv.DMatch(match[0], match[1], match[2], match[3]))
    return good