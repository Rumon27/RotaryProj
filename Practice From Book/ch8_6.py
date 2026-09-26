import cv2 as cv
import numpy as np 

img = np.zeros((800, 800, 3), dtype=np.uint8)

kalman = cv.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array(
     [[1,0,0,0],
      [0,1,0,0]], dtype=np.float32
)


kalman.transitionMatrix = np.array(
     [[1, 0, 1, 0],
     [0, 1, 0, 1],
     [0, 0, 1, 0],
     [0, 0, 0, 1]],dtype=np.float32
)

kalman.processNoiseCov = np.array(
     [[1, 0, 0, 0],
[0, 1, 0, 0],
[0, 0, 1, 0],
[0, 0, 0, 1]],dtype=np.float32
) * .03


last_measurement = None
last_prediction = None 

def on_mouse_move(event, x, y, flags, param):
     global img, kalman, last_measurement, last_prediction
     
     measurement = np.array([[x], [y]],dtype=np.float32)

     if last_measurement is None:
          kalman.statePre = np.array([[x], [y], [0], [0]],dtype=np.float32)
          kalman.statePost = np.array([[x], [y], [0], [0]],dtype=np.float32)
          prediction = measurement
     
     else:
          kalman.correct(measurement)
          prediction = kalman.predict()

          cv.line(img, (int(last_measurement[0]), int(last_measurement[1])),
                 (int(measurement[0]), int(measurement[1])), (0, 200, 200))

        
          cv.line(img, (int(last_prediction[0]), int(last_prediction[1])),
                 (int(prediction[0]), int(prediction[1])), (0, 0, 255))
     
     last_prediction = prediction.copy()          
     last_measurement = measurement


cv.namedWindow('kalman Tracker', cv.WINDOW_NORMAL)
cv.resizeWindow('kalman Tracker', 600, 400)

cv.setMouseCallback('kalman Tracker', on_mouse_move)

while True:
     
     cv.imshow('kalman Tracker', img)
     
     if cv.waitKey(1) == 27:
          cv.imwrite('kalman.png', img)
          break
          