import cv2 as cv 
import numpy as np
import matplotlib.pyplot as plt 
import os 


def suduku():
     root = os.getcwd()
     imgsrc = os.path.join(root, 'Images/sudoku.png')
     img = cv.imread(imgsrc)
     imgg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
     
     maxval = 255
     thresholds = [-10, -5, 0, 5, 10, 15, 20, 25, 30]
     
     thres_img = []
     
     for i in thresholds:
          parts = cv.adaptiveThreshold(imgg, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 31, i)
          thres_img.append(parts)
          
     plt.figure()
     for i in range(0, len(thres_img)):
          plt.subplot(3,3,i+1)
          plt.imshow(thres_img[i], cmap='gray')
     
     plt.tight_layout()
     plt.show()
               
# def suduku2():
#      root = os.getcwd()
#      imgsrc = os.path.join(root, 'Images/sudoku.png')
#      img = cv.imread(imgsrc)
#      imgg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
     
#      maxval = 255
#      thresholds = [-10, -5, 0, 5, 10, 15, 20, 25, 30]
     
#      thres_img = []
     
#      for i in thresholds:
#           parts = cv.adaptiveThreshold(imgg, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 31, i)
#           thres_img.append(parts)
          
#      plt.figure()
#      for i in range(0, len(thres_img)):
#           plt.subplot(3,3,i+1)
#           plt.imshow(thres_img[i], cmap='gray')
     
#      plt.tight_layout()
#      plt.show()
               
     
 
if __name__=="__main__":
     #grayscaleMap()
     suduku()
     #suduku2()