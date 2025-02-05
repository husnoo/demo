import cv2
import picamera2

cv2.startWindowThread()

picam2 = picamera2.Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

while True:
    frame = picam2.capture_array()    
    cv2.imshow("Camera", frame)
    cv2.waitKey(1)

    
