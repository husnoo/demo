import cv2
import threading
from src.pubsub import Pub, Sub
from src.pubsub import decode_numpy

def camera_loop():
    cv2.startWindowThread()
    sub_cam = Sub("tcp://127.0.0.1:12345", '/camera')
    #sub_cam = Sub("tcp://127.0.0.1:12345", '/camera_labelled')
    while True:
        frame = sub_cam.recv()
        if frame is not None:
            cv2.imshow("Camera", decode_numpy(frame))
        if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
            break
    cv2.destroyAllWindows()


def main():
    # Start the camera in a separate thread
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    pub = Pub("tcp://127.0.0.1:12345")

    
    while True:
        text = input("What target? ")
        if text.lower() == "exit":
            break
        pub.send('/target', text)
        print("OK")

if __name__ == '__main__':
    main()

