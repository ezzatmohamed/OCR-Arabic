import numpy as np
import cv2
import os
import math
import matplotlib.pyplot as plt
import skimage.morphology
from skimage import img_as_ubyte

from skimage.morphology import binary_erosion, binary_dilation, binary_closing, skeletonize, thin


class Word:

    def __init__(self, Word,WordRGB, MTI, MFV, BaseIndex,height):
        self.Word = Word
        self.WordRGB = WordRGB
        self.MTI = MTI
        self.MFV = MFV
        self.BaseIndex = BaseIndex
        self.Regions = []
        self.Holes = []
        self.height = height
        #self.GetHeight()

    def GetHeight(self):
        WordHP = np.sum(self.Word, axis=1)
        for i in range(len(WordHP)):
            if WordHP[i] != 0:
                self.height = self.BaseIndex - i
                break

    def IsHole(self, Start, End, Cut):

        a = self.Word[:, End:Start + 1].copy()
        MaxVal = 0
        Trans = 0

        for j in range(1, self.BaseIndex+1):
            if self.Word[j][Cut] != self.Word[j - 1][Cut]:
                Trans += 1
        if Trans > MaxVal:
            MaxVal = Trans

        Threshold = 2
        if MaxVal >=Threshold:
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

        # for j in range(1, cols):
        #     if Mat[0][j] != 0:
        #         IsReachable[0][j] = 1

        for i in range(1, rows):
            for j in range(1, cols):
                if Mat[i][j] != 0:
                    IsReachable[i][j] = IsReachable[i - 1][j] or IsReachable[i][j - 1] or IsReachable[i - 1][j - 1] # or IsReachable[i][j + 1]

        if np.sum(IsReachable[:, -1]) != 0:
            return True
        return False

    def IsValidCut(self, Start, End, Cut):
        if np.sum(self.Word[:, Cut]) == 0:
            return True

        elif self.IsHole( Start, End, Cut):
            return False
        # TODO : Fix Connected-Path Algorithm
        elif not self.IsPath(Start,End):
            return True


        else:
            a = self.Word[:, End:Start + 1].copy()
            # cv2.imshow('Test Image', a)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            HP = np.sum(a, axis=1)
            HP1 = np.sum(HP[0:self.BaseIndex])
            HP2 = np.sum(HP[self.BaseIndex+1:])

            HP3 = HP[self.BaseIndex] / 255
            HP4 = HP[self.BaseIndex+1] / 255
            #HP3 += HP[self.BaseIndex-1] / 255
            if Start != End:
                ratio = HP3 / (Start - End)
                ratio2 = HP4 / (Start - End)
                if HP2 > HP1 and ratio < 0.5 and ratio2 < 0.5:
                    return False

        return True


    def IsStroke(self, Start, End):

        a = self.Word[:, End+1:Start].copy()
        HP = np.sum(a, axis=1)
        HP1 = np.sum(HP[0:self.BaseIndex])
        HP2 = np.sum(HP[self.BaseIndex+2:])
        HP3 = HP[self.BaseIndex] / 255
        # Stroke => HP above baseline is greater than HP below the baseline

        for H in self.Holes:
            if H >= End and H <= Start:
                return False

        if HP2 !=0 :
            return False

        # Stroke => It has a connected line in the baseline
        # ratio = HP3 / (Start - End)
        # if ratio < 0.6:
        #     return False

        # WordHP = np.sum(self.Word,axis=1)
        # for i in range( len(WordHP) ):
        #     if WordHP[i] != 0:
        #         height = self.BaseIndex - i
        #         break

        for i in range(len(HP)):
            if HP[i] != 0:
                if i <= self.height+1:
                    return False
                else:
                    break

        Trans = 0
        Flag = 0
        for i in range(self.BaseIndex):
            if Flag == 0 and HP[i] != 0 :
                Trans+=1
                Flag = 1
            elif Flag == 1 and HP[i] == 0:
                Trans+=1
                Flag =0

        if Trans > 2:
            return False


        return True

    def IsStrokeDots(self, Start, End):
        a = self.Word[:, End+1:Start].copy()
        HP = np.sum(a, axis=1)
        HP1 = np.sum(HP[0:self.BaseIndex])
        HP2 = np.sum(HP[self.BaseIndex + 1:])
        HP3 = HP[self.BaseIndex] / 255
        # Stroke => HP above baseline is greater than HP below the baseline

        for H in self.Holes:
            if H >= End and H <= Start:
                return False

        if HP2 !=0:
            return False

        # Stroke => It has a connected line in the baseline
        # ratio = HP3 / (Start - End)
        # if ratio < 0.6:
        #     return False


        Trans = 0
        Flag = 0
        for i in range(self.BaseIndex):
            if Flag == 0 and HP[i] != 0:
                Trans+=1
                Flag = 1

            elif Flag == 1 and HP[i] == 0:
                Trans +=1
                Flag = 0
        if Trans < 3 :
            return False

        return True

    def FilterDal(self):
        # pass
        Length = len(self.Regions)
        i=0
        while( i < Length-1 ):
            Start = self.Regions[i]
            End  = self.Regions[i+1]
            Sum = np.sum(self.Word[:,End:Start]) // 255
            if Sum <= 5:
                self.Regions.pop(i)
                Length-=1
            else:
                i+=1

        if Length <= 0:
            return
        Start = self.Regions[Length - 1]

        End =  0
        Sum = np.sum(self.Word[:, End:Start]) // 255
        if Sum <= 5:
            self.Regions.pop(Length-1)
            Length -= 1




    def CheckPop(self,Cut):
        VP = np.sum(self.Word, axis=0)
        if VP[Cut] == 0:
            return False

        # if not self.IsPath((Start,End)):
        #     return False
        return True


    def FilterStroke(self):

        #Filter Seeen
        #TODO: Check No zero VP in the character 'س' , check it is not '7ah' using transitions

        i = -1
        Length = len(self.Regions)
        while ( i < Length-2 ):
            if i == -1:
                VP = np.sum(self.Word,axis=0)
                for j in range( len(VP)-1,0,-1):
                    if VP[j] != 0:
                        Start = j+1
                        break

            else:
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
            if i ==  Length-3:
                if self.CheckPop(self.Regions[i+1]) and self.CheckPop(self.Regions[i+2]):
                    self.Regions.pop(i + 1)
                    self.Regions.pop(i + 1)
                    Length -= 2
            else:
                Start = self.Regions[i+2]
                End   = self.Regions[i+3]
                if self.IsStroke(Start, End):
                    if self.CheckPop(self.Regions[i + 1]) and self.CheckPop(self.Regions[i + 2]):
                        self.Regions.pop(i + 1)
                        self.Regions.pop(i + 1)
                        Length -= 2
            i+=1

        # Filtering Sheeen
        i = -1
        Length = len(self.Regions)
        while (i < Length - 2):

            if i == -1:
                VP = np.sum(self.Word, axis=0)
                for j in range(len(VP) - 1, 0, -1):
                    if VP[j] != 0:
                        Start = j
                        break
            else:
                Start = self.Regions[i]

            End = self.Regions[i + 1]
            if not self.IsStroke(Start+1, End):
                i += 1
                continue

            if i != Length-3:
                Start = self.Regions[i + 2]
                End = self.Regions[i + 3]
                if not self.IsStroke(Start, End):
                    i += 1
                    continue

            Start = self.Regions[i + 1]
            End = self.Regions[i + 2]
            if  self.IsStrokeDots(Start, End):
                if self.CheckPop(self.Regions[i+1]) and self.CheckPop(self.Regions[i+2]):
                    self.Regions.pop(i + 1)
                    self.Regions.pop(i + 1)
                    Length -= 2

            i += 1

        i = 0
        Length = len(self.Regions)
        #
        # # Filter ( saad , Daad)
        for H in self.Holes:
            i = 0
            while( i < Length-2 ):
                Start = self.Regions[i]
                End = self.Regions[i + 1]
                if ( H > End and H < Start ):
                    break
                i+=1
            if i >= Length-2:
                continue
            Start = self.Regions[i+1]
            End = self.Regions[i+2]
            if self.IsStroke(Start,End):
                if self.CheckPop(self.Regions[i+1]):

                    HP4 =  np.sum(self.Word[:,End:Start+1],axis=1)
                    h=0
                    for k in range(len(HP4)):
                        if HP4[k] !=0:
                            h= self.BaseIndex - k
                            break
                    self.Regions.pop(i+1)
                    Length-=1



        if Length < 1:
            return
        LastCut = self.Regions[Length-1]
        a = self.Word[:,0:(LastCut)].copy()
        HP = np.sum(a, axis=1)
        VP = np.sum(self.Word[:,LastCut], axis=0)

        HP1 = np.sum(HP[0:self.BaseIndex])
        HP2 = np.sum(HP[self.BaseIndex+1:])
        H = self.BaseIndex
        for i in range(self.BaseIndex):
            if HP[i] != 0:
                H = i
                break


        #if self.IsStroke(LastCut//2,0) and VP != 0:
        #    self.Regions.pop(Length - 1)
        # 0.2*HP2 <= HP1
        # if ( (self.BaseIndex- H) < 0.5 * (self.BaseIndex - self.height) ) and VP != 0:#and 0.7*HP2 <= HP1:
        #      self.Regions.pop(Length-1)

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

    def GetChars(self):
        Length = len(self.Regions)

        Chars = []

        Last = 0


        for i in range(Length-1,-1,-1):
            SegmentedChar = self.Word[:,Last:self.Regions[i]].copy()
            Chars.append(SegmentedChar)
            Last = self.Regions[i]

        SegmentedChar = self.Word[:, Last:].copy()

        Chars.append(SegmentedChar)

        return Chars[::-1]
