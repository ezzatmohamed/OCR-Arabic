import numpy as np
import cv2
import os
import math
import matplotlib.pyplot as plt
import skimage.morphology
from skimage import img_as_ubyte

from skimage.morphology import binary_erosion, binary_dilation, binary_closing, skeletonize, thin


class Word:

    def __init__(self, Word,WordRGB, MTI, MFV, BaseIndex):
        self.Word = Word
        self.WordRGB = WordRGB
        self.MTI = MTI
        self.MFV = MFV
        self.BaseIndex = BaseIndex
        self.Regions = []
        self.Holes = []

    def IsHole(self, Start, End, Cut):

        a = self.Word[:, End:Start + 1].copy()
        MaxVal = 0
        Trans = 0
        for j in range(1, len(a)):
            if self.Word[j][Cut] != self.Word[j - 1][Cut]:
                Trans += 1

        if Trans > MaxVal:
            MaxVal = Trans

        Threshold = 2
        if MaxVal >Threshold:
            self.Holes.append(Cut)
            return True
        return False

    def IsPath(self, Start, End):
        a = self.Word[:, End:Start + 1].copy()
        # cv2.imshow('BaseLine', a)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        Mat = self.Word[:, End:Start + 1].copy()
        dim = Mat.shape
        rows = dim[0]
        cols = dim[1]
        IsReachable = np.zeros((rows, cols))

        for i in range(1, rows):
            if Mat[i][0] != 0:
                IsReachable[i][0] = 1

        for i in range(1, rows):
            for j in range(1, cols):
                if Mat[i][j] != 0:
                    IsReachable[i][j] = IsReachable[i - 1][j] or IsReachable[i][j - 1] or IsReachable[i - 1][j - 1]

        if np.sum(IsReachable[:, -1]) != 0:
            return True
        return False

    def IsValidCut(self, Start, End, Cut):
        if np.sum(self.Word[:, Cut]) == 0:
            return True
        elif not self.IsPath(Start, End):
            return True
        elif self.IsHole( Start, End, Cut):
            return False
        else:
            a = self.Word[:, End:Start + 1].copy()
            # cv2.imshow('Test Image', a)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            HP = np.sum(a, axis=1)
            HP1 = np.sum(HP[0:self.BaseIndex])
            HP2 = np.sum(HP[self.BaseIndex:])

            HP3 = HP[self.BaseIndex] / 255

            if Start != End:
                ratio = HP3 / (Start - End)
                if HP2 > HP1 and ratio < 0.5:
                    return False

        return True


    def IsStroke(self, Start, End):

        a = self.Word[:, End:Start + 1].copy()
        HP = np.sum(a, axis=1)
        HP1 = np.sum(HP[0:self.BaseIndex])
        HP2 = np.sum(HP[self.BaseIndex:])
        HP3 = HP[self.BaseIndex-1] / 255
        # Stroke => HP above baseline is greater than HP below the baseline

#        if HP1 < HP2:
#            return False
        for H in self.Holes:
            if H >= End and H <= Start:
                return False

        # Stroke => It has a connected line in the baseline
        ratio = HP3 / (Start - End)
        if ratio < 0.3:
            return False

        WordHP = np.sum(self.Word,axis=1)
        for i in range( len(WordHP) ):
            if WordHP[i] != 0:
                height = self.BaseIndex - i
                break
#        height = self.MTI-1
#        height = self.BaseIndex - height

        for i in range(len(HP)):
            if HP[i] != 0:
                if self.BaseIndex - i >= height-1:
                    return False
                else:
                    return True

        return True

        #np.max()

    def FilterStroke(self):

        i = 0
        Length = len(self.Regions)
        while ( i < Length-3 ):
            Start = self.Regions[i]
            End   = self.Regions[i+1]
            if not self.IsStroke(Start,End):
                i+=1
                continue
            Start = self.Regions[i+1]
            End   = self.Regions[i+2]
            if not self.IsStroke(Start,End):
                i+=1
                continue
            Start = self.Regions[i+2]
            End   = self.Regions[i+3]
            if self.IsStroke(Start,End):
                self.Regions.pop(i+1)
                self.Regions.pop(i+1)
                Length-=2
            i+=1

    def DetectCutPoints(self):
        # Flag = 0
        # cv2.imshow('Test Image', Word)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # print(Word.shape)

        End = Start = -1
        IsStart = False
        num = 1
        for i in range(len(self.Word[self.MTI]) - 2, 0, -1):
            if self.Word[self.MTI][i] == 0 and self.Word[self.MTI][i + 1] != 0:
                Start = i
                IsStart = True
            if self.Word[self.MTI][i] != 0 and self.Word[self.MTI][i + 1] == 0 and IsStart:

                End = i
                Mid = (End + Start) // 2
                IsStart = False
                # if Flag == 0 and Word[MTI][i] != 0:
                #    End = i
                #    Flag = 1
                # elif Flag == 1 and Word[MTI][i] == 0:
                #    Start = i
                #    Mid = (End + Start) // 2
                Cut = -1
                for j in range(End, Start + 1):
                    if np.sum(self.Word[:, j]) == 0:
                        Cut = j
                        break
                # VP = np.sum(Word[:,End:Start + 1], axis=0)

                if Cut != -1:
                    Cut = Cut

                elif np.sum(self.Word[:, Mid]) == self.MFV:
                    Cut = Mid

                else:
                    Cut = -1
                    for j in range(End, Mid + 1):
                        if np.sum(self.Word[:, j]) <= self.MFV:
                            Cut = j

                    if Cut != -1:
                        Cut = Cut
                    else:
                        Cut = -1
                        for j in range(Mid, Start + 1):
                            if np.sum(self.Word[:, j]) <= self.MFV:
                                Cut = j
                                break

                        if Cut != -1:
                            Cut = Cut
                        else:
                            Cut = Mid

                # if num == 2 or num == 4 or num == 7:
                # s    cv2.imwrite('res' + str(num) + '.jpg', Word[:, End:Start+3])
                if self.IsValidCut(Start - 1, End, Cut):
                    self.Regions.append(Cut)

                num += 1
                # cv2.imshow('BaseLine', Word[:,End:Start+3] )
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

                Flag = 0
            # print(Regions)

    def GetCuts(self):
        return self.Regions

    def Display(self):
        h = self.Word.shape[1]
        for j in range(len(self.Regions)):
            self.WordRGB = cv2.rectangle(self.WordRGB, (self.Regions[j], 0), (self.Regions[j], h), (0, 255, 0), 1)
