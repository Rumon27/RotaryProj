import cv2 as cv 
import os 
import numpy as np 

# randomBytes = bytearray(os.urandom(120000))
# flatnumpyArray = np.array(randomBytes)

# grayimg = flatnumpyArray.reshape(300, 400)
# cv.imwrite("Random.png", grayimg)

# bgrimg = flatnumpyArray.reshape(100, 400, 3)
# cv.imwrite("RandomColor.png", bgrimg)

root = os.getcwd()
impath = os.path.join(root, 'images/car.jpg')

img = cv.imread(impath)
img[0:100,0:100] = [244,244,255]

cv.imshow('img', img)

cv.waitKey(0)

print(img.size)
print(img.shape)
print(img.dtype)
