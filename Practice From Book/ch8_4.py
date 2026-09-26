url = "http://192.168.1.73:8570/video"
import os 

import cv2 as cv 


cap  = cv.VideoCapture(url)

#1
for i in range(10):
     success, frame = cap.read();
     
if not success:
     exit(1);
     
#2 ROI
fh = frame.shape[0]
fw = frame.shape[1]

w = fw // 8
h = fh // 8

x = fw // 2 - w//2
y = fh // 2 - h//2

trackWindow = (x, y, w, h)

#3 ROI to HSV

roi = frame[y:y+h, x:x+w]
hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)

#4 histogram
roi_hist = cv.calcHist([hsv_roi], [0], None, [180], [0, 180])

#5 Normalize
cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)

#6 iterations: BUT I DONT KNOW HOW THESE FUNCTION WORKING
term_crit = (cv.TERM_CRITERIA_COUNT | cv.TermCriteria_EPS, 10, 1)

#7 calc
success, frame = cap.read()



cv.namedWindow("back", cv.WINDOW_NORMAL)
cv.resizeWindow("back", 600, 400)
cv.namedWindow("meanshift", cv.WINDOW_NORMAL)
cv.resizeWindow("meanshift", 600, 400)
while success:
     hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

     back_proj = cv.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
     
     num_iters, trackWindow = cv.meanShift(back_proj, trackWindow, term_crit)

     #8
     x, y, w, h = trackWindow
     
     cv.rectangle(frame, (x,y), (x+w, y + h), (0, 255, 100), 2)
     
     cv.imshow("back", back_proj)
     cv.imshow('meanshift', frame)
     
     if cv.waitKey(1) == 27:
               break
          
     success, frame = cap.read()
