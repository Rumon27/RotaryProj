""" 
HPF is a filter that examines a region of an image and boosts
the intensity of certain pixels baseddd on the differecne in the
intensity of the surrounding pixels.
"""

import cv2 as cv 
import numpy as np 
from scipy import ndimage
import os 
root = os.getcwd()

kernel_3x3 = []
r3, c3 = 3, 3

for i in range(r3):
     row = []
     for j in range(c3):
          row.append(-1)
     kernel_3x3.append(row)
kernel_3x3[1][1] = 8

kernel_5x5 = []
r5, c5 = 5, 5

for i in range(r5):
     row = []
     for j in range(c5):
          if(i == 0 or i == 4 or j == 0 or j == 4):
               row.append(-1)
          elif (i + j) == 4 and i==j:
               row.append(4)
          elif((i + j) in (2, 4, 6)):
               row.append(1)
          elif((i+j) in (3, 5)):
               row.append(2)
     kernel_5x5.append(row)

impath = os.path.join(root, "images/statue_small.jpg")
img = cv.imread(impath, cv.IMREAD_GRAYSCALE)

cv.imshow("img", img)
blurred = cv.GaussianBlur(img, (17,17), 0)

k3 = ndimage.convolve(blurred, kernel_3x3)
k5 = ndimage.convolve(blurred, kernel_5x5)

g_hpf = img - blurred

cv.imshow("3x3", k3)
cv.imshow("5x5", k5)
cv.imshow("bl4", blurred)
cv.imshow("hpf", g_hpf)


cv.waitKey()
cv.destroyAllWindows()