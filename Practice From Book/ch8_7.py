import cv2 as cv 
import numpy as np 
import os 

class Pedestrian():
     def __init__(self, id, hsv_frame, track_window):
          self.id = id 
          self.track_window = track_window
          self.term_crit = (cv.TermCriteria_COUNT | cv.TermCriteria_EPS, 10, 1)

          x, y, w, h = self.track_window
          
          roi = hsv_frame[y:y+h, x:x+w]
          roi_hist = cv.calcHist([roi], [0], None, [16], [0, 180])
          self.roi_hist = cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)

          self.kalman = cv.KalmanFilter(4, 2)
          
          self.kalman.measurementMatrix = np.array(
               [
                    [1,0,0,0],
                    [0,1,0,0]
               ]     , np.float32
          )
          
          self.kalman.transitionMatrix = np.array(
               [
                   [1, 0, 1, 0],
                           [0, 1, 0, 1],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]
               ], np.float32
          )
          
          self.kalman.processNoiseCov = np.array(
               [
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]
               ], np.float32
          
          )
     
          center_x = x + w / 2
          center_y = y + h / 2
          
          self.kalman.statePre = np.array(
               [
                    [center_x], [center_y], [0], [0]
               ], np.float32
          )
          
          self.kalman.statePost = np.array(
               [
                    [center_x], [center_y], [0], [0]
               ], np.float32
          )               
          
     def update(self, frame, hsv_frame):
          back_proj = cv.calcBackProject(
               [hsv_frame], [0], self.roi_hist, [0, 180], 1)

          ret, self.track_window = cv.meanShift(
               back_proj, self.track_window, self.term_crit)

          x,y,w,h = self.track_window 
          center = np.array([[x + w/2], [y + h/2]], np.float32)
          
          prediction = self.kalman.predict()
          estimate = self.kalman.correct(center)

          center_offset = estimate[:2, 0] - center[:, 0]
          
          self.track_window = (x + int(center_offset[0]),
                               y + int(center_offset[1]), w, h)
          
          x,y,w,h = self.track_window
          
          cv.circle(frame, (int(prediction[0, 0]), int(prediction[1, 0])),
                    4, (255, 0, 0), -1)
          
          cv.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

          cv.putText(frame, "ID: %d" % self.id, (x, y-5), cv.FONT_HERSHEY_SIMPLEX,
                     0.6, (255, 0, 0), 1, cv.LINE_AA)
          
          
def main():
     root = os.getcwd()
     vidPath = os.path.join(root, "videos/pedestrians.avi")
     cap = cv.VideoCapture(vidPath)
     
     bg_subtractor = cv.createBackgroundSubtractorKNN()
     historyLen = 20
     bg_subtractor.setHistory(historyLen)

     erode_kernel = cv.getStructuringElement(
          cv.MORPH_ELLIPSE, (3,3)
     )
     
     dilate_kernel = cv.getStructuringElement(
          cv.MORPH_ELLIPSE, (5,7)
     )
     
     pedestrians = []
     num_history_frames_populated = 0
     while True:
          success, frame = cap.read()
          if not success:
               break

          fg_mask = bg_subtractor.apply(frame)

          if num_history_frames_populated < historyLen:
               num_history_frames_populated += 1
               continue
          
          _, thresh = cv.threshold(fg_mask, 127, 255, cv.THRESH_BINARY)
          
          cv.erode(thresh, erode_kernel, thresh, iterations=2)
          cv.dilate(thresh, dilate_kernel, thresh, iterations=2)

          conturs, heir = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

          hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

          should_initialize_pedestrians = len(pedestrians) == 0
          
          id = 0
          for c in conturs:
               if cv.contourArea(c) > 500:
                    (x, y, w, h) = cv.boundingRect(c)
                    cv.rectangle(frame, (x, y), (x+w, y+h),
                                 (0,255,0), 1)
                    
                    if should_initialize_pedestrians:
                         pedestrians.append(
                              Pedestrian(id, hsv_frame, (x,y,w,h))
                         )
               id += 1
               
          for pedestrian in pedestrians:
               pedestrian.update(frame, hsv_frame)
               
          cv.imshow("Pdes", frame)
          
          if cv.waitKey(110) == 27:
               break 
          
if __name__=="__main__":
     main() 
          

          

          
          
          