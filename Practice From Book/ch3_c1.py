import cv2 as cv 
import numpy as np 
import os 

root = os.getcwd()

imgPath = os.path.join(root, "images/hammer.jpg")
img = cv.pyrDown(cv.imread(imgPath, cv.IMREAD_GRAYSCALE))

ret, thresh = cv.threshold(cv.cvtColor(img, cv.COLOR_BGR2GRAY), 127, 255, cv.THRESH_BINARY)

contours, hier = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

for c in contours:
     x,y,w,h = cv.boundingRect(c)
     cv.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

     rect = cv.minAreaRect(c)
     box = cv.boxPoints(rect)
     box = np.int32(box)
     cv.drawContours(img, [box], 0, (0, 0, 255), 3)
     
     (x, y), radius = cv.minEnclosingCircle(c)
     
     center = (int(x), int(y))
     radius = int(radius)

     img = cv.circle(img, center, radius, (0, 255, 0), 2)
     cv.drawContours(img, contours, -1, (255, 0 , 0), 5)
     
    

cv.imshow("Contours", img)
     
cv.waitKey()
cv.destroyAllWindows()
     

