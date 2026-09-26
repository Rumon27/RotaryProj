import numpy as np
import cv2 as cv
import time

url = "http://192.168.1.31:5000/video"


def open_camera(url):
    cap = cv.VideoCapture(url)
    if not cap.isOpened():
        print("Could not open camera")
        exit()

    # Throw away a few frames so the camera settles
    for i in range(10):
        ok, frame = cap.read()
        if not ok:
            print("No frame from camera")
            exit()

    return cap


def find_black_circle(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (7, 7), 0)

    _, thresh = cv.threshold(gray, 10, 255, cv.THRESH_BINARY_INV)

    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    best = None
    best_area = 0

    for c in contours:
        area = cv.contourArea(c)
        if 300 < area < 1000 and area > best_area:
            (x, y), r = cv.minEnclosingCircle(c)
            best = (int(x), int(y), int(r))
            best_area = area

    return best, thresh, gray


def find_red_circle(frame):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    lower1 = np.array([0, 100, 100])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([170, 100, 100])
    upper2 = np.array([179, 255, 255])

    mask1 = cv.inRange(hsv, lower1, upper1)
    mask2 = cv.inRange(hsv, lower2, upper2)
    mask = mask1 | mask2

    kernel = np.ones((3, 3), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    best = None
    best_area = 0

    for c in contours:
        area = cv.contourArea(c)
        if 300 < area < 1000 and area > best_area:
            (x, y), r = cv.minEnclosingCircle(c)
            best = (int(x), int(y), int(r))
            best_area = area

    return best, mask


def get_angle(black, red):
    bx, by, _ = black
    rx, ry, _ = red

    rad = np.arctan2(ry - by, rx - bx)
    angle = np.degrees(rad) % 360
    return angle


def draw_circle(frame, circle, color, label):
    if circle is None:
        return

    x, y, r = circle
    cv.circle(frame, (x, y), r, color, 2)
    cv.circle(frame, (x, y), 2, color, -1)
    cv.putText(frame, label, (x + r + 5, y - r - 5),
               cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


def main():
    cap = open_camera(url)

    cv.namedWindow("frame", cv.WINDOW_NORMAL)
    cv.resizeWindow("frame", 1200, 800)
    cv.namedWindow("thresh", cv.WINDOW_NORMAL)
    cv.resizeWindow("thresh", 600, 400)
    cv.namedWindow("mframe", cv.WINDOW_NORMAL)
    cv.resizeWindow("mframe", 600, 400)
    cv.namedWindow("hsv", cv.WINDOW_NORMAL)
    cv.resizeWindow("hsv", 600, 400)

    previous_angle = None
    total_angle = 0.0

    last_time = time.perf_counter()
    rpm_list = []
    rpm_avg = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("No frame, stopping")
            break

        now = time.perf_counter()
        dt = now - last_time
        last_time = now

        black, thresh, gray = find_black_circle(frame)
        red, red_mask = find_red_circle(frame)

        draw_circle(frame, black, (255, 255, 0), "black")
        draw_circle(frame, red, (0, 255, 255), "red")

        if black is not None and red is not None:
            angle = get_angle(black, red)

            if previous_angle is None:
                previous_angle = angle
            else:
                diff = angle - previous_angle

                if diff > 180:
                    diff -= 360
                elif diff < -180:
                    diff += 360

                total_angle += diff
                previous_angle = angle

                if dt > 0:
                    rpm = (diff / 360.0) / dt * 60.0
                    rpm_list.append(rpm)

                    if len(rpm_list) > 20:
                        rpm_list.pop(0)

                    rpm_avg = sum(rpm_list) / len(rpm_list)
        else:
            # If we lose the markers, reset the angle tracking
            previous_angle = None

        cv.putText(frame, f"RPM: {-rpm_avg:.2f}", (50, 50),
                   cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        cv.putText(frame, f"Angle: {total_angle:.1f}", (50, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv.imshow("frame", frame)
        cv.imshow("thresh", thresh)
        cv.imshow("mframe", gray)
        cv.imshow("hsv", red_mask)

        if cv.waitKey(1) == 27:
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()