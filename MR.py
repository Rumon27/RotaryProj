import numpy as np
import cv2 as cv
import time

# --- Video source ---
# any URL cv.VideoCapture can open: an IP camera / MJPEG stream, an RTSP
# stream, a network-shared desktop stream, or a local video file path.
SOURCE_URL = "http://127.0.0.1:5000/video"

# --- Region to crop out of each captured frame ---
# (x, y, width, height) in pixels, relative to the captured frame itself.
# Set to None to use the whole frame with no cropping.
CAPTURE_REGION = None  # e.g. (100, 50, 1000, 1000)

# --- ArUco setup ---
# must match the dictionary used in generate_tags.py (DICT_4X4_50)
ARUCO_DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
ARUCO_PARAMS = cv.aruco.DetectorParameters()
ARUCO_DETECTOR = cv.aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMS)


def openCamera(url):
    cap = cv.VideoCapture(url)

    if not cap.isOpened():
        print(f"could not open video source: {url}")
        exit()

    for i in range(10):
        success, frame = cap.read()
        if not success:
            print("No frame from source")
            exit()

    return cap


def crop_region(frame, region):
    if region is None:
        return frame

    x, y, w, h = region
    return frame[y : y + h, x : x + w]


def findBlackCircle(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray_blurred = cv.GaussianBlur(gray, (7, 7), 0)

    _, thresh = cv.threshold(gray_blurred, 10, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    circle = None
    best_area = 0

    for c in contours:
        area = cv.contourArea(c)
        if 100 < area < 1500 and area > best_area:
            (x, y), r = cv.minEnclosingCircle(c)
            circle = (int(x), int(y), int(r))
            best_area = area

    return circle, thresh, gray_blurred


def find_tagged_markers(frame):
    """
    Detects ArUco tags in the frame. Returns a dict: {tag_id: (x, y, r)}
    where (x, y) is the tag's center and r is a radius estimate (half the
    tag's diagonal). The ID is decoded directly from the tag's pattern --
    the same physical marker's ID every frame, every session.
    """
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    corners, ids, _ = ARUCO_DETECTOR.detectMarkers(gray)

    markers = {}
    if ids is not None:
        for tag_corners, tag_id in zip(corners, ids.flatten()):
            pts = tag_corners[0]  # shape (4, 2): the 4 corner points
            cx, cy = pts.mean(axis=0)

            diag = np.linalg.norm(pts[0] - pts[2])
            r = diag / 2

            markers[int(tag_id)] = (int(cx), int(cy), int(r))

    return markers, gray


def get_angle(black, point):
    bx, by, _ = black
    rx, ry = point

    rad = np.arctan2(ry - by, rx - bx)
    angle = np.degrees(rad) % 360

    return angle


def draw_circle(frame, circle, color, label):
    if circle is None:
        return

    x, y, r = circle

    cv.circle(frame, (x, y), max(r, 2), color, 2)
    

    cv.putText(
        frame, label, (x + r + 5, y - r - 5), cv.FONT_HERSHEY_PLAIN, 1.0, color, 1
    )


def main():
     cap = openCamera(SOURCE_URL)

     cv.namedWindow("frame", cv.WINDOW_NORMAL)
     cv.resizeWindow("frame", 1000, 1000)

     previous_angles = {}
     total_angles = {}
     rpm_lists = {}
     rpm_avgs = {}
     missed_frames = {}

     MAX_MISSED_FRAMES = 15

     lastTime = time.perf_counter()
     debug_saved = False

     while True:
          success, raw_frame = cap.read()
          if not success:
               print("No frame, ERROR")
               break

          frame = crop_region(raw_frame, CAPTURE_REGION)

          if not debug_saved:
               cv.imwrite("debug_frame.png", frame)
               debug_saved = True
               print("saved debug_frame.png -- check this if detection looks wrong")
               print(
                    f"raw frame size: {raw_frame.shape[1]}x{raw_frame.shape[0]}, "
                    f"cropped size: {frame.shape[1]}x{frame.shape[0]}"
               )

          now = time.perf_counter()
          dt = now - lastTime
          lastTime = now

          black, thresh, gray_display = findBlackCircle(frame)

          markers, _ = find_tagged_markers(frame)

          draw_circle(frame, black, (255, 255, 0), "black")

          seen_this_frame = set(markers.keys())

          if black is not None:
               for tag_id, (mx, my, mr) in markers.items():
                    draw_circle(frame, (mx, my, mr), (255, 0, 255), f"ID {tag_id}")

                    angle = get_angle(black, (mx, my))

                    if tag_id not in previous_angles:
                         previous_angles[tag_id] = angle
                         total_angles[tag_id] = 0
                         rpm_lists[tag_id] = []
                         rpm_avgs[tag_id] = 0
                         missed_frames[tag_id] = 0
                         continue

                    diff = angle - previous_angles[tag_id]

                    if diff > 180:
                         diff -= 360
                    elif diff < -180:
                         diff += 360

                    total_angles[tag_id] += diff
                    previous_angles[tag_id] = angle
                    missed_frames[tag_id] = 0

                    if dt > 0:
                         rpm = (diff / 360) / dt * 60
                         rpm_lists[tag_id].append(rpm)

                         if len(rpm_lists[tag_id]) > 50:
                              rpm_lists[tag_id].pop(0)

                         rpm_avgs[tag_id] = sum(rpm_lists[tag_id]) / len(rpm_lists[tag_id])

          for tag_id in list(previous_angles.keys()):
               if tag_id not in seen_this_frame:
                    missed_frames[tag_id] = missed_frames.get(tag_id, 0) + 1
                    if missed_frames[tag_id] > MAX_MISSED_FRAMES:
                         del previous_angles[tag_id]
                         del total_angles[tag_id]
                         del rpm_lists[tag_id]
                         del rpm_avgs[tag_id]
                         del missed_frames[tag_id]

          cv.putText(
               frame,
               "RPM per marker:",
               (10, 30),
               cv.FONT_HERSHEY_SIMPLEX,
               0.6,
               (0, 0, 0),
               2,
          )

          y = 60
          for tag_id in sorted(rpm_avgs.keys()):
               rpm = -rpm_avgs[tag_id]
               cv.putText(
                    frame,
                    f"ID {tag_id}: {rpm:6.2f} RPM",
                    (10, y),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 150, 0),
                    2,
               )
               y += 30

          cv.imshow("frame", frame)

          if cv.waitKey(1) == 27:
               break

     cap.release()
     cv.destroyAllWindows()


if __name__ == "__main__":
    main()
