import cv2
import threading
from src.pubsub import Pub, Sub
from src.pubsub import decode_numpy
from src import config

def camera_loop():
    cv2.startWindowThread()
    sub_cam = Sub(config.CAM_ADDR, '/camera')
    #sub_cam = Sub(config.CAM_LABELLED_ADDR, '/camera_labelled')
    while True:
        frame = sub_cam.recv()
        if frame is not None:
            cv2.imshow("Camera", decode_numpy(frame))
        if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
            break
    cv2.destroyAllWindows()


def main():
    # Start the camera viewer in a separate thread
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    pub_target = Pub(config.TARGET_ADDR)

    
    while True:
        text = input("What target? ")
        if text.lower() == "exit":
            break
        pub_target.send('/target', text)
        print("OK")

if __name__ == '__main__':
    main()

