import cv2 as cv 
import numpy as np 

img = np.zeros((200, 200), dtype=np.uint8)
img[50: 151, 50: 151] = 255

ret, thresh = cv.threshold(img, 127, 255, 0)
contour, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

color = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
img = cv.drawContours(color, contour, -1, (0,255,0), 1)


cv.imshow("cont", img)
cv.waitKey()
cv.destroyAllWindows()

print(contour)

