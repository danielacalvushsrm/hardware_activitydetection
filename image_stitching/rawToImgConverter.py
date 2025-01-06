
import numpy as np
from PIL import Image, ImageEnhance
from image_adjustments import *
from convert_from_raw import *
import cv2 as cv

def loadImage(path):
    "loads the numpy image from a fiel and reshapes it"
    buf = np.load(path)
    arr = np.frombuffer(buf, dtype=np.uint8)
    arr = np.reshape(arr, (3040, 6112))
    return arr

def convertImage(f):
    arr = loadImage(f)  
    print("-------- NPY loaded------------")

    image = convertFromRaw(arr)

    print("----------convert from 12 to 8 bit--------")
    # Scale 12 bit / channel to 8 bit per channel
    image = convertFrom12To8Bit(image)


    print("----------(color corrections)--------")
    print("----------(white balancing)--------")
    image = whitebalance(image)

    print("---------- contrast and brightness correction--------")
    image = contrastAndBrightness(image)

    print("---------- gamma correction--------")
    image = adjust_gamma(image)

    print("---------- saturation --------")
    image = adjust_saturation(image)
    return image
