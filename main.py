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

Img = cv2.imread('109.png')

# rotated = Skew(Img)
# cv2.imshow('Test Image', Img)
# cv2.imshow('rotated Image', rotated)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

S = Segmentation(Img)
S.Start()

# Words in a 2D-Array. Words is an array of Words, Each Word as an array of Characters
# Words and Characters are arranged from (Right-To-Left)
Words = S.GetSegmentedWords()

# for w in Words:
#     for c in w:
#         cv2.imshow('Test Image', c)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()