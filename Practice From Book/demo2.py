import cv2 as cv 
import numpy as np 
import os 

url = "http://192.168.1.73:8570/video"

def videoFromCam():
    cap = cv.VideoCapture(url)
    
    if not cap.isOpened():
        exit()
        
    cv.namedWindow('Phone Camera', cv.WINDOW_NORMAL)
    cv.resizeWindow('Phone Camera', 600, 800)
        
    while True:
        ret, frame = cap.read()
        
        if ret:
            cv.imshow('Phone Camera', frame)
            
                   
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv.destroyAllWindows()

def videoFromFile():
    root = os.getcwd()
    vidPath = os.path.join(root, 'Images/file_example_MOV_1280_1_4MB.mov')
    cap = cv.VideoCapture(vidPath)

    while cap.isOpened():
        ret, frame = cap.read()
        delay = int(1000/60)
        cv.imshow('video', frame)

        if cv.waitKey(delay) == ord('q'):
            break


def writeVideoToFile():
    cap = cv.VideoCapture(url)

    if not cap.isOpened():
        print("Could not open camera")
        return
    
    cv.namedWindow('Phone Camera', cv.WINDOW_NORMAL)


    fourcc = cv.VideoWriter_fourcc(*'XVID')

    root = os.getcwd()
    outpath = os.path.join(root, 'Images/new1Video.avi')

   
    
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    
    out = cv.VideoWriter(
            outpath,
            fourcc,
            20,
            (width, height)
        )

    print(height, width)
    
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        out.write(frame)

        cv.imshow('Phone Camera', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    videoFromCam()
    #videoFromFile()
    #writeVideoToFile()




# import cv2

# url = "http://192.168.1.73:8570/video"

# cap = cv2.VideoCapture(url)

# while True:
#     ret, frame = cap.read()

#     if not ret:
#         print("Could not read camera")
#         break

#     cv2.imshow("Phone Camera", frame)

#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break

# cap.release()
# cv2.destroyAllWindows()