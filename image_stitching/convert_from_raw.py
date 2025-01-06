import cv2
import numpy as np

def convert_rggb_to_rgb(rggb):
    # idea from https://stackoverflow.com/questions/74919865/rggb-x-y-rgb-x-2-y-2-3
    r = rggb[0::2, 0::2]
    g1 = rggb[0::2, 1::2]
    g2 = rggb[1::2, 0::2]
    b = rggb[1::2, 1::2]
    # Combine the color channels into a Bayer pattern image 
    ret_arr = np.zeros((rggb.shape[0]//2, rggb.shape[1]//2, 3), np.uint16)
    ret_arr[:,:,0] = r
    ret_arr[:,:,1] = (g1 + g2)/2
    ret_arr[:,:,2] = b

    # OpenCV cvt.color conversion methode

    ret_arr = cv2.cvtColor(rggb, cv2.COLOR_BayerRGGB2BGR)

    return ret_arr

def bitshiftIn16Bit(value, places):
    return np.uint16(value) << places

def bitshiftleft(value, places):
    return value << places

def bitshiftright(value, places):
    return np.uint16(value >> places)

def bitand(arr1, arr2):
    return np.sum([arr1, arr2], axis=0)

def unpack8Bit(eightbit):
    # based on https://www.strollswithmydog.com/open-raspberry-pi-high-quality-camera-raw/
    twelfebit = np.zeros(3040*4056, np.uint16)
    eightbit = np.reshape(eightbit, (3040*6084))

    twelfebit[1::2] = bitand(bitshiftIn16Bit(eightbit[1::3], 4) ,bitshiftright(eightbit[2::3], 4)) # bit shift right

 
    twelfebit[0::2] = bitand(bitshiftIn16Bit(eightbit[0::3], 4),  bitshiftright(bitshiftleft(eightbit[2::3],4),4)) # first shift to left to kick out b, then shift back
    reshaped =np.reshape(twelfebit, (3040, 4056))

    return reshaped

def sliceNonImageData(arr):
     return np.delete(arr, slice(6084, 6112),1)

def convertFromRaw(arr):
    
    image = sliceNonImageData(arr)
    print("-------- Non image data sliced------------")


    #cv2.imwrite("firstimg.jpg", cv2.cvtColor(np.uint8(onlyimagedata),cv2.COLOR_BAYER_RG2RGB ))
    print("-----------unpacking 3x8bit to 2x12 bit and store in 16 bit---------------")
    image=unpack8Bit(image)

    print("----------convert rggb to rgb--------")
    # Extract the red, green, and blue color channels from the sensor data
    image=convert_rggb_to_rgb(image)

    return image