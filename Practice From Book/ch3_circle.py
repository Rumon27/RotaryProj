import cv2 as cv 
import numpy as np 
import os 

root = os.getcwd()

imgpath = os.path.join(root, "images/planet_glow.jpg")
img = cv.imread(imgpath)

grayImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
grayImg = cv.GaussianBlur(grayImg, ksize=(3,3), sigmaX=cv.BORDER_DEFAULT)
#grayImg = cv.medianBlur(grayImg, 5)



circles = cv.HoughCircles(grayImg, cv.HOUGH_GRADIENT, 1, 120, 
                          param1=100, param2=30, minRadius=0, maxRadius=0)

circles = np.uint16(np.round(circles))

print(circles)
print(circles[0, :])

for i in circles[0, :]:
     cv.circle(img, (i[0], i[1]), i[2], (0, 255, 100), 2)
     cv.circle(img, (i[0], i[1]), 2, (0,0, 255), 3)

cv.imwrite("planets_circle.jpg", img)
cv.imshow("Houghcircle", img)
cv.waitKey()
cv.destroyAllWindows()