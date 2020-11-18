from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2
import argparse
import math
import statistics as stats

minWidth = 20
minHeight = 20
minAr = 0.85
maxAr = 1.15
gray = None


def getAnswers(img):
    ANSWERS = list()

    image = cv2.imread(img)
    # image = cv2.resize(image, (400, 500), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # RETR_EXTERNAL: sadece en dıştaki kenarları almak için
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
    print("questionCnts: ", len(questionCnts))
    circleAreas = list()

    for qCnt in questionCnts:
        # minimum kapsayan dairenin yarıçapı
        radius = cv2.minEnclosingCircle(qCnt)[1]
        circleAreas.append(math.pi * radius * radius)

    meanCircleArea = stats.mean(circleAreas)

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
            #! bubbled[0] --> total        bubbled[1] --> answer
            if total > (meanCircleArea * 0.6):
                bubbled = j
                bubbledCount += 1

        if bubbledCount == 1:
            ANSWERS.append(bubbled)
        elif bubbledCount == 0:
            #! 5 boş
            ANSWERS.append(5)
        else:
            #! 6 birden çok cevap
            ANSWERS.append(6)

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
    paper = None
    if docCnt is not None:
        paper = four_point_transform(image, docCnt.reshape(4, 2))
        warped = four_point_transform(gray, docCnt.reshape(4, 2))
    else:
        paper = image
        warped = gray

    if warped.size < (image.size * 0.1):
        paper = image
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

    circleAreas = list()

    for qCnt in questionCnts:
        # minimum kapsayan dairenin yarıçapı
        radius = cv2.minEnclosingCircle(qCnt)[1]
        circleAreas.append(math.pi * radius * radius)

    meanCircleArea = stats.mean(circleAreas)

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

            # if bubbled is None or total > bubbled[0]:
            if total > (meanCircleArea * 0.6):
                bubbled = j
                bubbledCount += 1

        answer = ANSWER_KEY[qNum]
        color = None
        if bubbledCount == 1:
            if bubbled == answer:
                correct += 1
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
        elif bubbledCount == 0:
            color = (255, 0, 0)
        else:
            color = (0, 0, 255)
        cv2.drawContours(paper, [cnts[answer]], -1, color, 3)

    score = (correct / len(ANSWER_KEY)) * 100

    cv2.putText(paper, "{:.2f}%".format(score), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.imshow("Sonuç", paper)
    return "{: .2f}".format(score)


# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
#                 help="path to the input image")
# args = vars(ap.parse_args())
# ans = getAnswers(args["image"])
# print(ans)
# print(getScores(args["image"], ans))
# cv2.waitKey(0)
