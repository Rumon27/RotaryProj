import cv2 as cv 
import numpy as np 
import os 
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt 


def readAndWritePixel():
     root = os.getcwd()
     imgpath = os.path.join(root, 'Images/images (1).jpg')
     img = cv.imread(imgpath)
     imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
     
          
     eyepixel = imgRGB[255, 92]
     imgRGB[92, 255] = (255, 0, 0)
     
     plt.figure()
     plt.imshow(imgRGB)
     plt.show(block=True)

def readAndWritePixelRegion():
     root = os.getcwd()
     imgpath = os.path.join(root, 'Images/images (1).jpg')
     img = cv.imread(imgpath)
     imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
     
     
     eyeRegion = imgRGB[82:98, 243:268]
     
     dx = 98-82
     dy = 268 - 243
     
     starty = 266
     startx = 60
     
     imgRGB[startx:startx+dx, starty:starty+dy] = eyeRegion
     
     plt.figure()
     plt.imshow(imgRGB)
     plt.show(block=True)


if __name__ == '__main__':
     #readAndWritePixel()
     readAndWritePixelRegion()
     

