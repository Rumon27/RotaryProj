import cv2 as cv 
import numpy as np 
import os 
from limit import get_limit


url = "http://192.168.1.73:8570/video"

orange = [0,85,255]
cap = cv.VideoCapture(url)

def videoFromCam():
    
    if not cap.isOpened():
        exit()
        
    cv.namedWindow('Phone Camera', cv.WINDOW_NORMAL)
    cv.resizeWindow('Phone Camera', 800, 600)
        
    while True:
        ret, frame = cap.read()
        
        if ret:
            cv.imshow('Phone Camera', frame)
            
                   
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv.destroyAllWindows()
    
def detectColor():
    cv.namedWindow('FRAME', cv.WINDOW_NORMAL)
    cv.resizeWindow('FRAME', 800, 600)
    
    while True:
        ret, frame = cap.read()

        hsvImg = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        lowerLimit, upperLimit = get_limit(color=orange)

        mask = cv.inRange(hsvImg, lowerLimit, upperLimit)



        kernel = np.ones((5, 5), np.uint8)

        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

        contours, _ = cv.findContours(
            mask,
            cv.RETR_EXTERNAL,
            cv.CHAIN_APPROX_SIMPLE
        )

        if contours:
            largest = max(contours, key=cv.contourArea)

            if cv.contourArea(largest) > 500:
                x, y, w, h = cv.boundingRect(largest)

                cv.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    3
                )

        cv.imshow('FRAME', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv.destroyAllWindows()
    



if __name__=='__main__':
    #videoFromCam()
    detectColor()