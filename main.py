from Segmentation import *

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

# arr= [1,2,3,4,56,7,4,3,2,42,41]
# blur = cv2.blur(arr,(5,5))

# exit(0)

TestNum = 1630
Img = cv2.imread('csep'+str(TestNum)+'.png')


S = Segmentation(Img)
S.Start()

# Words in a 2D-Array. Words is an array of Words, Each Word as an array of Characters
# Words and Characters are arranged from (Right-To-Left)
FileName = "csep"+str(TestNum)+".txt"
File = open(FileName,"r")
Lines = File.readlines()


RealWords = Lines[0].split(" ")
Words = S.GetSegmentedWords()

# exit(0)
Length = len(RealWords)

if Length != len(Words):
    print("Error in Words")
    print(len(Lines))
    print(Length)
    print(len(Words))
    exit(0)

Correct = 0
for i in range(Length):
    # print(RealWords[i])
    if WordLength(RealWords[i]) == len(Words[i]):
        Correct+=1

Accuracy = (Correct/Length)*100
print("Correct: " + str(Correct))
print("Errors: " + str(Length-Correct))
print("Accuracy: "+str(Accuracy))
# for w in Words:
#     for c in w:
#         cv2.imshow('Test Image', c)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()