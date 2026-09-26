import cv2 as cv 
import numpy as np 
import os 

root = os.getcwd()

imgPath = os.path.join(root, "images/chess_board.png")
img = cv.imread(imgPath)

grayImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

dst = cv.cornerHarris(grayImg, 2, 3, 0.04)

img[dst > 0.01 * dst.max()] = [0, 0, 255]

cv.imshow("corners", img)
cv.waitKey()