'''
  - takes text targets from `/target`
  - takes image from `/camera`
  - calls paligemma server for location information
  - publishes `/camera_labelled`
  - publishes `/motor_left` and `/motor_right`
'''

import datetime
import time

from src.pubsub import Pub, Sub
from src.pubsub import encode_numpy, decode_numpy
from src import config

import pynng
import msgpack
import numpy
import cv2

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
    sub_cam = Sub(config.CAM_ADDR, '/camera')
    sub_target = Sub(config.TARGET_ADDR, '/target')
    pub_cam_labelled = Pub(config.CAM_LABELLED_ADDR)
    pub_motors = Pub(config.MOTORS_ADDR)

    vlm = VLMProxy("tcp://192.168.0.52:8089")

    # we keep a long-lived variable with the current target/frame and update if new one comes through
    target = None 
    frame = None
    objects_detected = []
    while 1:
        target_ = sub_target.recv()
        if target_ is not None:
            target = target_
            print(f'new target: {target}')

        frame_ = sub_cam.recv()
        if frame_ is not None:
            frame = decode_numpy(frame_)


        # TODO: Is this calling too often? It's meant to wait until there's been a reply
        if target is not None and frame is not None:
            prompt = 'detect ' + target
            #print('call vlm...')
            response = vlm.process(frame, prompt)

            #print('response:', response)
            # Need to check multiple times and only make a new call if free
            if response['ret'] is not None and 'objects' in response['ret']:
                if len(response['ret']['objects']) > 0:
                    objects_detected = []
                    for obj in response['ret']['objects']:
                        if 'xyxy' in obj and target in obj['name']:
                            print(f"target: {target}, name: {obj['name']}")
                            objects_detected.append(obj)
                            #print('obj:', obj)





        # draw frame around object
        for obj in objects_detected:
            frame_ = numpy.copy(frame)
            start_point = [obj['xyxy'][0],obj['xyxy'][1]]
            end_point = [obj['xyxy'][2],obj['xyxy'][3]]
            color = (255, 0, 0)
            color = color[::-1]
            thickness = 2
            cv2.rectangle(frame_, start_point, end_point, color, thickness)
            cv2.putText(frame_, obj['name'], start_point, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
            # publish it
            pub_cam_labelled.send('/camera_labelled', encode_numpy(frame_))

            mid_point = ((start_point[0] + end_point[0]) / 2 , (start_point[1] + end_point[1]) / 2)
            print('midpoint:', mid_point, ', frame.shape:', frame_.shape)
            pos_x = mid_point[0] - frame_.shape[0]/2

            if numpy.abs(pos_x) > 10:
                #rotate_right(pos_x/100)
                left = pos_x/10000
                right = -pos_x/10000
            else:
                #move_forward(10)
                left = 1.0
                right = 1.0

            pub_motors.send('/motor_left', left)
            pub_motors.send('/motor_right', right)

            
        print('end of one cycle')
        time.sleep(1)
        
    






if __name__ == '__main__':
    main()

