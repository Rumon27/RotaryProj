import cv2 as cv
import numpy as np 
import matplotlib.pyplot as plt
import os
import time

def hsvColorSegmentation():
     root = os.getcwd()
     imgPath = os.path.join(root, "Images/images.jpg")
     img = cv.imread(imgPath)
     
     imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
     hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
     
     lowerBound = np.array([0,0,50])
     upperBound = np.array([10, 120, 100])

     mask = cv.inRange(hsv, lowerBound, upperBound)
     
     cv.imshow("HSV masked", mask)
     cv.waitKey(0)

if __name__=="__main__":
     hsvColorSegmentation()
     
     