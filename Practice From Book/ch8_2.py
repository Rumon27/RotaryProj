import cv2 as cv 
import numpy as np 
import os 

root = os.getcwd()

vidPath = os.path.join(root, "videos/hallway.mpg")
cap  = cv.VideoCapture(vidPath)


bg_subtractor = cv.createBackgroundSubtractorMOG2(detectShadows=True)

erode_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,3))
dilate_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (7,7))

success, frame = cap.read()

while success:
     fg_mask = bg_subtractor.apply(frame)
     
     _, thresh = cv.threshold(fg_mask, 244, 255, cv.THRESH_BINARY)
     cv.erode(thresh, erode_kernel, thresh, iterations=2)
     cv.dilate(thresh, dilate_kernel, thresh, iterations=2)
     
     contours, heir = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
     
     for c in contours:
          if cv.contourArea(c) > 2000:
                    x, y, w, h = cv.boundingRect(c)
                    cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 255), 2)

     cv.imshow('mog', fg_mask)
     cv.imshow("thres", thresh)
     cv.imshow('detection', frame)

     if cv.waitKey(30) == 27:
          break
     
     success, frame = cap.read()
     
     
