from __future__ import division
import serial # leitura da saida da COM
import time # delay de conexão
import os # verificar se o script está rodando em um windows
import msvcrt # input original do windows
import cv2
import numpy as np
from PIL import Image, ImageDraw
from operator import itemgetter
import sys


def ocr():
    white = (255, 255, 255)

    letters = []

    # Delimit the area around the Characters
    def getBoxes(image, rgbImage):
  
        width, height = image.size

        boxes = []
        whiteLine = True
        readingChar = False
  
        charStartX = 0
        charEndX = 0

        # Start reading the image
        for x in range(0, width):

            # Read one vertical line  
            for y in range(0, height):
                if rgbImage.getpixel((x, y)) != white:
                    whiteLine = False
                    break;
                whiteLine = True

            if whiteLine == False:
                if readingChar == False:
                    charStartX = x
                    readingChar = True
            else:
                if readingChar == True:
                    charEndX = x
                    readingChar = False

                    # Get the box height
                    charStartY, charEndY = getBoxHeight(rgbImage, width, height, charStartX, charEndX)
                    boxes.append((charStartX, charEndX, charStartY, charEndY))

        return boxes

    # Get the height of the character box
    def getBoxHeight(rgbImage, width, height, charStartX, charEndX):

        whiteLine = True
        readingChar = False

        charStartY = 0
        charEndY = 0

        for y in range(0, height):
            for x in range(charStartX, charEndX):
                if rgbImage.getpixel((x, y)) != white:
                    whiteLine = False
                    break;
                whiteLine = True

            if whiteLine == False:
                if readingChar == False:
                    charStartY = y
                    readingChar = True
            else:
                if readingChar == True:
                    charEndY = y
                    readingChar = False

        return (charStartY, charEndY)

    # Read white spaces
    def getSpaces(image, rbgImage):

        width, height = image.size

        spaces = []
        whiteLine = True
        readingSpace = False
    
        spaceStartX = 0
        spaceEndX = 0

        # Start reading image
        for x in range(0, width):

        # Read one vertical line  
            for y in range(0, height):
                if rgbImage.getpixel((x, y)) != white:
                    whiteLine = False
                    break;
                whiteLine = True

            if whiteLine == False:
                if readingSpace == True:
                    spaceEndX = x
                    readingSpace = False
                    spaces.append((spaceStartX, spaceEndX))
            else:
                if readingSpace == False:
                    spaceStartX = x
                    readingSpace = True

        return spaces

    # Get the spaces read and insert them in the box list
    def mergeSpacesIntoBoxes(boxes, spaces, imageHeight):

        # Identify and add the Spaces. Avg may not be a good method
        s = 0
        for space in spaces:
            s = s + (space[1] - space[0])

        average = s / len(spaces)
        spaceInBoxes = []
        for space in spaces:
            if space[1] - space[0] > average + 1:
                spaceInBoxes.append((space[0], space[1], 0, imageHeight))

        boxes = boxes + spaceInBoxes
        boxes = sorted(boxes, key=itemgetter(0))

        return boxes

    # Run a XNOR in the read box matrix against the trained matrix
    def xnor(box, matrix):

        # Compare it against each character in the trained matrix
        results = []
        for character in matrix:
        
            # Check if the boxes are the same size
            letter = character[0]
            width = character[1]
            height = character[2]
            positives = 0

            # If the box read is too big, we scale it down to match the trained box
            subImage = rgbImage.crop((box[0], box[2], box[1], box[3]))
            boxWidth, boxHeight = subImage.size
            trainedWidth, trainedHeight = (int(character[1]), int(character[2]))
            
            if boxWidth > trainedWidth and boxHeight > trainedHeight:
                subImage = subImage.resize((trainedWidth, trainedHeight), Image.NEAREST)
                boxWidth, boxHeight = subImage.size
        
            # Read this character's matrix
            boxMatrix = []
            for y in range(0, boxHeight):
                for x in range(0, boxWidth):
                    if subImage.getpixel((x, y)) == white:
                        boxMatrix.append("0")
                    else:
                        boxMatrix.append("1")

            boxSize = boxWidth * boxHeight
            trainedSize = trainedWidth * trainedHeight
            size = 0
            if boxSize < trainedSize:
                size = boxSize
            else:
                size = trainedSize

            # XNOR
            for i in range(0, size):
                if character[i + 3] == boxMatrix[i]:
                    positives = positives + 1

            if size == 0:
                size = 1
            ratio = positives / size
            
            if all(item == "0" for item in boxMatrix): # Check if space
                results.append((" ", 0))
            elif positives > 0: # A character!
                results.append((letter, ratio))

        results = sorted(results, key=itemgetter(1), reverse=True)

        # Print the results
        if results[0][1] == 0:
            print(" ")
        else:
            letters.append(str(results[0][0]))
            # print(str(results[0][0]) + " - " + str(results[0][1] * 100) + "% sure")

        return results

    # Open the trained OCR table
    def readOCRMatrix(fontName):

        f = open("C:/Users/Lodi/Desktop/placa-transito-tes/ocr/" + fontName + ".ocr", "r")
        content = f.read()

        matrix = []
        
        for line in content.split("\n"):
            lineSplit = line.split(",")
            if len(lineSplit) == 1:
                break;

            matrix.append((lineSplit))

        f.close()
        return matrix

    filename = "C:/Users/Lodi/Desktop/placa-transito-tes/ocr/placa.png"

    # Open the image to be read
    fontName = "mandator"
    image = Image.open(filename)
    rgbImage = image.convert("RGB")

    width, height = image.size

    # Read the trained ocr table
    matrix = readOCRMatrix(fontName)

    # Get the boxes
    boxes = getBoxes(image, rgbImage)
    spaces = getSpaces(image, rgbImage)
    boxes = mergeSpacesIntoBoxes(boxes, spaces, height)

    # Read the image and try to identify the Characters
    for box in boxes:
        result = xnor(box, matrix)

    return letters


def identficador_placas_veiculares():
    placas_cadastradas = [["G", "T", "J", "6", "6", "9", "9"]]

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
            lista_letras_identificadas = ocr()
            if "." in lista_letras_identificadas:
                lista_letras_identificadas.remove(".")
            for placa in placas_cadastradas:
                sum = 0
                quantidade_caracteres = len(lista_letras_identificadas)
                if len(placa) < quantidade_caracteres:
                    quantidade_caracters = len(placa)
                for i in range(0, quantidade_caracteres-1):
                    if lista_letras_identificadas[i] == placa[i]:
                        sum = sum + 1

                print(lista_letras_identificadas)
                print(placa)
                print(sum)

                if sum > 4:
                    conexao.write(b'V')
                else:
                    conexao.write(b'F')

                

    cv2.destroyAllWindows()


conexao = serial.Serial('COM3', 9600) # configuração da conexão
time.sleep(1.8) # delay de conexão

while(True):
    identficador_placas_veiculares()

conexao.write(b'X') # fim da conexão do lado do arduino
conexao.close() # fim da conexão do lado do python