from Segmentation import *

Img = cv2.imread('3.png')
S = Segmentation(Img)
S.Start()

# Words in a 2D-Array. Words is an array of Words, Each Word as an array of Characters
# Words and Characters are arranged from (Right-To-Left)
Words = S.GetSegmentedWords()

for w in Words:
    for c in w:
        cv2.imshow('Test Image', c)
        cv2.waitKey(0)
        cv2.destroyAllWindows()