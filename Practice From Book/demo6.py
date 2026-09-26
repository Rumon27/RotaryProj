import cv2 as cv 
import numpy as np
import matplotlib.pyplot as plt 
import os 

def grayHistogram():
     root = os.getcwd()
     imgpath = os.path.join(root, 'Images/kessa-cat-1647775_1920.jpg')
     img = cv.imread(imgpath, cv.IMREAD_GRAYSCALE)
     
     plt.figure()
     plt.imshow(img, cmap='gray')
     
     hist = cv.calcHist([img], [0], None, [256], [0,256])
     
     plt.figure()
     plt.plot(hist)
     plt.xlabel("bins")
     plt.ylabel("# of pixels")
     plt.show()
     
     
def colorHistogram():
     root = os.getcwd()
     imgpath = os.path.join(root, 'Images/kessa-cat-1647775_1920.jpg')
     img = cv.imread(imgpath)
     imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
     
     plt.figure()
     plt.imshow(imgRGB)

     colors = ['b', 'g', 'r']
     plt.figure()
     for i in range(len(colors)):
          hist = cv.calcHist([imgRGB], [i], None, [256], [0, 256])
          plt.plot(hist, colors[i])
     
     plt.xlabel('Pixel intensity')
     plt.ylabel("number of pixels")

     plt.show()
     
if __name__=="__main__":
     #grayHistogram()
     colorHistogram()