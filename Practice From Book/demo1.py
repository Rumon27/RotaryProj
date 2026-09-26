import cv2 as cv 
import matplotlib.pyplot as plt 
import os 
import numpy as np 

def readImage():
     root = os.getcwd()
     imgPath = os.path.join(root, 'Images/images (1).jpg')
     img = cv.imread(imgPath)
     debug = 1
     cv.imshow('img', img)
     cv.waitKey(0)
     
def writeImage():
     root = os.getcwd()
     imgPath = os.path.join(root, 'Images/images (1).jpg')
     img = cv.imread(imgPath)
     outpath = os.path.join(root, 'Images/notun.jpg')
     cv.imwrite(outpath, img)
     
if __name__ == '__main__':
     #readImage()
     writeImage()