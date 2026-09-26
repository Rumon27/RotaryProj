import numpy as np
import cv2 as cv
import time

url = "http://192.168.1.30:5000/video"

# --- ArUco setup ---
# must match the dictionary used in generate_tags.py (DICT_4X4_50)
ARUCO_DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
ARUCO_PARAMS = cv.aruco.DetectorParameters()
ARUCO_DETECTOR = cv.aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMS)


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


def find_tagged_markers(frame):
    """
    Detects ArUco tags in the frame. Returns a dict: {tag_id: (x, y, r)}
    where (x, y) is the tag's center and r is a radius estimate (half the
    tag's diagonal) so it can be drawn/handled the same way the old
    red-circle detections were.

    Unlike the old color-blob detection, the ID here is *decoded directly
    from the tag's pattern* -- it's the same physical marker's ID every
    frame, every session. No frame-to-frame identity guessing needed.
    """
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    corners, ids, _ = ARUCO_DETECTOR.detectMarkers(gray)

    markers = {}
    if ids is not None:
        for tag_corners, tag_id in zip(corners, ids.flatten()):
            pts = tag_corners[0]  # shape (4, 2): the 4 corner points
            cx, cy = pts.mean(axis=0)

            # radius estimate: half the distance between opposite corners
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
    cv.circle(frame, (x, y), 2, color, -1)

    cv.putText(
        frame, label, (x + r + 5, y - r - 5), cv.FONT_HERSHEY_PLAIN, 1.0, color, 1
    )


def main():
    cap = openCamera(url)

    cv.namedWindow("frame", cv.WINDOW_NORMAL)
    cv.resizeWindow("frame", 1200, 800)

    # per-tag-ID state -- keyed directly by the decoded tag ID, since
    # ArUco already gives us stable identity. No tracker/matching needed.
    previous_angles = {}
    total_angles = {}
    rpm_lists = {}
    rpm_avgs = {}
    missed_frames = {}   # tag_id -> consecutive frames not seen

    MAX_MISSED_FRAMES = 15   # how long to keep a tag's history if briefly not detected

    lastTime = time.perf_counter()

    while True:
        success, frame = cap.read()
        if not success:
            print("No frame, ERROR")
            break

        now = time.perf_counter()
        dt = now - lastTime
        lastTime = now

        black, thresh, gray_display = findBlackCircle(frame)

        markers, _ = find_tagged_markers(frame)

        draw_circle(frame, black, (255, 255, 0), "black")

        seen_this_frame = set(markers.keys())

        if black is not None:
            for tag_id, (mx, my, mr) in markers.items():
                draw_circle(frame, (mx, my, mr), (0, 255, 255), f"ID {tag_id}")

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

                    if len(rpm_lists[tag_id]) > 20:
                        rpm_lists[tag_id].pop(0)

                    rpm_avgs[tag_id] = sum(rpm_lists[tag_id]) / len(rpm_lists[tag_id])

        # age out tags that weren't seen this frame; drop their state
        # once they've been missing too long
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
            (255, 255, 255),
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
                (0, 255, 0),
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