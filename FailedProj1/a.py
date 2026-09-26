import numpy as np
import cv2 as cv
import time

url = "http://192.168.1.31:5000/video"


class CentroidTracker:
    def __init__(self, max_disappeared=15, max_distance=60):
        self.next_id = 0
        self.objects = {}          # id -> (x, y)
        self.disappeared = {}      # id -> frames since last seen
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance  # px; reject matches farther than this

    def register(self, centroid):
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.next_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, input_centroids):
        if len(input_centroids) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        if len(self.objects) == 0:
            for c in input_centroids:
                self.register(c)
            return self.objects

        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        objects = np.array(object_centroids)
        inputs = np.array(input_centroids)

        D = np.zeros((len(objects), len(inputs)))

        for i in range(len(objects)):
          for j in range(len(inputs)):

               dx = objects[i][0] - inputs[j][0]
               dy = objects[i][1] - inputs[j][1]

               D[i][j] = np.sqrt(dx**2 + dy**2)

        closest_inputs = D.argmin(axis=1)
        
        rows = np.arange(len(objects))
        cols = closest_inputs
        
        used_rows, used_cols = set(), set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            if D[row, col] > self.max_distance:
                continue

            object_id = object_ids[row]
            self.objects[object_id] = input_centroids[col]
            self.disappeared[object_id] = 0

            used_rows.add(row)
            used_cols.add(col)

        unused_rows = set(range(D.shape[0])) - used_rows
        unused_cols = set(range(D.shape[1])) - used_cols

        for row in unused_rows:
            object_id = object_ids[row]
            self.disappeared[object_id] += 1
            if self.disappeared[object_id] > self.max_disappeared:
                self.deregister(object_id)

        for col in unused_cols:
            self.register(input_centroids[col])

        return self.objects


centerBx = None
centerBy = None

tracker = CentroidTracker(max_disappeared=15, max_distance=60)

previous_angle = {}   # object_id -> last angle (deg)
total_angle = {}      # object_id -> cumulative signed angle (deg)
last_time = {}        # object_id -> perf_counter of last update
rpm_values = {}        # object_id -> last computed rpm (for smooth display)

startTime = time.perf_counter()


cap = cv.VideoCapture(url)

for i in range(10):
     success, frame = cap.read()

     if not success:
          exit(0)


cv.namedWindow("frame", cv.WINDOW_NORMAL)
cv.resizeWindow("frame", 1200, 800)
cv.namedWindow("thresh", cv.WINDOW_NORMAL)
cv.resizeWindow("thresh", 600, 400)
cv.namedWindow("mframe", cv.WINDOW_NORMAL)
cv.resizeWindow("mframe", 600, 400)
cv.namedWindow("hsv", cv.WINDOW_NORMAL)
cv.resizeWindow("hsv", 600, 400)


while True:
     success, frame = cap.read()

     if not success:
          break

     m1frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
     m2frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

     m1frame = cv.GaussianBlur(m1frame, (7, 7), 0)

     ret, thresh = cv.threshold(m1frame, 10, 255, cv.THRESH_BINARY_INV)

     contoursB, hier = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

     lr1 = np.array([0, 100, 100])
     ur1 = np.array([10, 255, 255])

     lr2 = np.array([170, 100, 100])
     ur2 = np.array([179, 255, 255])

     mask1 = cv.inRange(m2frame, lr1, ur1)
     mask2 = cv.inRange(m2frame, lr2, ur2)

     redMask = mask1 | mask2

     kernel = np.ones((3, 3), np.uint8)
     mask = cv.morphologyEx(redMask, cv.MORPH_OPEN, kernel)
     mask = cv.morphologyEx(redMask, cv.MORPH_CLOSE, kernel)

     contoursA, _ = cv.findContours(redMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

     # --- fixed black/blue reference point (single object, unchanged) ---
     for c in contoursB:
          (x, y), r = cv.minEnclosingCircle(c)
          center = (int(x), int(y))
          r = int(r)
          if 300 < cv.contourArea(c) < 1000:
               cv.circle(frame, center, r, (255, 255, 0), 2)
               centerBx = int(x)
               centerBy = int(y)

     # --- collect ALL valid red centroids this frame ---
     red_centroids = []
     for c in contoursA:
          (x, y), r = cv.minEnclosingCircle(c)
          area = cv.contourArea(c)
          if 300 < area < 1000:
               red_centroids.append((int(x), int(y)))
               cv.circle(frame, (int(x), int(y)), int(r), (255, 255, 0), 2)

     # --- match centroids to persistent IDs across frames ---
     tracked_objects = tracker.update(red_centroids)

     # --- per-object angle / RPM tracking ---
     for object_id, (x, y) in tracked_objects.items():
          cv.putText(frame, f"ID {object_id}", (x - 10, y - 15),
                     cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

          if centerBx is None or centerBy is None:
               continue

          rad = np.arctan2(y - centerBy, x - centerBx)
          angle = np.degrees(rad) % 360
          now = time.perf_counter()

          if object_id not in previous_angle:
               previous_angle[object_id] = angle
               total_angle[object_id] = 0.0
               last_time[object_id] = now
               rpm_values[object_id] = 0.0
               continue

          angleDiff = angle - previous_angle[object_id]
          if angleDiff > 180:
               angleDiff -= 360
          elif angleDiff < -180:
               angleDiff += 360

          total_angle[object_id] += angleDiff
          previous_angle[object_id] = angle

          dt = now - last_time[object_id]
          last_time[object_id] = now

          if dt > 0:
               rpm_values[object_id] = (angleDiff / 360) / dt * 60

          cv.putText(frame, f"RPM: {rpm_values[object_id]:.1f}", (x - 10, y + 25),
                     cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

     # --- cleanup stale entries for IDs the tracker has dropped ---
     stale_ids = set(previous_angle.keys()) - set(tracked_objects.keys())
     for object_id in stale_ids:
          del previous_angle[object_id]
          del total_angle[object_id]
          del last_time[object_id]
          del rpm_values[object_id]

     cv.imshow("frame", frame)
     cv.imshow("thresh", thresh)
     cv.imshow("mframe", m1frame)
     cv.imshow("hsv", redMask)

     if cv.waitKey(1) == 27:
          break

cap.release()
cv.destroyAllWindows()