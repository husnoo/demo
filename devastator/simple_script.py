'''
Simple script to take a target, take image from camera, pass to VLM, get location,
and steer robot to the object.

Problem: VLM responds slowly, and we need to get robot to move very slowly and not just overshoot.

Will make use of robot calibration.

Will also use VLM in blocking mode to simplify.

Will assume distance to target is 2m.

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
    
    def process(self, img, prompt, block=False):
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
                ret_msg = self.socket.recv(block=block)
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
    # So if the distance is about 2m, and an object is about 30cm to the right, we need to move 
    # 180*numpy.arctan(30/200)/numpy.pi = 8.530 degrees
    # the VM takes about 2-3 seconds to respond, so we don't want to move more than  8.530 / 3 == 2.84deg/s
    # this is around 0.567 in terms of driving speed
    # s=0.60, 12deg/s roughly

    # distance to target ~176cm, ~22cm off center
    # image is 640x480, the bottle is 424px away from left
    # or (- 424 (/ 640 2))=104px off center
    # so 104px==22cm, and angle is arctan(22/176)=0.1243rad=7.12degrees
    # at s=0.6, we would rotate at 12deg/s, so for 7.12deg we need to rotate for (/ 7.12 12)=0.59seconds
    
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
        response = vlm.process(frame, prompt, block=True)
        if response['ret'] and 'objects' in response['ret']:
            # we have objects
            objects_detected = []
            for obj in response['ret']['objects']:
                if 'xyxy' in obj and target in obj['name']:
                    print(f"target: {target}, name: {obj['name']}")
                    objects_detected.append(obj)
        
        ## draw box around target
        for i,obj in enumerate(objects_detected):
            frame = numpy.copy(frame)
            start_point = [obj['xyxy'][0],obj['xyxy'][1]]
            end_point = [obj['xyxy'][2],obj['xyxy'][3]]
            color = (255, 0, 0)
            color = color[::-1]
            thickness = 2
            cv2.rectangle(frame, start_point, end_point, color, thickness)
            cv2.putText(
                frame, obj['name'], start_point, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
            # centerline
            center_x = int(frame.shape[1] / 2)
            cv2.line(frame,(center_x,0),(center_x,frame.shape[0]),(255,0,0),1)

        # update camera display
        cv2.imshow("Camera", frame)
        cv2.waitKey(1)

        # steer robot
        dx = 0
        for i,obj in enumerate(objects_detected):
            if target in obj['name']:
                x = (obj['xyxy'][0] + obj['xyxy'][2]) / 2.0
                y = (obj['xyxy'][1] + obj['xyxy'][3]) / 2.0
                dx = x - frame.shape[1] / 2
                print(i, x, y, frame.shape, dx)
                break # keep only first matching target
        print('dx=', dx)
        #dx = 104 # px
        #dx_cm = (dx / 104) * 22
        #distance = 176
        #angle = numpy.arctan(dx_cm/distance) * 180/numpy.pi

        if numpy.abs(dx) > 20:
            angle = numpy.arctan(22/176) * (dx / 104) * 180 / numpy.pi
            print(angle)
            s = 0.60
            w = 25 #deg/s
            t = numpy.abs(angle / w)
            sign = numpy.sign(angle)
            start = datetime.datetime.now()
            robot.set_left_tread_speed(-s * sign)
            robot.set_right_tread_speed(s * sign)
            print('dx={:.3f}, angle={:.2f}, t={}'.format(dx, angle, t))
            while 1:
                now = datetime.datetime.now()
                if (now-start).total_seconds() >= t:
                    robot.stop()
                    break
        else:
            robot.set_left_tread_speed(-0.8)
            robot.set_right_tread_speed(-0.8)


        

        

if __name__ == '__main__':
    robot = Robot()    
    #try:
    main(robot)
    #except:
    #pass
    
    robot.stop()
