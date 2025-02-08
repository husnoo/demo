'''
  - takes text targets from `/target`
  - takes image from `/camera`
  - calls paligemma server for location information
  - publishes `/camera_labelled`
  - publishes `/motor_left` and `/motor_right`
'''

import datetime

from src.pubsub import Pub, Sub
from src.pubsub import encode_numpy, decode_numpy

import pynng
import msgpack

class VLMProxy:
    def __init__(self, url):
        self.url = url
        self.socket = pynng.Pair0()
        self.socket.dial(self.url)
        self.first = True
        self.last_reply = datetime.datetime.now()
    
    def process(self, img, prompt):
        # TODO: rewrite this with the pubsub/encode/decode approach - will need to update the paligemma code too
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
            # check if there's an answer yet, then send again
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
    sub_cam = Sub("tcp://127.0.0.1:12345", '/camera')
    sub_target = Sub("tcp://127.0.0.1:12345", '/target')
    pub = Pub("tcp://127.0.0.1:12345")
    vlm = VLMProxy("tcp://192.168.0.52:8089")

    target = None # we keep a long-lived variable with the current target and update if new one comes through
    while 1:

        target_ = sub_target.recv()
        if target_ is not None:
            target = target_
        
        frame = sub_cam.recv())
        if frame is not None:
            frame = decode_numpy(frame)
            print(frame.shape)
        if target is not None and frame is not None:
            prompt = 'detect ' + target
            response = vlm.process(frame, prompt)
            if response['ret'] is not None and 'objects' in response['ret']:
                if len(response['ret']['objects']) > 0:
                    for obj in response['ret']['objects']:
                        if 'xyxy' in obj:
                            #objects_detected[prompt] = obj
                            print('obj:', obj)


    #pub.send('/camera_labelled', encode_numpy(frame))
    #pub.send('/motor_left', 1.0)
    #pub.send('/motor_right', 1.0)
    






if __name__ == '__main__':
    main()

