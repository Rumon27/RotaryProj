import cv2 as cv 
import numpy as np 
import os 

root = os.getcwd()

imgPath = os.path.join(root, "images/varese.jpg")
img = cv.imread(imgPath)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

surf = cv.xfeatures2d.SURF_create(8000)

keypoints, descriptor = surf.detectAndCompute(gray, None)

cv.drawKeypoints(img, keypoints, img, (51, 164, 123), cv.DrawMatchesFlags_DRAW_RICH_KEYPOINTS)

cv.imshow("souf", img)
cv.waitKey()



