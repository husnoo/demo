"""01_simple_controller controller."""


from controller import Robot
import numpy
import cv2
import pynng
import msgpack

import datetime




class VLMProxy:
    def __init__(self):
        self.url = "tcp://192.168.0.52:8089"
        self.socket = pynng.Pair0()
        self.socket.dial(self.url)
        self.first = True
        self.last_reply = datetime.datetime.now()
    
    def process(self, img, prompt):

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
            # TODO: check if there's an answer yet, then send again
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















robot = Robot()
timestep = int(robot.getBasicTimeStep())

cam = robot.getDevice('camera')
cam.enable(timestep)
left_motors = []
right_motors = []

for motor_name in [
        'wheel_motor00','wheel_motor01','wheel_motor02','wheel_motor03', 'wheel_motor04',
        'wheel_motor05','wheel_motor06','wheel_motor07','wheel_motor08','wheel_motor09',]:
    motor = robot.getDevice(motor_name)
    motor.setPosition(float('inf'))
    motor.setVelocity(0)
    #motor.setVelocity(-20)
    if motor_name < 'wheel_motor05':
        left_motors.append(motor)
    else:
        right_motors.append(motor)        






def move_forward(v):
    for motor in left_motors:
        motor.setVelocity(-v)
    for motor in right_motors:
        motor.setVelocity(-v)


def move_backward(v):
    for motor in left_motors:
        motor.setVelocity(v)
    for motor in right_motors:
        motor.setVelocity(v)


def rotate_right(theta):
    for motor in left_motors:
        motor.setVelocity(-theta)
    for motor in right_motors:
        motor.setVelocity(theta)
    
def rotate_left(theta):
    for motor in left_motors:
        motor.setVelocity(theta)
    for motor in right_motors:
        motor.setVelocity(-theta)




#import pdb
#pdb.set_trace()
# len(cam.getImage()) == 307200
# image = numpy.frombuffer(cam.getImage(), numpy.uint8).reshape((cam.getHeight(), cam.getWidth(), 4))
# image.shape == (240, 320, 4)
cv2.startWindowThread()
cv2.namedWindow("preview")


vlm = VLMProxy()

objects_detected = {}

while robot.step(timestep) != -1:
    image = numpy.frombuffer(cam.getImage(), numpy.uint8).reshape((cam.getHeight(), cam.getWidth(), 4))[:,:,0:3]

    #prompt = 'detect rubber duck;'
    prompt = 'detect ball;'
    
    response = vlm.process(image, prompt)
    
    if response['ret'] is not None and 'objects' in response['ret']:
        if len(response['ret']['objects']) > 0:
            for obj in response['ret']['objects']:
                if 'xyxy' in obj:
                    objects_detected[prompt] = obj

    for key in objects_detected:
        obj = objects_detected[key]
        image = numpy.copy(image)
        start_point = [obj['xyxy'][0],obj['xyxy'][1]]
        end_point = [obj['xyxy'][2],obj['xyxy'][3]]
        color = (255, 0, 0)
        color = color[::-1]
        thickness = 2
        cv2.rectangle(image, start_point, end_point, color, thickness)
        cv2.putText(image, obj['name'], start_point, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)

    cv2.imshow("preview", image)
    cv2.waitKey(timestep)

    if len(objects_detected) > 0:
        key = list(objects_detected.keys())[0]
        #print(objects_detected)
        # {'detect rubber duck;': {'content': '<loc0681><loc0841><loc0861><loc0985> rubber duck', 'xyxy': [263, 160, 308, 202], 'mask': None, 'name': 'rubber duck'}}
        obj = objects_detected[key]
        start_point = [obj['xyxy'][0],obj['xyxy'][1]]
        end_point = [obj['xyxy'][2],obj['xyxy'][3]]
        x = (start_point[0] + end_point[0])/2
        y = (start_point[1] + end_point[1])
        pos_x = x - cam.getWidth()/2
    else:
        pos_x = 0
    

    #move_forward(10)
    #rotate_left(10)
    #rotate_right(2)

    if numpy.abs(pos_x) > 10:
        rotate_right(pos_x/100)
    else:
        move_forward(10)
    
    

