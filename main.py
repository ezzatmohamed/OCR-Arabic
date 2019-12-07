import numpy as np
import cv2
import os
from Line import *
from Word import *

import math
import matplotlib.pyplot as plt
import skimage.morphology
from skimage import img_as_ubyte

from skimage.morphology import binary_erosion, binary_dilation, binary_closing, skeletonize, thin


# Gaps are whether Gaps between words OR Gaps within sub-word
# removing sub-word Gaps

def SegmentLines(Img,ImgRGB):
    HP = np.sum(Img,axis=1)

    Start = -1
    Lines = []
    LinesRGB = []
    C = 0
    for i in range(1,HP.size):
        if HP[i] != 0 and HP[i-1] == 0 and Start == -1:
            Start = i-1
        elif HP[i] == 0 and HP[i-1] != 0 and Start != -1:
            End   = i
            NewLine = Img[Start:End+1,:].copy()
            NewLineRGB = ImgRGB[Start:End+1,:].copy()

            Start = -1

            HP2 = np.sum(NewLine,axis=1)
            Max = np.max(HP2)
            if Max / 255  < 10:
                continue
            Lines.append(NewLine)
            LinesRGB.append(NewLineRGB)

    return np.array(Lines),np.array(LinesRGB)

def ToBinaryImg(Img):
    ImgGray = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)
    BinaryImg = np.array(ImgGray)
    BinaryImg[ImgGray > 127] = 0
    BinaryImg[ImgGray <= 127] = 255
    print(BinaryImg.shape)
    # cv2.imshow('Gray Image', ImgGray)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # cv2.imshow('Binary Image', BinaryImg)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return BinaryImg

WordIdx = 2
Img = cv2.imread('1.png')
dim = Img.shape
BinaryImg = ToBinaryImg(Img)
Lines, LinesRGB = SegmentLines(BinaryImg,Img)

for idx in range( len(Lines)) :

    L = Line(Lines[idx],LinesRGB[idx])
    h = Lines[idx].shape[1]

    #cv2.imshow('BaseLine', Lines[idx])
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    L.WordSegment()
    L.DetectBaseline()
    L.MaxTrans()

    Words = L.GetBinWords()
    WordsRGB = L.GetRGBWords()
    MFV   = L.GetMFV()
    BaseIndex = L.GetBaseline()
    MTI = L.GetMTI()

    Name = "Line_" + str(idx)
    os.mkdir(Name)
    cv2.imwrite(Name+'/'+Name+'.jpg', L.GetBinaryL())

    for i in range(len(Words)):
        W = Word(Words[i],WordsRGB[i] ,MTI, MFV, BaseIndex)
        W.DetectCutPoints()
        Cuts = W.GetCuts()

        #W.Display()

        for j in range(len(Cuts)):
            WordsRGB[i] = cv2.rectangle(WordsRGB[i], (Cuts[j], 0), (Cuts[j], h), (0, 255, 0), 1)



        cv2.imwrite(Name+'/word'+str(i)+'.jpg', WordsRGB[i])


    # Cuts = Test(Words[0],BaseIndex,MFV)
    #WordsRGB[WordIdx] = cv2.rectangle(WordsRGB[WordIdx], (0, MTI), (dim[0], MTI), (0, 255, 0), 1)
    #WordsRGB[WordIdx] = cv2.rectangle(WordsRGB[WordIdx], (0, BaseIndex), (dim[0], BaseIndex), (0, 255, 0), 1)