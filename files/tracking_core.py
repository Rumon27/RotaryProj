import numpy as np
import cv2 as cv

ARUCO_DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
ARUCO_PARAMS = cv.aruco.DetectorParameters()
ARUCO_DETECTOR = cv.aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMS)


def crop_region(frame, region):
    if region is None:
        return frame
    x, y, w, h = region
    return frame[y:y + h, x:x + w]


def find_black_circle(frame):
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

    return circle


def find_tagged_markers(frame):
    """
    Returns {tag_id: (x, y, r)} -- (x, y) is the tag's center, r is a
    pixel-size estimate (half the corner diagonal), NOT distance from any
    rotation center. Orbital radius must be computed separately against
    the black circle's position.
    """
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    corners, ids, _ = ARUCO_DETECTOR.detectMarkers(gray)

    markers = {}
    if ids is not None:
        for tag_corners, tag_id in zip(corners, ids.flatten()):
            pts = tag_corners[0]
            cx, cy = pts.mean(axis=0)
            diag = np.linalg.norm(pts[0] - pts[2])
            r = diag / 2
            markers[int(tag_id)] = (int(cx), int(cy), int(r))

    return markers


def get_angle(black, point):
    bx, by, _ = black
    rx, ry = point
    rad = np.arctan2(ry - by, rx - bx)
    return np.degrees(rad) % 360


def draw_circle(frame, circle, color, label):
    if circle is None:
        return

    x, y, r = circle
    cv.circle(frame, (x, y), max(r, 2), color, 2)
    cv.circle(frame, (x, y), 2, color, -1)
    cv.putText(frame, label, (x + r + 5, y - r - 5), cv.FONT_HERSHEY_PLAIN, 1.0, color, 1)
