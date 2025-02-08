from src.robot import Robot
from src.pubsub import Sub

def main():
    robot = Robot()
    
    sub_left = Sub("tcp://127.0.0.1:12345", '/motor_left')
    sub_right = Sub("tcp://127.0.0.1:12345", '/motor_right')

    while True:
        speed_left = sub_left.recv()
        if speed_left is not None:
            print(f"Received on {sub.topic}: {speed_left}")
            #set_left_tread_speed(self, speed_left)

        speed_right = sub_right.recv()
        if speed_right is not None:
            print(f"Received on {sub.topic}: {speed_right}")
            #set_right_tread_speed(self, speed_right)

        #robot.stop()

