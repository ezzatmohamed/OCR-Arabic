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
    return thresholded_img/255


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


def get_black_pixels(img):
    unique, counts = np.unique(img, return_counts=True)
    return counts[0]


def get_white_pixels(img):
    unique, counts = np.unique(img, return_counts=True)
    return counts[1]


def get_horizontal_transition(bin_img):
    a = np.array(bin_img).astype(np.uint8)
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
    a = np.array(bin_img).astype(np.uint8)
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
    return reg1/255, reg2/255, reg3/255, reg4/255


def get_regions_b_w_ratios(reg1, reg2, reg3, reg4):
    ratios = []
    B1W1 = get_black_pixels(reg1)/get_white_pixels(reg1)
    B2W2 = get_black_pixels(reg2)/get_white_pixels(reg2)
    B3W3 = get_black_pixels(reg3)/get_white_pixels(reg3)
    B4W4 = get_black_pixels(reg4)/get_white_pixels(reg4)
    B1B2 = get_black_pixels(reg1)/get_black_pixels(reg2)
    B3B4 = get_black_pixels(reg3)/get_black_pixels(reg4)
    B1B3 = get_black_pixels(reg1)/get_black_pixels(reg3)
    B2B4 = get_black_pixels(reg2)/get_black_pixels(reg4)
    B1B4 = get_black_pixels(reg1)/get_black_pixels(reg4)
    B2B3 = get_black_pixels(reg2)/get_black_pixels(reg3)
    ratios.append([B1W1, B2W2, B3W3, B4W4, B1B2, B3B4, B1B3, B2B4, B1B4, B2B3])
    ratios_dict = {
        "B1W1": B1W1,
        "B2W2": B2W2,
        "B3W3": B3W3,
        "B4W4": B4W4,
        "B1B2": B1B2,
        "B3B4": B3B4,
        "B1B3": B1B3,
        "B2B4": B2B4,
        "B1B4": B1B4,
        "B2B3": B2B3
    }
    return ratios

# Will add class num


def extract_features(img):
    features = []
    bin_img = preprocess(img)
    features.append(get_h_w_ratio(bin_img))
    features.append(get_b_w_ratio(bin_img))
    features.append(get_vertical_transition(bin_img))
    features.append(get_horizontal_transition(bin_img))
    r, t, z, l = divide_img(preprocess(Img))
    features.append(get_regions_b_w_ratios(r, t, z, l))
    return features


Img = cv2.imread('D:/Senior2/Pattern/PatternRepo/OCR-Arabic/2.png')
#black_to_white, white_to_black = get_vertical_transition(preprocess(Img))
#print(black_to_white, white_to_black)
#r, t, z, l = divide_img(preprocess(Img))
#print(get_regions_b_w_ratios(r, t, z, l))
# get_black_pixels(r) [0. 1.] [ 18 894]
# get_b_w_ratio(preprocess(Img)/255)
#cv2.imshow("Lol", Img)
print(extract_features(Img))
cv2.waitKey(0)
cv2.destroyAllWindows()
