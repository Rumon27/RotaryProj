import cv2 as cv 
import numpy as np 
import os 

root = os.getcwd()

imgPath = os.path.join(root, "images/lines.jpg")

img = cv.imread(imgPath)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
edges = cv.Canny(gray, 50 ,120)

minLineLength = 20
maxLineGap = 5

lines = cv.HoughLinesP(edges, 1, np.pi/180, 20, minLineLength, maxLineGap)

print(lines[0])

     
x1 = lines[0][0]
x2 = lines[0][1]
y1 = lines[0][2]
y2 = lines[0][3]

print(x1, x2, y1, y2)
print(y2)
cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

     
cv.imshow("edges", edges)
cv.imshow("lines", img)
cv.waitKey()
cv.destroyAllWindows() 


