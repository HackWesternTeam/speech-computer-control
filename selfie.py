import cv2
from datetime import date
import time
import os
if not os.path.exists('pictures'):
    os.makedirs('pictures')
cap = cv2.VideoCapture(0)
cap.set(3,640) #width=640
cap.set(4,480) #height=480
today = date.today()


if cap.isOpened():
    _,frame = cap.read()
    cap.release() #releasing camera immediately after capturing picture
    print("say cheese")
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    if _ and frame is not None:
        cv2.imwrite('pictures/selfie_'+str(today)+'.jpg', frame)