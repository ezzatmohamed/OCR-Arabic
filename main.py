from Segmentation import *

Dict = { "ا":0,"ب":1,"ت":2,"ث":3,"ج":4,"ح":5,"خ":6,"د":7,"ذ":8,"ر":9,"ز":10,"س":11,"ش":12,"ص":13,"ض":14,"ط":15,"ظ":16,"ع":17,"غ":18,"ف":19,"ق":20,"ك":21,"ل":22,"م":23,"ن":24,"و":25,"ه":26,"ي":27,"لا":29 }


def Skew(Img):
    gray = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    # threshold the image, setting all foreground pixels to
    # 255 and all background pixels to 0
    thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)

    # otherwise, just take the inverse of the angle to make
    # it positive
    else:
        angle = -angle

    (h, w) = Img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(Img, M, (w, h),flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def WordLength(W):
    count = 1
    for i in range(len(W)-1):
        if W[i]+W[i+1] != "لا":
            count+=1
    return count    

def Train(NumberOfData):


    ImgCount = 0

    AllLength = 0
    AllCorrect = 0
    count = 0
    WrongImgs=0

    try:
        shutil.rmtree("train")
    except:
        print("No train folder")

    os.mkdir("train")

    File = open("associtations.txt","w")
    # exit(0)
    for scanned in os.listdir('dataset/scanned2'):

        Path = 'dataset/scanned2/'+scanned
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

        FileName = 'dataset/text2/'+scanned[:-4] +'.txt'
        print(FileName)

        File = open(FileName, "r")
        Lines = File.readlines()
        RealWords = Lines[0].split(" ")
        Words = S.GetSegmentedWords()

        # Words2 = S2.GetSegmentedWords()

        Length = len(RealWords)
        print("================================")
        print(Length)
        print(len(Words))
        # print(len(Words2))
        print("================================")

        if Length != len(Words):
            print("Error in Words")
            print("Number Of True Words: "+str(Length))
            print("Number of Words: " + str(len(Words)))
            WrongImgs +=1
            continue

        File = open("associtations.txt", "a")
        Correct = 0
        for i in range(Length):
            WL = len(Words[i])
            if WordLength(RealWords[i]) == WL :
                Correct += 1
                for j in range(WL):
                    name = str(ImgCount)+".png"
                    cv2.imwrite("train/"+name,Words[i][j])
                    File.write(str(Dict[RealWords[i][j]])+" " + name+"\n" )
                    ImgCount+=1

        AllLength += Length
        AllCorrect += Correct

        count += 1
        if count == NumberOfData:
            break

    File.close()
    AllAccuracy = (AllCorrect / AllLength) * 100
    print("Segmentation Finished")
    print(str(WrongImgs) + " Failed Images")
    print("Testing on " + str(AllLength) + " Words ")
    print(str(AllCorrect) + " Are Correct")
    print("Accuracy : "+str(AllAccuracy) +"%")


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
Train(20)