'''
Simple script to take a target, take image from camera, pass to VLM, get location,
and steer robot to the object.

Problem: VLM responds slowly, and we need to get robot to move very slowly and not just overshoot.

Would it be worth calibrating the robot rotation?

'''

import datetime
import time

import cv2
import picamera2
import pynng
import msgpack
import numpy

from src.robot import Robot


class VLMProxy:
    def __init__(self, url):
        self.url = url
        self.socket = pynng.Pair0()
        self.socket.dial(self.url)
        self.first = True
        self.last_reply = datetime.datetime.now()
    
    def process(self, img, prompt):
        # TODO: rewrite this with the pubsub/encode/decode approach - will need to update the paligemma code too
        print('VLMProxy process img=', img.shape, img.dtype)
        request_data = msgpack.packb({
            'image': img[:,:,::-1].tobytes(),
            "image_shape": img.shape,
            "prompt": prompt,
            "max-tokens": 512,
        })
        if self.first:
            self.socket.send(request_data)
            self.first = False
            ret_data = None # we don't have an answer yet
        else:
            # check if there's an answer yet, then send new one
            try:
                ret_msg = self.socket.recv(block=False)
                ret_data = msgpack.unpackb(ret_msg)
                self.last_reply = datetime.datetime.now()
                self.socket.send(request_data)
            except pynng.TryAgain as err:
                # no reply yet, we wait.
                ret_data = {
                    'seconds-since-last-reply': (datetime.datetime.now()-self.last_reply).total_seconds()
                }
        return {'response': 'ok', 'ret': ret_data}






def main():
    robot = Robot()
    #robot.set_left_tread_speed(speed)
    #robot.set_right_tread_speed(speed)

    cv2.startWindowThread()
    picam2 = picamera2.Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB888', "size": (640, 480)}))
    picam2.start()

    while True:
        frame = picam2.capture_array()
        # look for target



        # steer robot



        
        # draw box around target
        
        # update camera display
        cv2.imshow("Camera", frame)
        cv2.waitKey(1)


    


















    
