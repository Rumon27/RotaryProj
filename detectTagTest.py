import cv2

DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
PARAMS = cv2.aruco.DetectorParameters()
DETECTOR = cv2.aruco.ArucoDetector(DICTIONARY, PARAMS)

def main():
    img = cv2.imread("tags/tag_0.png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    corners, ids, rejected = DETECTOR.detectMarkers(gray)

    print("ids found:", ids)
    print("corners:", corners)
    print("num rejected candidates:", len(rejected))

if __name__ == "__main__":
    main()