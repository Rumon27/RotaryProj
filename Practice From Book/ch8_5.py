import numpy as np
import cv2 as cv

url = "http://192.168.1.73:8570/video"

cap = cv.VideoCapture(url)

# Give the stream a few frames to stabilize
for i in range(10):
    success, frame = cap.read()

if not success:
    print("Could not read video stream")
    cap.release()
    exit()


# -------------------------
# 1. Create ROI
# -------------------------

fh, fw = frame.shape[:2]

w = fw // 8
h = fh // 8

x = fw // 2 - w // 2
y = fh // 2 - h // 2

trackWindow = (x, y, w, h)


# -------------------------
# 2. Convert ROI to HSV
# -------------------------

roi = frame[y:y+h, x:x+w]

hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)


# -------------------------
# 3. Create mask
# -------------------------

mask = cv.inRange(
    hsv_roi,
    np.array((0, 60, 32)),
    np.array((180, 255, 255))
)


# -------------------------
# 4. Create histogram
# -------------------------

roi_hist = cv.calcHist(
    [hsv_roi],
    [0],
    mask,
    [180],
    [0, 180]
)


# -------------------------
# 5. Normalize histogram
# -------------------------

cv.normalize(
    roi_hist,
    roi_hist,
    0,
    255,
    cv.NORM_MINMAX
)


# -------------------------
# 6. CamShift termination
# -------------------------

term_crit = (
    cv.TERM_CRITERIA_COUNT | cv.TERM_CRITERIA_EPS,
    10,
    1
)


# -------------------------
# Windows
# -------------------------

cv.namedWindow("back", cv.WINDOW_NORMAL)
cv.resizeWindow("back", 600, 400)

cv.namedWindow("camshift", cv.WINDOW_NORMAL)
cv.resizeWindow("camshift", 600, 400)


# -------------------------
# Main loop
# -------------------------

success, frame = cap.read()

while success:

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # Back projection
    back_proj = cv.calcBackProject(
        [hsv],
        [0],
        roi_hist,
        [0, 180],
        1
    )

    # CamShift
    rotated_rect, trackWindow = cv.CamShift(
        back_proj,
        trackWindow,
        term_crit
    )

    # Draw rotated rectangle
    box_points = cv.boxPoints(rotated_rect)
    box_points = np.intp(box_points)

    cv.polylines(
        frame,
        [box_points],
        True,
        (255, 0, 0),
        2
    )

    cv.imshow("back", back_proj)
    cv.imshow("camshift", frame)

    key = cv.waitKey(1) & 0xFF

    if key == 27:
        break

    success, frame = cap.read()


cap.release()
cv.destroyAllWindows()