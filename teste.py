import cv2
import numpy as np

# read image
img = cv2.imread("plate2.png")
hh, ww = img.shape[:2]

# shave off 3 pixels all around to remove outer white border
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
cv2.imwrite("license2_thresh.png", thresh)
cv2.imwrite("license2_mask.png", mask)
cv2.imwrite("license2_result.png", result)

# display it
cv2.imshow("thresh", thresh)
cv2.imshow("mask", mask)
cv2.imshow("result", result)
cv2.waitKey(0)