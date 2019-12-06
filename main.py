import numpy as np
import cv2
import os

import math
import matplotlib.pyplot as plt
import skimage.morphology
from skimage import img_as_ubyte

from skimage.morphology import binary_erosion, binary_dilation, binary_closing, skeletonize, thin


# Gaps are whether Gaps between words OR Gaps within sub-word
# removing sub-word Gaps
def FilterGaps(G, L):
    G = np.array(G)
    L = np.array(L)

    IQR = 2

    # Filtering Depending On IQR ( Interquartile Range ) Value
    G = G[L >= IQR]
    L = L[L >= IQR]

    Mean = np.mean(L)
    G = G[L >= Mean]
    L = L[L >= Mean]

    return G, L


def FindGaps(Line):
    G = []
    L = []

    # Vertical Projection Of the text
    VP = np.sum(Line, axis=0)
    VP2 = VP[VP != 0].astype(np.int64)
    MFV = np.bincount(VP2).argmax()
    # print(VP2)
    # print(MFV)
    flag = 0
    for i in range(len(VP)):

        if VP[i] == 0:
            if flag == 0:
                # This is a Gap Start
                G.append(i)
                L.append(1)
                flag = 1
            else:
                # Increment Gap Length
                L[-1] += 1


        elif flag == 1:
            # End of The Gap
            flag = 0

    return G, L, MFV


def WordSegment(Line, LineRGB):
    # G => Array of Gaps, L => Length of each gap
    G, L, MFV = FindGaps(Line)
    G, L = FilterGaps(G, L)

    # Separete Each Word in a single Image
    Words = [Line[0:, G[i] + L[i]:G[i + 1]] for i in range(len(G) - 1)]
    WordsRGB = [LineRGB[0:, G[i] + L[i]:G[i + 1]] for i in range(len(G) - 1)]

    return Words, MFV, WordsRGB


def ToBinaryImg(Img):
    ImgGray = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)
    BinaryImg = np.array(ImgGray)
    BinaryImg[ImgGray > 127] = 0
    BinaryImg[ImgGray <= 127] = 255

    # cv2.imshow('Gray Image', ImgGray)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # cv2.imshow('Binary Image', BinaryImg)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return BinaryImg


def MaxTrans(Line, Baseline):
    MTI = 0
    MaxVal = 0

    for i in range(0, Baseline):
        Trans = 0
        for k in range(1, len(Line[i])):
            if Line[i][k] != Line[i][k - 1]:
                Trans += 1
        if Trans > MaxVal:
            MaxVal = Trans
            MTI = i

    MTIidx = []

    # Flag = 0
    # for k in range(1, len(Line[MTI]) ):
    #    if Flag == 0 and Line[MTI][k] == 1 and Line[MTI][k] == 0 :
    #        MTIidx.append(k)
    #        Flag = 1
    #    elif Flag == 1
    print(MaxVal)
    return MTI - 1, np.array(MTIidx)


def DetectBaseline(Line):
    ThinnedImg = skimage.morphology.thin(Line)
    ThinnedImg = img_as_ubyte(ThinnedImg)

    HP = ThinnedImg

    Baseline = np.array(np.sum(ThinnedImg, axis=1))
    BaseIndex = np.argmax(Baseline)

    return BaseIndex


def IsPath(Word, Start, End):
    Mat = Word[:, End   :Start+1].copy()
    dim = Mat.shape
    rows = dim[0]
    cols = dim[1]
    IsReachable = np.zeros((rows, cols))

    for i in range(1, rows):
        if Mat[i][0] != 0 :
            IsReachable[i][0] = 1

    #for j in range(1, cols):
    #    if Mat[0][j] != 0 and IsReachable[0][j] != 0:
    #        IsReachable[0][j] = 1

    for i in range(1, rows):
        for j in range(1, cols):
            if Mat[i][j] != 0:
                IsReachable[i][j] = IsReachable[i - 1][j] or IsReachable[i][j - 1] or IsReachable[i-1][j - 1]

    if np.sum(IsReachable[:, -1]) != 0:
        return True
    return False


def IsValidCut(Word, Start, End, Cut, MFV):
    if np.sum(Word[:, Cut]) == 0:
        return True
    elif not IsPath(Word, Start, End):
        return True


def DetectCutPoints(Word, MTI, MFV):
    Flag = 0
    cv2.imshow('Test Image', Word)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(Word.shape)

    End = Start = -1
    Regions = []
    IsStart = False
    for i in range(len(Word[MTI]) - 2, 0, -1):
        if Word[MTI][i] == 0 and Word[MTI][i+1] != 0:
            Start = i
            IsStart = True
        if Word[MTI][i] != 0 and Word[MTI][i+1] == 0 and IsStart:

            End = i
            Mid = (End + Start) // 2
            IsStart = False
        #if Flag == 0 and Word[MTI][i] != 0:
        #    End = i
        #    Flag = 1
        #elif Flag == 1 and Word[MTI][i] == 0:
        #    Start = i
        #    Mid = (End + Start) // 2
            Cut = -1
            for j in range(End, Start + 1):
                if np.sum(Word[:, j]) == 0:
                    Cut = j
                    break
            # VP = np.sum(Word[:,End:Start + 1], axis=0)

            if Cut != -1:
                Cut = Cut

            elif np.sum(Word[:, Mid]) == MFV:
                Cut = Mid

            else:
                Cut = -1
                for j in range(End, Mid + 1):
                    if np.sum(Word[:, j]) <= MFV:
                        Cut = j

                if Cut != -1:
                    Cut = Cut
                else:
                    Cut = -1
                    for j in range(Mid, Start + 1):
                        if np.sum(Word[:, j]) <= MFV:
                            Cut = j
                            break

                    if Cut != -1:
                        Cut = Cut
                    else:
                        Cut = Mid


            if IsValidCut(Word, Start, End, Cut, MFV):
                pass
            Regions.append(Cut)
            Flag = 0
        # print(Regions)

    return Regions


arr = np.zeros((2, 3))
x = arr.shape
Img = cv2.imread('3.png')
dim = Img.shape
BinaryImg = ToBinaryImg(Img)

# Segment Words
Words, MFV, WordsRGB = WordSegment(BinaryImg, Img)

# Baseline and Max transitions
BaseIndex = DetectBaseline(Words[-1])
MTI, _ = MaxTrans(Words[-1], BaseIndex)
Cuts = DetectCutPoints(Words[-1], MTI, MFV)

# NewCuts = FilterCuts(Words[-1], MFV, Cuts)

cv2.imwrite('word1.jpg', Words[-1])

# Cuts = Test(Words[0],BaseIndex,MFV)
for i in range(len(Cuts)):
    WordsRGB[-1] = cv2.rectangle(WordsRGB[-1], (Cuts[i], 0), (Cuts[i], dim[1]), (0, 255, 0), 1)
WordsRGB[-1] = cv2.rectangle(WordsRGB[-1], (0, MTI), (dim[0], MTI), (0, 255, 0), 1)
WordsRGB[-1] = cv2.rectangle(WordsRGB[-1], (0, BaseIndex), (dim[0], BaseIndex), (0, 255, 0), 1)

cv2.imwrite('res2.jpg', WordsRGB[-1])
cv2.imshow('BaseLine', WordsRGB[-1])
cv2.waitKey(0)
cv2.destroyAllWindows()
