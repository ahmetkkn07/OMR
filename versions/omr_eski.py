from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2
# import argparse

minWidth = 20
minHeight = 20
minAr = 0.85
maxAr = 1.15


def getAnswers(img):
    ANSWERS = list()

    image = cv2.imread(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    #! RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    #! CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)
    docCnt = None

    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for cnt in cnts:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            if len(approx) == 4:
                docCnt = approx
                break

    warped = None

    if docCnt is not None:
        warped = four_point_transform(gray, docCnt.reshape(4, 2))
    else:
        warped = gray

    if warped.size < (image.size * 0.1):
        warped = gray

    # cv2.imshow("xxx", warped)

    thresh = cv2.threshold(warped, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)

    questionCnts = []

    for cnt in cnts:
        (x, y, w, h) = cv2.boundingRect(cnt)
        ar = w / float(h)

        if minWidth >= 20 and h >= minHeight and ar >= minAr and ar <= maxAr:
            questionCnts.append(cnt)

    questionCnts = contours.sort_contours(
        questionCnts, method="top-to-bottom")[0]

    correct = 0
    #! q --> 0,1,2,3,4 soru sayısı
    #! i --> 0,5,10,15,20 kutucuk sayısı
    for (qNum, i) in enumerate(np.arange(0, len(questionCnts), 5)):
        bubbledCount = 0

        cnts = contours.sort_contours(
            questionCnts[i:i + 5], method="left-to-right")[0]

        bubbled = None

        #! j --> indeks değerleri
        #! cnt --> her bir kutucuk
        for (j, cnt) in enumerate(cnts):

            msk = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(msk, [cnt], -1, 255, -1)
            msk = cv2.bitwise_and(thresh, thresh, mask=msk)
            total = cv2.countNonZero(msk)

            if bubbled is None or total > bubbled[0]:
                # if toplam > 400:
                bubbled = (total, j)
                bubbledCount += 1

        # if bubbledCount != 1:
            #! 5 boş şık olarak ayarlandı
            # ANSWERS.append(5)
        # else:
        ANSWERS.append(bubbled[1])

    return ANSWERS.copy()


def getScores(img, ANSWER_KEY):

    image = cv2.imread(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    #! RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    #! CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)
    docCnt = None

    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for cnt in cnts:
            peri = cv2.arcLength(cnt, True)

            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            if len(approx) == 4:
                # kağıdı ata
                docCnt = approx
                break

    warped = None
    if docCnt is not None:
        warped = four_point_transform(gray, docCnt.reshape(4, 2))
    else:
        warped = gray

    if warped.size < (image.size * 0.1):
        warped = gray

    thresh = cv2.threshold(warped, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)

    questionCnts = []

    for cnt in cnts:
        (x, y, w, h) = cv2.boundingRect(cnt)
        ar = w / float(h)

        if minWidth >= 20 and h >= minHeight and ar >= minAr and ar <= maxAr:
            questionCnts.append(cnt)

    questionCnts = contours.sort_contours(
        questionCnts, method="top-to-bottom")[0]

    correct = 0

    #! q --> 0,1,2,3,4 soru sayısı
    #! i --> 0,5,10,15,20 kutucuk sayısı
    for (qNum, i) in enumerate(np.arange(0, len(questionCnts), 5)):
        cnts = contours.sort_contours(
            questionCnts[i:i + 5], method="left-to-right")[0]

        bubbled = None

        #! j --> indeks değerleri
        #! cnt --> her bir kutucuk
        for (j, cnt) in enumerate(cnts):

            msk = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(msk, [cnt], -1, 255, -1)
            msk = cv2.bitwise_and(thresh, thresh, mask=msk)
            total = cv2.countNonZero(msk)

            if bubbled is None or total > bubbled[0]:
                bubbled = (total, j)

        answer = ANSWER_KEY[qNum]

        if answer == bubbled[1]:
            correct += 1

    puan = (correct / len(ANSWER_KEY)) * 100
    return "{: .2f}".format(puan)


# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
#                 help="path to the input image")
# args = vars(ap.parse_args())
# ans = getAnswers(args["image"])
# print(ans)
# print(getScores(args["image"], ans))
# cv2.waitKey(0)
