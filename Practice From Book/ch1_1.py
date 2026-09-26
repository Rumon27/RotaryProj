import cv2 as cv

url = "http://192.168.1.73:8570/video"

clicked = False 
def onMouse(event, x, y, flags, param):
     global clicked
     if event == cv.EVENT_LBUTTONUP:
          clicked = True
     
camera = cv.VideoCapture(url)

cv.namedWindow("mywindow", cv.WINDOW_NORMAL)
cv.resizeWindow("mywindow", 400, 600)
cv.setMouseCallback("mywindow", onMouse)
print('Showing camera feed. Click window or press any key to stop')

success, frame = camera.read()
while success and cv.waitKey(1) == -1 and not clicked:
     cv.imshow("mywindow", frame)
     success, frame = camera.read()

cv.destroyWindow("mywindow")
camera.release()
     
     
     