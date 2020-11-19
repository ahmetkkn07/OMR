from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2
import argparse
import math
import statistics as stats
import pytesseract
from pytesseract import image_to_string
from werkzeug.utils import secure_filename

gray = None

minWidth = 20
minHeight = 20
minAr = 0.8
maxAr = 1.2
darknessRate = 0.45

greenColor = (0, 255, 0)
redColor = (0, 0, 255)
blueColor = (255, 0, 0)

scoreLoc = (20, 20)

font = cv2.FONT_HERSHEY_SIMPLEX

pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'


def getAnswers(img):
    ANSWERS = list()
    image = cv2.imread(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    thresh = cv2.threshold(gray, 0, 255,
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
        radius = cv2.minEnclosingCircle(qCnt)[1]
        circleAreas.append(math.pi * radius * radius)

    meanCircleArea = stats.mean(circleAreas)

    for (qNum, i) in enumerate(np.arange(0, len(questionCnts), 5)):
        bubbledCount = 0

        cnts = contours.sort_contours(
            questionCnts[i:i + 5], method="left-to-right")[0]

        bubbled = None

        for (j, cnt) in enumerate(cnts):
            msk = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(msk, [cnt], -1, 255, -1)
            msk = cv2.bitwise_and(thresh, thresh, mask=msk)
            total = cv2.countNonZero(msk)

            if total > (meanCircleArea * 0.5):
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


def getScores(img, ANSWER_KEY, UPLOAD_FOLDER):
    image = cv2.imread(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)
    nameRect = None

    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for cnt in cnts:
            peri = cv2.arcLength(cnt, True)

            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            if len(approx) == 4:
                nameRect = approx
                break

    paper = image

    nameField = None
    if nameRect is not None:
        nameField = four_point_transform(gray, nameRect.reshape(4, 2))

    name = image_to_string(
        nameField, config="-c tessedit_char_whitelist='ABCDEFGHIJKLMNOPRSTUVYZabcdefghijklmnoprstuvyz '")
    # name = image_to_string(
    #     nameField, lang='tur')
    name = name[:-1]
    # print(name)
    thresh = cv2.threshold(gray, 0, 255,
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
    if len(questionCnts) % 5 != 0:
        raise Exception
    for qCnt in questionCnts:
        # minimum kapsayan dairenin yarıçapı
        radius = cv2.minEnclosingCircle(qCnt)[1]
        circleAreas.append(math.pi * radius * radius)

    meanCircleArea = stats.mean(circleAreas)

    correct = 0
    wrong = 0
    empty = 0

    for (qNum, i) in enumerate(np.arange(0, len(questionCnts), 5)):
        bubbledCount = 0
        cnts = contours.sort_contours(
            questionCnts[i:i + 5], method="left-to-right")[0]

        bubbled = None

        for (j, cnt) in enumerate(cnts):
            msk = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(msk, [cnt], -1, 255, -1)
            msk = cv2.bitwise_and(thresh, thresh, mask=msk)
            total = cv2.countNonZero(msk)

            if total > (meanCircleArea * darknessRate):
                bubbled = j
                bubbledCount += 1

        answer = ANSWER_KEY[qNum]
        color = None
        if bubbledCount == 1:
            if bubbled == answer:
                correct += 1
                color = greenColor
            else:
                wrong += 1
                color = redColor
        elif bubbledCount == 0:
            empty += 1
            color = blueColor
        else:
            wrong += 1
            color = redColor
        if answer <= 4:
            cv2.drawContours(paper, [cnts[answer]], -1, color, 3)

    constant = 100.0 / len(ANSWER_KEY)
    score = correct * constant

    scoreText = "Puan: {:.2f}".format(score)
    cv2.putText(paper, scoreText, scoreLoc, font, 0.9, redColor, 2)

    img = UPLOAD_FOLDER + "/" + secure_filename(name) + ".jpg"
    cv2.imwrite(img, paper)
    img = "/static" + \
        UPLOAD_FOLDER.split('static')[1] + \
        "/" + secure_filename(name) + ".jpg "

    return ["{: .2f}".format(score), name, img, correct, wrong, empty]
