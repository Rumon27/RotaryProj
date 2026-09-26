import cv2 as cv 
import numpy as np 
import os 

root = os.getcwd()

imgPath = os.path.join(root, "images/varese.jpg")
img = cv.imread(imgPath)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

sift = cv.SIFT_create()
keypoints, descriptors = sift.detectAndCompute(gray, None)

cv.drawKeypoints(img, keypoints, img, (52, 163, 236), cv.DrawMatchesFlags_DRAW_RICH_KEYPOINTS)

cv.imshow("a", img)
cv.waitKey()
