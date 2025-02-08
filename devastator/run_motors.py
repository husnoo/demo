from src.robot import Robot
from src.pubsub import Sub

def main():
    robot = Robot()
    
    sub_left = Sub("tcp://127.0.0.1:12345", '/motor_left')
    sub_right = Sub("tcp://127.0.0.1:12345", '/motor_right')

    left = 0
    right = 0

    while True:
        speed_left = sub_left.recv()
        if speed_left is not None:
            print(f"Received on {sub.topic}: {speed_left}")
            left += speed_left
        speed_right = sub_right.recv()
        if speed_right is not None:
            print(f"Received on {sub.topic}: {speed_right}")
            right += speed_right

        print(f'setting left={left}, right={right}')
        robot.set_left_tread_speed(left)
        robot.set_right_tread_speed(right)

        left = left - 1
        right = right - 1
        if left < 0:
            left = 0
        if right < 0:
            right = 0
        if left == 0 and right == 0:
            robot.stop()


if __name__ == '__main__':
    main()

