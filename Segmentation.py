import numpy as np
import cv2
import os
from Line import *
from Word import *
import shutil

import math
import matplotlib.pyplot as plt
import skimage.morphology
from skimage import img_as_ubyte

from skimage.morphology import binary_erosion, binary_dilation, binary_closing, skeletonize, thin


class Segmentation:

    def __init__(self,Img):
        self.Img = Img
        self.Binary_Img = Img
        self.Bin_Lines = []
        self.RGB_Lines = []
        self.Result = []
    def ToBinaryImg(self):
        ImgGray = cv2.cvtColor(self.Img, cv2.COLOR_BGR2GRAY)
        self.Binary_Img = np.array(ImgGray)
        self.Binary_Img[ImgGray > 127] = 0
        self.Binary_Img[ImgGray <= 127] = 255

    def SegmentLines(self):

        HP = np.sum(self.Binary_Img, axis=1)

        Start = -1
        C = 0
        for i in range(1, HP.size):
            if HP[i] != 0 and HP[i - 1] == 0 and Start == -1:
                Start = i - 1
            elif HP[i] == 0 and HP[i - 1] != 0 and Start != -1:
                End = i
                NewLine = self.Binary_Img[Start:End + 1, :].copy()
                NewLineRGB = self.Img[Start:End + 1, :].copy()

                Start = -1

                HP2 = np.sum(NewLine, axis=1)
                Max = np.max(HP2)
                if Max / 255 < 10:
                    continue
                self.Bin_Lines.append(NewLine)
                self.RGB_Lines.append(NewLineRGB)

    def CreateTestFolder(self):
        Test_Number = 1
        while (os.path.isdir("tests/test" + str(Test_Number))):
            Test_Number += 1
        Path = "tests/test" + str(Test_Number)
        os.mkdir(Path)
        return Path

    def Start(self):

        Path = self.CreateTestFolder()

        dim = self.Img.shape
        self.ToBinaryImg()
        self.SegmentLines()


        Lines = []

        for idx in range(len(self.Bin_Lines)):

            L = Line(self.Bin_Lines[idx], self.RGB_Lines[idx])
            h = self.Bin_Lines[idx].shape[1]

            L.WordSegment()

            Words = L.GetBinWords()
            WordsRGB = L.GetRGBWords()
            MFV = L.GetMFV()
            BaseIndex = L.GetBaseline()
            MTI = L.GetMTI()
            Height = L.GetHeight()

            Name = "Line_" + str(idx)

            os.mkdir(Path + "/" + Name)
            cv2.imwrite(Path + '/' + Name + '/' + Name + '.jpg', L.GetBinaryL())

            for i in range(len(Words)-1,-1,-1):

                # For Debugging
                if i == 4 and idx == 6:
                    print(1)
                W = Word(Words[i], WordsRGB[i], MTI, MFV, BaseIndex, Height)
                W.DetectCutPoints()
                W.FilterStroke()
                # W.FilterDal()
                Cuts = W.GetCuts()

                Chars = W.GetChars()

                self.Result.append(Chars)


                # for c in Chars:
                #     cv2.imshow('Test Image', c)
                #     cv2.waitKey(0)
                #     cv2.destroyAllWindows()

                # W.Display()

                for j in range(len(Cuts)):
                    WordsRGB[i] = cv2.rectangle(WordsRGB[i], (Cuts[j], 0), (Cuts[j], h), (0, 255, 0), 1)

                WordsRGB[i] = cv2.rectangle(WordsRGB[i], (0, MTI), (dim[0], MTI), (0, 255, 0), 1)
                WordsRGB[i] = cv2.rectangle(WordsRGB[i], (0, BaseIndex), (WordsRGB[i].shape[1], BaseIndex), (0, 255, 0),
                                            1)
                WordsRGB[i] = cv2.rectangle(WordsRGB[i], (0, Height), (WordsRGB[i].shape[1], Height), (0, 255, 0), 1)

                cv2.imwrite(Path + '/' + Name + '/word' + str(i) + '.jpg', WordsRGB[i])


    def GetSegmentedWords(self):
        return np.asarray(self.Result)