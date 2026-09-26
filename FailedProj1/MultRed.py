import numpy as np
import cv2 as cv
import time
from FailedProj1.Tracker import CentroidTracker

url = "http://192.168.1.31:5000/video"


def openCamera(url):
    cap = cv.VideoCapture(url)

    if not cap.isOpened():
        print("could not open camera")
        exit()

    for i in range(10):
        success, frame = cap.read()

        if not success:
            print("No frame from camera")
            exit()

    return cap


def findBlackCircle(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray_blurred = cv.GaussianBlur(gray, (7, 7), 0)

    _, thresh = cv.threshold(gray_blurred, 10, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    circle = None
    best_area = 0

    for c in contours:
        area = cv.contourArea(c)
        if 100 < area < 500 and area > best_area:
            (x, y), r = cv.minEnclosingCircle(c)
            circle = (int(x), int(y), int(r))
            best_area = area

    return circle, thresh, gray_blurred


def find_red_circle(frame):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    l1 = np.array([0, 100, 100])
    u1 = np.array([10, 255, 255])
    l2 = np.array([170, 100, 100])
    u2 = np.array([179, 255, 255])

    mask1 = cv.inRange(hsv, l1, u1)
    mask2 = cv.inRange(hsv, l2, u2)

    mask = mask1 | mask2

    kernel = np.ones((3, 3), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    circles = []

    for c in contours:
        area = cv.contourArea(c)
        if 60 < area < 300:
            (x, y), r = cv.minEnclosingCircle(c)
            circles.append((int(x), int(y), int(r)))

    return circles, mask


def get_angle(black, red_point):
    bx, by, _ = black
    rx, ry = red_point

    rad = np.arctan2(ry - by, rx - bx)
    angle = np.degrees(rad) % 360

    return angle


def draw_circle(frame, circle, color, label):
    if circle is None:
        return

    x, y, r = circle

    cv.circle(frame, (x, y), max(r, 2), color, 2)
    cv.circle(frame, (x, y), 2, color, -1)

    cv.putText(
        frame, label, (x + r + 5, y - r - 5), cv.FONT_HERSHEY_PLAIN, 1.0, color, 1
    )


def main():
    cap = openCamera(url)

    cv.namedWindow("frame", cv.WINDOW_NORMAL)
    cv.resizeWindow("frame", 1200, 800)
    # cv.namedWindow("thresh", cv.WINDOW_NORMAL)
    # cv.resizeWindow("thresh", 600, 400)
    # cv.namedWindow("mframe", cv.WINDOW_NORMAL)
    # cv.resizeWindow("mframe", 600, 400)
    # cv.namedWindow("hsv", cv.WINDOW_NORMAL)
    # cv.resizeWindow("hsv", 600, 400)

    red_tracker = CentroidTracker(max_disappeared=15, max_distance=260)


    previous_angles = {}  
    total_angles = {}  
    rpm_lists = {}  
    rpm_avgs = {}  

    lastTime = time.perf_counter()

    while True:
        success, frame = cap.read()
        if not success:
            print("No frame, ERROR")
            break

        now = time.perf_counter()
        dt = now - lastTime
        lastTime = now

        black, thresh, gray = findBlackCircle(frame)

        redCircles, red_mask = find_red_circle(frame)
        redCentroids = [(x, y) for (x, y, r) in redCircles]

        objects = red_tracker.update(redCentroids)

        draw_circle(frame, black, (255, 255, 0), "black")

       
        if black is not None:
            for object_id, centroid in objects.items():
                cx, cy = centroid
                cv.circle(frame, (cx, cy), 4, (100, 100, 100), -1)
                cv.putText(
                    frame,
                    f"ID {object_id}",
                    (cx + 8, cy - 8),
                    cv.FONT_HERSHEY_PLAIN,
                    1.0,
                    (100, 100, 100),
                    1,
                )

                angle = get_angle(black, centroid)

                if object_id not in previous_angles:
                    
                    previous_angles[object_id] = angle
                    total_angles[object_id] = 0
                    rpm_lists[object_id] = []
                    rpm_avgs[object_id] = 0
                    continue

                diff = angle - previous_angles[object_id]

                if diff > 180:
                    diff -= 360
                elif diff < -180:
                    diff += 360

                total_angles[object_id] += diff
                previous_angles[object_id] = angle

                if dt > 0:
                    rpm = (diff / 360) / dt * 60
                    rpm_lists[object_id].append(rpm)

                    if len(rpm_lists[object_id]) > 20:
                        rpm_lists[object_id].pop(0)

                    rpm_avgs[object_id] = sum(rpm_lists[object_id]) / len(
                        rpm_lists[object_id]
                    )

  
        stale_ids = [oid for oid in previous_angles if oid not in objects]
        for oid in stale_ids:
            del previous_angles[oid]
            del total_angles[oid]
            del rpm_lists[oid]
            del rpm_avgs[oid]

      
        cv.putText(
            frame,
            "RPM per marker:",
            (10, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        y = 60
        for object_id in sorted(rpm_avgs.keys()):
            rpm = -rpm_avgs[object_id]  
            cv.putText(
                frame,
                f"ID {object_id}: {rpm:6.2f} RPM",
                (10, y),
                cv.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
            y += 30

        cv.imshow("frame", frame)
        # cv.imshow("thresh", thresh)
        # cv.imshow("mframe", gray)
        # cv.imshow("hsv", red_mask)

        if cv.waitKey(1) == 27:
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
