import cv2 as cv 
import numpy as np 
import os 

# detect if i is inside o
def is_inside(i, o):
     ix, iy, iw, ih = i
     ox, oy, ow, oh = o 
     
     if ox < ix and oy < iy and (ox + ow) > (ix + iw) and (oy + oh) > (iy + ih):
          return True
     else:
          return False




root = os.getcwd()

imgPath = os.path.join(root, "images/haying.jpg")
img = cv.imread(imgPath)


hog = cv.HOGDescriptor()
hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())
found_rects, found_weights = hog.detectMultiScale(img, winStride=(4,4), scale=1.02,
                                                  groupThreshold=1.9)

found_rects_filtered = []
found_weights_filtered = []

for ri, r in enumerate(found_rects):
     for qi, q in enumerate(found_rects):
          if ri != qi and is_inside(r, q):
               break
          else:
               found_rects_filtered.append(r)
               found_weights_filtered.append(found_weights[ri])        
               
for ri, r in enumerate(found_rects_filtered):
     x, y, w, h = r 
     cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
     
     text = f"{found_weights_filtered[ri]:.2f}"
     
     cv.putText(img=img, text=text, org=(x, y-20),fontFace= cv.FONT_HERSHEY_SIMPLEX, fontScale=1,color=(0, 255, 255), thickness=1)
       
cv.imshow("Bitches in Hayfield", img)
cv.waitKey()
