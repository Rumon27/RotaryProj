import cv2 as cv 
import numpy as np 
import os 

root = os.getcwd()

imgPath = os.path.join(root, "images/hammer.jpg")
img = cv.pyrDown(cv.imread(imgPath, cv.IMREAD_UNCHANGED))

ret, thresh = cv.threshold(cv.cvtColor(img, cv.COLOR_BGR2GRAY), 127, 255, cv.THRESH_BINARY)

contours, hier = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

black = np.zeros_like(img)

for cnt in contours:
     epsilon = .01 * cv.arcLength(cnt, True)
     approx = cv.approxPolyDP(cnt, epsilon, True)
     
     hull = cv.convexHull(cnt)
     
     cv.drawContours(black, [cnt], -1, (0, 255, 0), 2)
     cv.drawContours(black, [approx], -1, (255, 0, 0), 2)
     cv.drawContours(black, [hull], -1, (0, 0, 255), 2)
     
cv.imshow("Pic", black)
cv.waitKey()
cv.destroyAllWindows()