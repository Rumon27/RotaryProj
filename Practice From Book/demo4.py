import cv2 as cv
import numpy as np 
import matplotlib.pyplot as plt
import os
import time

root = os.getcwd()
imgPath = os.path.join(root, "Images/images.jpg")
img = cv.imread(imgPath)

def pureColors():
     zeros = np.zeros((100, 100))
     ones = np.ones((100 , 100))

     matImg = cv.merge((zeros, zeros, 255 * ones))
     cvImg = cv.merge((zeros, zeros, 255 * ones))

     plt.figure()
     plt.subplot(1,1,1)
     plt.imshow(matImg, vmin=0, vmax=50)
     plt.title("matplotlib")
     
     cv.imshow("image", cvImg)
     cv.waitKey(0)
     cv.destroyAllWindows()
     plt.show()

def bgrChannelGrayScale():
     
     
     if img is None:
          print("No Image found")
          return
     
     b,g,r = cv.split(img)

     zeros = np.zeros_like(b)
     
     b = cv.merge((b, zeros, zeros))
     g = cv.merge((zeros, g, zeros))
     r = cv.merge((zeros, zeros, r))
     
     cv.imshow("image", b)
     cv.waitKey(0)
     cv.destroyAllWindows()
     cv.imshow("image", g)
     cv.waitKey(0)
     cv.destroyAllWindows()
     cv.imshow("image", r)
     cv.waitKey(0)
     cv.destroyAllWindows()
     
     
def greyScale():
     imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
     cv.imshow('gray', imgGray)
     cv.waitKey(0)
     cv.destroyAllWindows()

def readAsgray():
     img = cv.imread(imgPath, cv.IMREAD_GRAYSCALE)
     cv.imshow('gray2', img)
     cv.waitKey(0)
     cv.destroyAllWindows()

if __name__=="__main__":
     #pureColors()
     #bgrChannelGrayScale()
     greyScale()
     time.sleep(1)
     readAsgray()
     