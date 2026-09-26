import cv2 as cv 
import numpy as np
import matplotlib.pyplot as plt 
import os 



def grayscaleMap():
     gradient = np.linspace(0, 255, 256, dtype=np.uint8).reshape(1,-1)

     height = 50
     gradient_img = np.repeat(gradient, height, axis=0)

     thresholds = [0,50, 100, 150, 200, 250]
     max_val = 255

     thres_imgs = []

     for i in thresholds:
          _, binary = cv.threshold(gradient_img, i, max_val, cv.THRESH_TOZERO)
          thres_imgs.append(binary)


     plt.figure(figsize=(12, 6))
     plt.subplot(7,1,1)
     plt.imshow(gradient_img)

     for i in range(1, len(thres_imgs)):
          plt.subplot(7, 1, i)
          plt.imshow(thres_imgs[i], cmap='gray')

     plt.tight_layout()
     plt.show()
     

def suduku():
     root = os.getcwd()
     imgsrc = os.path.join(root, 'Images/sudoku.png')
     img = cv.imread(imgsrc)
     imgg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
     
     maxval = 255
     thresholds = [0, 60, 70, 80, 90, 100, 110, 120, 130]
     
     thres_img = []
     
     for i in thresholds:
          _, parts = cv.threshold(imgg, i, maxval, cv.THRESH_BINARY)
          thres_img.append(parts)
          
     plt.figure()
     for i in range(0, len(thres_img)):
          plt.subplot(3,3,i+1)
          plt.imshow(thres_img[i], cmap='gray')
     
     plt.tight_layout()
     plt.show()
               
               
     
 
if __name__=="__main__":
     #grayscaleMap()
     suduku()