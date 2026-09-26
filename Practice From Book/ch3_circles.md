## Note 1

1. How to detect circles
2. https://theailearner.com/tag/cv2-houghcircles/ 
3. the function houghCircles() return 3 parameters:
   1. (x, y) point
   2. r Radius
4. circles = cv2.HoughCircles(img_gray,cv2.HOUGH_GRADIENT,1,20,
                     param1=60,param2=40,minRadius=0,maxRadius=0)
   1. image: 8-bit, single-channel, grayscale input image
   2. method: HOUGH_GRADIENT and HOUGH_GRADIENT_ALT
   3. dp: The inverse ratio of accumulator resolution and image resolution
   4. minDist: Minimum distance between the centers of the detected circles. All the candidates below this distance are neglected as explained above
   5. param1: it is the higher threshold of the two passed to the Canny edge detector (the lower canny threshold is twice smaller)
   6. param2: it is the accumulator threshold for the circle centers at the detection stage as discussed above.
   7. minRadius: minimum radius that you expect. If unknown, put zero as default.
   8. maxRadius: if -ve, only circle centers are returned without radius search. If unknown, put zero as default.
5. this function return 3 dimensional array. that is why we need to
     convert the array to 2D using 
          np.uint16(np.round(circles)) and  print(circles[0, :]) 