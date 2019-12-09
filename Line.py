import numpy as np
import cv2
import os
import math
import matplotlib.pyplot as plt
import skimage.morphology
from skimage import img_as_ubyte

from skimage.morphology import binary_erosion, binary_dilation, binary_closing, skeletonize, thin


class Line:

    def __init__(self,L_Binary,L_RGB):
        self.L_Binary = L_Binary
        self.L_RGB    = L_RGB
        self.G = []
        self.L = []
        self.Words = []
        self.WordsRGB = []
        self.Baseline=0
        self.MTI  =0

    def FilterGaps(self):
        IQR = 2

        # Filtering Depending On IQR ( Interquartile Range ) Value
        # G => Gaps
        # L => Length of The Gap
        self.G = self.G[self.L >= IQR] # Removing Gaps Which its length < IQR
        self.L = self.L[self.L >= IQR] # Removing Gaps' Lengths

        Mean = np.mean(self.L)
        self.G = self.G[self.L >= Mean]
        self.L = self.L[self.L >= Mean]

    def FindGaps(self):

        # Vertical Projection Of the text
        VP = np.sum(self.L_Binary, axis=0)
        VP2 = VP[VP != 0].astype(np.int64)

        self.MFV = np.bincount(VP2).argmax()

        flag = 0
        for i in range(len(VP)):

            if VP[i] == 0:
                if flag == 0:
                    # This is a Gap Start
                    self.G.append(i)
                    self.L.append(1)
                    flag = 1
                else:
                    # Increment Gap Length
                    self.L[-1] += 1


            elif flag == 1:
                # End of The Gap
                flag = 0

        self.G = np.array(self.G)
        self.L = np.array(self.L)

    def WordSegment(self):
        # G => Array of Gaps, L => Length of each gap
        self.FindGaps()
        self.FilterGaps()

        # Separete Each Word in a single Image
        self.Words = [self.L_Binary[0:, self.G[i] + self.L[i]:self.G[i + 1]] for i in range(len(self.G) - 1)]
        self.WordsRGB = [self.L_RGB[0:, self.G[i] + self.L[i]:self.G[i + 1]] for i in range(len(self.G) - 1)]


    def MaxTrans(self):

        self.MTI = 0
        MaxVal = 0

        for i in range(0, self.Baseline):
            Trans = 0
            for k in range(1, len(self.L_Binary[i])):
                if self.L_Binary[i][k] != self.L_Binary[i][k - 1]:
                    Trans += 1
            if Trans > MaxVal:
                MaxVal = Trans
                self.MTI = i
        self.MTI = self.MTI
        #MTIidx = []

    def DetectBaseline(self):
        ThinnedImg = skimage.morphology.thin(self.L_Binary)
        ThinnedImg = img_as_ubyte(ThinnedImg)

        #HP = ThinnedImg

        HP = np.array(np.sum(ThinnedImg, axis=1))
        # BaseIndex = np.argmax(Baseline)
        BaseIndex = 0
        for i in range(len(HP) - 1, 0, -1):
            if HP[i] > HP[BaseIndex]:
                BaseIndex = i

        self.Baseline = BaseIndex +1

    def GetMFV(self):
        return self.MFV

    def GetBinWords(self):
        return self.Words

    def GetRGBWords(self):
        return self.WordsRGB

    def GetMTI(self):
        return self.MTI

    def GetBaseline(self):
        return self.Baseline
    def GetBinaryL(self):
        return self.L_Binary

