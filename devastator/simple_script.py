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






def main(robot):

    cv2.startWindowThread()
    picam2 = picamera2.Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
    picam2.start()

    target = 'red bottle'

    vlm = VLMProxy('tcp://192.168.0.52:8089')
    prompt = 'detect ' + target
    objects_detected = []
    while True:
        frame = picam2.capture_array()
        # look for target
        response = vlm.process(frame, prompt)
        if response['ret'] and 'objects' in response['ret']:
            # we have objects
            objects_detected = []
            for obj in response['ret']['objects']:
                if 'xyxy' in obj and target in obj['name']:
                    print(f"target: {target}, name: {obj['name']}")
                    objects_detected.append(obj)


        # steer robot
        #robot.set_left_tread_speed(speed)
        #robot.set_right_tread_speed(speed)
        for i,obj in enumerate(objects_detected):
            if target in obj['name']:
                x = (obj['xyxy'][0] + obj['xyxy'][2]) / 2.0
                y = (obj['xyxy'][1] + obj['xyxy'][3]) / 2.0
                dx = x - frame.shape[1] / 2
                print(i, x, y, frame.shape, dx)
                #0 406.0 254.5 (480, 640, 3) 85.5
                speed = 0.55 + (-dx/100/5.0)
                robot.set_left_tread_speed(speed)
                robot.set_right_tread_speed(-speed)
                
                
        # draw box around target
        for i,obj in enumerate(objects_detected):
            frame = numpy.copy(frame)
            start_point = [obj['xyxy'][0],obj['xyxy'][1]]
            end_point = [obj['xyxy'][2],obj['xyxy'][3]]
            color = (255, 0, 0)
            color = color[::-1]
            thickness = 2
            cv2.rectangle(frame, start_point, end_point, color, thickness)
            cv2.putText(frame, obj['name'], start_point, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)

        # update camera display
        cv2.imshow("Camera", frame)
        cv2.waitKey(1)


if __name__ == '__main__':
    robot = Robot()    
    try:
        main(robot)
    except:
        pass
    
    robot.stop()
