url = "http://192.168.1.73:8570/video"
import os 

import cv2 as cv 

root = os.getcwd()

BLUR_RADIUS = 21 
erode_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
dilate_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 9))
vidPath = os.path.join(root, "videos/hallway.mpg")
cap = cv.VideoCapture(vidPath)

for i in range(10):
     success, frame = cap.read()

if not success:
     exit(1)
     
     
gray_background = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
gray_background = cv.GaussianBlur(gray_background, (BLUR_RADIUS, BLUR_RADIUS), 0)



success, frame = cap.read()

cv.namedWindow("diff", cv.WINDOW_NORMAL)
cv.namedWindow("thresh", cv.WINDOW_NORMAL)
cv.namedWindow("detection", cv.WINDOW_NORMAL)

cv.resizeWindow("diff", 400, 600)
cv.resizeWindow("thresh", 400, 600)
cv.resizeWindow("detection", 400, 600)

while success:
     gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
     gray_frame = cv.GaussianBlur(gray_frame, (BLUR_RADIUS, BLUR_RADIUS), 0)


     diff = cv.absdiff(gray_frame, gray_background)
     _, thresh = cv.threshold(diff, 40, 255, cv.THRESH_BINARY)
     cv.erode(thresh, erode_kernel, thresh, iterations=2)
     cv.dilate(thresh, dilate_kernel, thresh, iterations=2)

     contours, heir = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

     for c in contours:
          if cv.contourArea(c) > 4000:
               x, y, w, h = cv.boundingRect(c)
               cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
               
     cv.imshow("diff", diff)
     cv.imshow("thresh", thresh)
     cv.imshow("detection", frame)
     
     if cv.waitKey(1) == 27:
          break
     
     success, frame = cap.read()






