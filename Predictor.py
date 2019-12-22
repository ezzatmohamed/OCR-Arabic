from sklearn import svm
import pickle
import time
import cv2
import numpy as np
from sklearn.neural_network import MLPClassifier
from FeatureExtraction import *
from Segmentation import *

Dict = {"ا": 0, "ب": 1, "ت": 2, "ث": 3, "ج": 4, "ح": 5, "خ": 6, "د": 7, "ذ": 8, "ر": 9, "ز": 10, "س": 11, "ش": 12,
        "ص": 13, "ض": 14, "ط": 15, "ظ": 16, "ع": 17, "غ": 18, "ف": 19, "ق": 20, "ك": 21, "ل": 22, "م": 23, "ن": 24,
        "و": 25, "ه": 26, "ي": 27, "لا": 29}
invDict = {0: "ا", 1: "ب", 2: "ت", 3: "ث", 4: "ج", 5: "ح", 6: "خ", 7: "د", 8: "ذ", 9: "ر", 10: "ز", 11: "س", 12: "ش",
           13: "ص", 14: "ض", 15: "ط", 16: "ظ", 17: "ع", 18: "غ", 19: "ف", 20: "ق", 21: "ك", 22: "ل", 23: "م", 24: "ن",
           25: "و", 26: "ه", 27: "ي", 29: "لا"}


def WordLength(W):
    count = 1
    for i in range(len(W) - 1):
        if W[i] + W[i + 1] != "لا":
            count += 1
    return count





def Segment(NumberOfData):
    ImgCount = 0

    AllLength = 0
    AllCorrect = 0
    count = 0
    WrongImgs = 0

    for scanned in os.listdir('dataset/scannedTest'):

        Path = 'dataset/scannedTest/' + scanned
        # Path2 = 'dataset/scanned2/'+scanned
        print(Path)
        Img = cv2.imread(Path)
        # Img2 = cv2.imread(Path2)

        S = Segmentation(Img)
        # S2 = Segmentation(Img2)
        try:
            S.Start()
            # S2.Start()
        except:
            print("Error in reading image")
            continue

        Words = S.GetSegmentedWords()
        # Words2 = S2.GetSegmentedWords()

        for i in range(len(Words)):
            WL = len(Words[i])

            for j in range(WL):
                name = str(ImgCount) + ".png"
                cv2.imwrite("trainTest/" + name, Words[i][j])
                ImgCount += 1

        # AllLength += Length
        # AllCorrect += Correct

        count += 1
        if count == NumberOfData:
            break

    # File.close()
    # AllAccuracy = (AllCorrect / AllLength) * 100
    # print("Segmentation Finished")
    # print(str(WrongImgs) + " Failed Images")
    # print("Testing on " + str(AllLength) + " Words ")
    # print(str(AllCorrect) + " Are Correct")
    # print("Accuracy : " + str(AllAccuracy) + "%")
    return Words

#
#
# Path = 'dataset/scanned2/capr6.png'
# Img = cv2.imread(Path)
# S = Segmentation(Img)
# try:
#     S.Start()
# except:
#     print("Error in reading image")
#
#
# FileName = 'dataset/text/capr6.txt'
#
# File = open(FileName, "r")
# Lines = File.readlines()
# RealWords = Lines[0].split(" ")
# Words = S.GetSegmentedWords()
#
# Length = len(RealWords)
# print("================================")
# print(Length)
# print(len(Words))
# print("================================")
def Test(Img):
    S = Segmentation(Img)
    S.Start()
    Words = S.GetSegmentedWords()
    Length = len(Words)
    ImgCount=0
    for i in range(Length):
        WL = len(Words[i])
        for j in range(WL):
            name = str(ImgCount) + ".png"
            cv2.imwrite("Test/" + name, Words[i][j])
            ImgCount += 1

    return ImgCount

def predict(ImgCount):
    fi = open('Classifier', 'rb')
    clf = pickle.load(fi)
    fi.close()

    features = []
    for i in range(ImgCount):
        Path = 'Test/' + str(i) + '.png'
        print(Path)
        Img = cv2.imread(Path)
        Img = cv2.resize(Img, (50, 50))
        features.append(extract_features(Img))

    print(clf)
    for i in range(len(features)):
        for j in range(len(features[i])):
            features[i][j]=float(features[i][j])
    prediction = clf.predict(features)
    # print(prediction)
    return prediction



File = open("output.txt", "r")
Lines = File.readlines()
PredWords = Lines[0].split(" ")
Length= len(PredWords)
File.close()

File = open("test.txt", "r")
Lines = File.readlines()
RealWords = Lines[0].split(" ")
Length2= len(RealWords)

print(Length)
print(Length2)

Correct = 0
for i in range(Length):
    if PredWords[i]== RealWords[i]:
        Correct+=1
        # print(PredWords[i] + " " + RealWords[i])

print("Accuracy: "+ str((Correct/Length)*100))






#
# wordsNum=Segment(1)
# length=[]
# for i in wordsNum:
#     length.append(len(i))
# print("peeee",length)
#
#
# Img = cv2.imread("capr39.png")
# ImgCount = Test(Img)
# pred=predict(ImgCount)
# w=open("output.txt","w",encoding="utf-8")
# c=0
# acc=length[c]
# k=0
# for i in pred:
#     if c<len(length)-1:
#         if k == acc:
#             w.write(" ")
#             c += 1
#             acc+=length[c]
#
#
#     w.write(invDict[i])
#     k+=1
#
#
# w.close()
