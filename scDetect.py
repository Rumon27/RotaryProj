import cv2
import numpy as np
import mss

DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
PARAMS = cv2.aruco.DetectorParameters()
DETECTOR = cv2.aruco.ArucoDetector(DICTIONARY, PARAMS)

# mss region format: dict with left, top, width, height (not right/bottom)
CAPTURE_REGION = {"left": 100, "top": 100, "width": 500, "height": 500}

def main():
    with mss.MSS() as sct:
        raw = sct.grab(CAPTURE_REGION)
        frame = np.array(raw)                      # BGRA
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    cv2.imwrite("debug_screenshot.png", frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = DETECTOR.detectMarkers(gray)

    print("ids found:", ids)
    print("num rejected candidates:", len(rejected))

if __name__ == "__main__":
    main()