import cv2
import numpy as np

img = np.zeros((1080, 1920, 3), dtype=np.uint8)

cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Test", 10000, 400)

cv2.imshow("Test", img)
cv2.waitKey(0)
cv2.destroyAllWindows()