import cv2 as cv 
import numpy as np 
from scipy import ndimage
import os 
root = os.getcwd()

impath = os.path.join(root, "images/statue_small.jpg")
img = cv.imread(impath)

canny_img = cv.Canny(img, 200, 300)
cv.imshow("canny ", canny_img)
cv.waitKey()
cv.destroyAllWindows()