import cv2 as cv 
import numpy as np
import matplotlib.pyplot as plt 
import os 

def convolution2d():
     root = os.getcwd()
     imgpath = os.path.join(root, 'Images/kessa-cat-1647775_1920.jpg')
     img = cv.imread(imgpath)
     imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)

     n = 20
     kernel = np.ones((n,n))/(n*n)
     
     imgFilter = cv.filter2D(imgRGB, -1, kernel)

     plt.figure()
     plt.subplot(121)
     plt.imshow(imgRGB)

     plt.subplot(122)
     plt.imshow(imgFilter)

     plt.show()

def callback():
     pass

def averageFilter():
     root = os.getcwd()
     imgpath = os.path.join(root, 'Images/kessa-cat-1647775_1920.jpg')
     img = cv.imread(imgpath)
     
     winName = "avgFilter"
     cv.namedWindow(winName)
     cv.createTrackbar('n', winName, 1, 100, callback)
     
     height, width, _ = img.shape
     
     scale = 1/4
     width = int(width*scale)
     height = int(height* scale)

     img = cv.resize(img, (width, height))

     while True:
          if cv.waitKey(1) == ord('q'):
               break
          
          n = cv.getTrackbarPos('n', winName)
          
          if n < 1:
               n = 1
          
          imgfilter = cv.blur(img, (n,n))
          cv.imshow(winName, imgfilter)
     

if __name__=="__main__":
     #convolution2d()
     averageFilter()