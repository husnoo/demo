import cv2
from src.pubsub import Pub, Sub
from src.pubsub import decode_numpy
from src import config

def main():
    cv2.startWindowThread()
    sub_cam_unlabelled = Sub(config.CAM_ADDR, '/camera')
    sub_cam_labelled = Sub(config.CAM_LABELLED_ADDR, '/camera_labelled')
    
    while True:
        frame = sub_cam_labelled.recv()
        if frame is not None:
            sub_cam_unlabelled = None # we only use the unlabelled version at the start

        if frame is None and sub_cam_unlabelled is not None:
            frame = sub_cam_unlabelled.recv()
        
        if frame is not None:
            cv2.imshow("Camera", decode_numpy(frame))
        if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
