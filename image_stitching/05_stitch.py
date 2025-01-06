import sys
import time

from rawToImgConverter import *

from HomographyTree import HomographyTree
from homography_helper import *
from pickle_helper import *
from dbfileselector import selectFilesByTimestamp
width=4056
height=3040
displayMasks = True
displayFinalImage= False
displayStitched = False
saveFinalImage = True
cv.ocl.setUseOpenCL(False)
displayGrid=False
#replace with your own system
construction =[[CAM_SOURCE.DRONE30, CAM_SOURCE.DRONE20, CAM_SOURCE.DRONE10, CAM_SOURCE.DRONE00],
                [CAM_SOURCE.DRONE31, CAM_SOURCE.DRONE21, CAM_SOURCE.DRONEE1, CAM_SOURCE.DRONE01],
                [CAM_SOURCE.DRONE32, CAM_SOURCE.DRONE22, CAM_SOURCE.DRONE12, CAM_SOURCE.DRONE02]]
persisted_files_folder="./persisted_files"

def HomographyMatrixOf(data, way):
    "returns a list of homographies whoose needs to be applied to come to target"
    homographylist= []
    #append all Hs all the way long
    i=0
    j=1
    while(j < len(way)):
        csource = way[i]
        ctarget=way[j]
        homographylist.append(data[getNameOfEnume(csource)+"__"+getNameOfEnume(ctarget)])
        i=i+1
        j=j+1
    return homographylist

def createImage(images):
    """Build up the graph by using homographytree instances"""
    d00 = HomographyTree(CAM_SOURCE.DRONE00, images[CAM_SOURCE.DRONE00],(0,3), None)
    d32 = HomographyTree(CAM_SOURCE.DRONE32, images[CAM_SOURCE.DRONE32],(2,0), None)
    d30 = HomographyTree(CAM_SOURCE.DRONE30, images[CAM_SOURCE.DRONE30],(0,0), None)
    d02 = HomographyTree(CAM_SOURCE.DRONE02, images[CAM_SOURCE.DRONE02], (2,3),None)

    d10 = HomographyTree(CAM_SOURCE.DRONE10,images[CAM_SOURCE.DRONE10],(0,2),  [d00])
    d20 = HomographyTree(CAM_SOURCE.DRONE20, images[CAM_SOURCE.DRONE20],(0,1), None)

    d22 = HomographyTree(CAM_SOURCE.DRONE22, images[CAM_SOURCE.DRONE22],(2,1), None))

    d31 = HomographyTree(CAM_SOURCE.DRONE31, images[CAM_SOURCE.DRONE31],(1,0), [d30, d32])

    d12 = HomographyTree(CAM_SOURCE.DRONE12,images[CAM_SOURCE.DRONE12],(2,2),  [d02])
    de1 = HomographyTree(CAM_SOURCE.DRONEE1, images[CAM_SOURCE.DRONEE1],(1,2), [d10, d12])

    #fake element for Drone 01, which was broken in 2023
    d01 = HomographyTree(CAM_SOURCE.DRONE01, getBlackNPImage(width, height),(1,3), None)

    root = HomographyTree(CAM_SOURCE.DRONE21,images[CAM_SOURCE.DRONE21],(1,1),[d20, d22, d31, de1])

    #set gridstructure
    d00.set_next(None, d01)
    d10.set_next(d00, de1)
    d20.set_next(d10, root)
    d30.set_next(d20, d31)
    d31.set_next(root, d32)
    root.set_next(de1, d22)
    de1.set_next(d01, d12)
    d01.set_next(None, d02)
    d32.set_next(d22, None)
    d22.set_next(d12, None)
    d12.set_next(d02, None)
    d02.set_next(None, None)

    filename = "bestH_ba.pickle"
    data=getBESTHContent(persisted_files_folder, filename)

    #we only need the homographies
    homographydata = {}
    for key in data.keys():
        homographydata[key]=data[key] 
    root.setHomography(homographydata, [])     

    #display all images in a grid
    if displayGrid:
        f,ax = plt.subplots(3,4)
        ax[0,0].imshow(d30.warpedImage, cmap='gray')
        ax[0, 0].set_title("drone 3 0")
        ax[1,0].imshow(d31.warpedImage, cmap='gray')
        ax[1, 0].set_title("drone 3 1")
        ax[2,0].imshow(d32.warpedImage, cmap='gray')
        ax[2, 0].set_title("drone 3 2")

        ax[0,1].imshow(d20.warpedImage, cmap='gray')
        ax[0, 1].set_title("drone 2 0")
        ax[1,1].imshow(root.warpedImage, cmap='gray')
        ax[1,1].set_title("drone 2 1 (root)")
        ax[2,1].imshow(d22.warpedImage, cmap='gray')
        ax[2, 1].set_title("drone 2 2")

        ax[0,2].imshow(d10.warpedImage, cmap='gray')
        ax[0, 2].set_title("drone 1 0")
        ax[1,2].imshow(de1.warpedImage, cmap='gray')
        ax[1,2].set_title("drone E 1")
        ax[2,2].imshow(d12.warpedImage, cmap='gray')
        ax[2,2].set_title("drone 1 2")

        ax[0,3].imshow(d00.warpedImage, cmap='gray')
        ax[0, 3].set_title("drone 0 0")
        ax[1,3].imshow(d01.warpedImage, cmap='gray')
        ax[1,3].set_title("drone 0 1 (broken)")
        ax[2,3].imshow(d02.warpedImage, cmap='gray')
        ax[2,3].set_title("drone 0 2")
        

        plt.show()

    #calculate final size of the gigaimage 
    sizeOfGigaimage=(d32.getMaxHeightOfCol(0),d00.getMaxWidthOfRow(0) )
    print("Fullsize of image: ",sizeOfGigaimage)
    #generate the giga Image for every Node
    root.generateFullImage(sizeOfGigaimage)

    #blend all images into one
    blender = cv.detail.Blender_createDefault(cv.detail.BLENDER_FEATHER)
    roi = (0,0,root.gigaImage.shape[1],d31.gigaImage.shape[0])
    blender.prepare(roi)
    print("Feed blender...")
    for node in root.getAllSubNodes():
        blender.feed(node.gigaImage.astype(np.int16), node.mask.astype(np.uint8), (0,0))
        
    res = None
    res_mask =None
    print("Blend images...")
    out, out_mask = blender.blend(res,res_mask)
    return out

def getBlackNPImage(width, height):
    """returns a black image in the shape width x height"""
    return np.zeros((height, width, 3), dtype = np.uint8)

def convertNpysToImages(npys):
    """converts the bayer file into an image file"""
    images={}
    for row in construction:
        for elem in row:
            print(elem)
            if elem in npys:
                # we have an image convert the image
                images[elem]=convertImage(npys[elem])
            else:
                print("no image found - create black one")
                images[elem] = getBlackNPImage(width, height)

    return images

if __name__ == '__main__':
    if len(sys.argv) == 2:
        timestamp = sys.argv[1]
    else:
        timestamp ="07-04-2023_16-00-00"
        print("Create Stitch for: "+str(timestamp))
        npysOfDrones=selectFilesByTimestamp(timestamp, "K:/raw")
        #convert all images to rgb
        images = convertNpysToImages(npysOfDrones)
    image=createImage(images)
    if displayFinalImage:
        plt.imshow(image)
        plt.show()
    if saveFinalImage:
        cv.imwrite("Stitch_ba_weights_distance.jpg", cv.cvtColor(image.astype('uint8'), cv.COLOR_RGB2BGR))




