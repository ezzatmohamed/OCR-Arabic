import cv2
import numpy as np
import matplotlib.pyplot as plt  # plot import

#import skimage.feature
#from commonfunctions import *
#from skimage.color import rgb2gray


def preprocess(img):
    # convert to gray scale
    gray = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)
    # blur image
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # convert to binary image
    _, thresholded_img = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)
    return thresholded_img


def get_edges(img, sigma):
    edges = skimage.feature.canny(
        image=img/255,
        sigma=1.5)

    return edges

# get height to width ratio


def get_h_w_ratio(bin_img):
    h = bin_img.shape[0]
    w = bin_img.shape[1]
    return h/w

# get num of black pixels over white pixels


def get_b_w_ratio(bin_img):
    a = np.array(bin_img)
    unique, counts = np.unique(a, return_counts=True)
    return counts[0] / counts[1]


def get_horizontal_transition(bin_img):
    a = np.array(bin_img/255).astype(np.uint8)
    count_bw = 0
    count_wb = 1
    for j in range(a.shape[0]):
        for i in range(a.shape[1]-1):
            if a[j, i] == 0 and a[j, i+1] == 1:
                count_bw += 1
            elif a[j, i] == 1 and a[j, i+1] == 0:
                count_wb += 1
    return count_bw, count_wb


def get_vertical_transition(bin_img):
    a = np.array(bin_img/255).astype(np.uint8)
    count_bw = 0
    count_wb = 0
    for j in range(a.shape[0]-1):
        for i in range(a.shape[1]-1):
            if a[j, i] == 0 and a[j+1, i] == 1:
                count_bw += 1
            elif a[j, i] == 1 and a[j+1, i] == 0:
                count_wb += 1
    return count_bw, count_wb

# dividing image into 4 regions


def divide_img(img):
    size = img.shape
    reg1 = img[0:int(size[0]/2), 0:int(size[1]/2)]
    reg2 = img[int(size[0]/2):int(size[0]), 0:int(size[1]/2)]
    reg3 = img[0:int(size[0]/2), int(size[1]/2):int(size[1])]
    reg4 = img[int(size[0]/2):int(size[0]), int(size[1]/2):int(size[1])]
    return reg1, reg2, reg3, reg4


def get_regions_b_w_ratios(reg1, reg2, reg3, reg4):

    return ratios


Img = cv2.imread('D:/Senior2/Pattern/PatternRepo/OCR-Arabic/2.png')
black_to_white, white_to_black = get_vertical_transition(preprocess(Img))
print(black_to_white, white_to_black)
segment_img(preprocess(Img))

#cv2.imshow("Lol", Img)
cv2.waitKey(0)
cv2.destroyAllWindows()
