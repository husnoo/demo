import cv2
import picamera2
import threading

def camera_loop():
    cv2.startWindowThread()
    
    picam2 = picamera2.Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()

    while True:
        frame = picam2.capture_array()    
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
            break

    picam2.stop()
    cv2.destroyAllWindows()





def process(text):
    print(f"Processing: {text}")


def main():
    # Start the camera in a separate thread
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()

    while True:
        text = input("What target? ")
        if text.lower() == "exit":
            break
        process(text)
        print("OK")
