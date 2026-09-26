import numpy as np
import cv2 as cv 

def get_limit(color):
     c = np.uint8([[color]])

     hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)

     hue = hsvC[0][0][0]
     saturation = hsvC[0][0][1]
     value = hsvC[0][0][2]
     
     if value < 50:
          lowrLmt = np.array([0,0,0])
          upprLmt = np.array([180, 255, 80])
     
     elif saturation < 50:
          lowrLmt = np.array([0,0,180])     
          upprLmt = np.array([180, 80, 255])

     else:
        if hue >= 165:
            lowrLmt = np.array([hue - 10, 100, 100], dtype=np.uint8)
            upprLmt = np.array([180, 255, 255], dtype=np.uint8)

        elif hue <= 15:
            lowrLmt = np.array([0, 100, 100], dtype=np.uint8)
            upprLmt = np.array([hue + 10, 255, 255], dtype=np.uint8)

        else:
            lowrLmt = np.array([hue - 10, 100, 100], dtype=np.uint8)
            upprLmt = np.array([hue + 10, 255, 255], dtype=np.uint8)
               
     return lowrLmt, upprLmt