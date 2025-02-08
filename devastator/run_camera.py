# The stuff from display_camera and run_ui for accessing came should come here.
# Then publish the image to /camera
# and run_ui should then be displaying it at first

import picamera2
from src.pubsub import Pub, encode_numpy
from src import config

picam2 = picamera2.Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
picam2.start()

pub = Pub(config.CAM_ADDR)

while True:
    frame = picam2.capture_array()
    pub.send('/camera', encode_numpy(frame))

