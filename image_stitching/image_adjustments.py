import numpy as np
import cv2
from skimage import img_as_ubyte
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from skimage.io import imread, imshow


def adaptWhitebalanceWithCut(value, lum, whitevalue):
    calc = value * lum / whitevalue
    calc[calc > 255] = 255

    return calc


def channel_statistics(image):
    df_color = []
    for i in range(0, 3):
        max_color = np.max(image[:, :, i])
        mean_color = np.mean(image[:, :, i])
        median_color = np.median(image[:, :, i])
        perc_90 = np.percentile(image[:, :, i], 90, axis=(0, 1))
        perc_95 = np.percentile(image[:, :, i], 95, axis=(0, 1))
        perc_99 = np.percentile(image[:, :, i], 99, axis=(0, 1))

        row = (max_color, mean_color, median_color,
               perc_90, perc_95, perc_99)
        df_color.append(row)

    return pd.DataFrame(df_color,
                        index=['Red', ' Green', 'Blue'],
                        columns=['Max', 'Mean', 'Median',
                                 'P_90', ' P_95', 'P_99'])


def createHistogram(image):
    color = ('b', 'g', 'r')
    for i, col in enumerate(color):
        histr = cv2.calcHist([image], [i], None, [256], [0, 256])
        plt.plot(histr, color=col)
        plt.xlim([0, 256])

    plt.show()


def whitepatch_balancing(image, from_row, from_column, row_width, column_width):
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    ax[0].imshow(image)
    ax[0].add_patch(Rectangle((from_column, from_row),
                              column_width,
                              row_width,
                              linewidth=3,
                              edgecolor='r', facecolor='none'));
    ax[0].set_title('Original image')
    image_patch = image[from_row:from_row + row_width, from_column:from_column + column_width]
    image_max = (image * 1.0 /
                 image_patch.max(axis=(0, 1))).clip(0, 1)
    print(image_patch.max(axis=(0, 1)))
    ax[1].imshow(image_max)
    ax[1].set_title('Whitebalanced Image')

    return image_max


def create_rgb_equalized(image):
    # get channels of the image b, g, r
    channels = cv2.split(image)
    eq_channels = []

    # create a CLAHE object
    clahe = cv2.createCLAHE(clipLimit=8.5, tileGridSize=(16, 16))

    # Loop through channels and apply adaptive histogram equalization
    for ch, color in zip(channels, ['B', 'G', 'R']):
        eq_channels.append(cv2.equalizeHist(ch))

    # Merge channels back together
    eq_image = cv2.merge(eq_channels)

    return eq_image


def whitebalance(image, whitecolor=(37, 95, 68)): 
    """executes a white balancing, white value determined by a photograph of an white paper lying in the aggregation"""
    # Use calculated color on image
    red_white = whitecolor[0]
    green_white = whitecolor[1]
    blue_white = whitecolor[2]

    lum = (red_white + green_white + blue_white) / 3

    # Split image in different channels
    blue, green, red = cv2.split(image)

    # Calculate new values with given white value
    blue_new = np.array([adaptWhitebalanceWithCut(b, lum, blue_white) for b in blue])
    blue_new = (np.rint(blue_new)).astype(np.uint8)

    red_new = np.array([adaptWhitebalanceWithCut(b, lum, red_white) for b in red])
    red_new = (np.rint(red_new)).astype(np.uint8)

    green_new = np.array([adaptWhitebalanceWithCut(b, lum, green_white) for b in green])
    green_new = (np.rint(green_new)).astype(np.uint8)

    ret_img = cv2.merge([blue_new, green_new, red_new])

    # Histogram equalisation
    ret_img = create_rgb_equalized(ret_img)

    return ret_img



def automatic_brightness_and_contrast(image, clip_hist_percent=1):
    """Automatic brightness and contrast optimization with optional histogram clipping"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum / 100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size - 1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    return (auto_result, alpha, beta)


def contrastAndBrightness(image, contrast=0.75, brightness=40):
    # https://www.tutorialspoint.com/how-to-change-the-contrast-and-brightness-of-an-image-using-opencv-in-python
    # https://www.geeksforgeeks.org/detecting-low-contrast-images-with-opencv-scikit-image-and-python/?ref=rp
    # maybe use  is_low_contrast(img,”threshold value”) from from skimage.exposure import is_low_contrast
    # call convertScaleAbs function

    # automatic alpha and beta calculation from https://stackoverflow.com/questions/56905592/automatic-contrast-and-brightness-adjustment-of-a-color-photo-of-a-sheet-of-pape
    adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
    #adjusted = automatic_brightness_and_contrast(image)[0]

    return adjusted


def adjust_gamma(image, gamma=0.6):
    # idea from https://pyimagesearch.com/2015/10/05/opencv-gamma-correction/
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def adjust_saturation(image):
    hsvImg = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsvImg[..., 1] = hsvImg[..., 1] * 1.3
    image = cv2.cvtColor(hsvImg, cv2.COLOR_HSV2BGR)

    return image


def convertFrom12To8Bit(image):
    return (image * ((2 ** 8 - 1) / (2 ** 12 - 1))).astype(np.uint8)
