# The stuff from display_camera and run_ui for accessing came should come here.
# Then publish the image to /camera
# and run_ui should then be displaying it at first

import picamera2
from src.pubsub import Pub, encode_numpy

picam2 = picamera2.Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

pub = Pub("tcp://127.0.0.1:12345")

while True:
    frame = picam2.capture_array()
    pub.send('/camera', encode_numpy(frame))

