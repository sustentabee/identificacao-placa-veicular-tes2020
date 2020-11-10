import cv2
import numpy as np

frameWidth = 640
frameHeight = 480
nPlateCascade = cv2.CascadeClassifier("C:/Users/Lodi/Desktop/placa-transito-tes/haarcascade_russian_plate_number.xml")
minArea = 200
color = (255, 0, 255)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap.set(4, 150)
count = 0
execution = True
while execution:
    success, img = cap.read()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    numberPlates = nPlateCascade.detectMultiScale(img, 1.1, 15)
    for (x, y, w, h) in numberPlates:
        area = w * h
        if area > minArea:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
            cv2.putText(img, "Number Plate", (x, y - 5),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, color, 2)
            (thresh, imgPB) = cv2.threshold(img, 156, 255, cv2.THRESH_BINARY)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 2))
            imgPB = cv2.morphologyEx(imgPB, cv2.MORPH_OPEN, kernel)
            imgRoi = imgPB[y:y + h, x:x + w]
            cv2.imshow("ROI", imgRoi)
    cv2.imshow("Result", img)

    k = cv2.waitKey(30)
    if k == ord('s'):
        execution = False
        cv2.imwrite("C:/Users/Lodi/Desktop/placa-transito-tes/ocr/placa_pre_tratada.png", imgRoi)
        # read image
        img = cv2.imread("C:/Users/Lodi/Desktop/placa-transito-tes/ocr/placa_pre_tratada.png")
        hh, ww = img.shape[:2]

        img = img[3:hh-3, 3:ww-3]

        # pad 3 black pixels back all around plus another 10 all around as buffer for later morphology
        img = cv2.copyMakeBorder(img, 13,13,13,13, cv2.BORDER_CONSTANT, (0,0,0))

        # convert img to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # threshold
        thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY)[1]

        # apply morphology to remove small black spots
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        hh2, ww2 = thresh.shape[:2]

        # shave off 10 pixels all around
        thresh = thresh[10:hh2-10, 10:ww2-10]

        # get largest outer contour
        cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        big_contour = max(cnts, key=cv2.contourArea)

        # draw filled contour on black background
        mask = np.zeros_like(thresh)
        cv2.drawContours(mask, [big_contour], -1, (255), cv2.FILLED)

        # use mask to make outside of thresholded license into white
        # put white in result where mask is black
        result = thresh.copy()
        result[mask == 0] = 255

        # write results
        cv2.imwrite("C:/Users/Lodi/Desktop/placa-transito-tes/ocr/placa.png", result)

        cv2.waitKey(500)
        exec(open('C:/Users/Lodi/Desktop/placa-transito-tes/ocr/ocr.py').read())

cv2.destroyAllWindows()
