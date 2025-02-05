from src.pca9685 import PCA9685




class DriveMotor:
    def __init__(self, pwm, pinA, pinB):
        self._pinA = pinA
        self._pinB = pinB
        self._pwm = pwm
        self.set_speed(0)
        self.MAX_VAL = 4096
        
    def set_speed(self, speed):
        """ Expect speed in range -1 ..... 0 ..... +1 """

        if speed == 0:
            on, off = 0, 4096 # off
            self._pwm.setPWM(self._pinA, on, off)
            self._pwm.setPWM(self._pinB, on, off)
        elif speed > 0:
            on_time = int(speed * self.MAX_VAL)
            on, off = 0, on_time
            self._pwm.setPWM(self._pinA, on, off)

            on, off = on_time, self.MAX_VAL-1
            self._pwm.setPWM(self._pinB, on, off)
            
        elif speed < 0:
            on_time = int(-1 * speed * self.MAX_VAL)

            on, off = on_time, self.MAX_VAL-1
            self._pwm.setPWM(self._pinA, on, off)

            on, off = 0, on_time
            self._pwm.setPWM(self._pinB, on, off)







class Robot():
    def __init__(self):
        # Channels for the pins on the PCA9685
        pin1A = 0 # M1A -> blue   -> PCA9685 Ch 0
        pin1B = 1 # M1B -> white  -> PCA9685 Ch 1
        pin2A = 2 # M2A -> gray   -> PCA9685 Ch 2
        pin2B = 3 # M2B -> yellow -> PCA9685 Ch 3
        #pin_gripper_grip = 
        #pin_gripper_pos = 
        self.pwm = PCA9685()
        self.pwm.setPWMFreq(50.0)
        self.motor_left = DriveMotor(self.pwm, pin1A, pin1B)
        self.motor_right = DriveMotor(self.pwm, pin2A, pin2B)
        # TODO: setup 2 servos here for gripper open/shut and up/down
        # TODO: Will need to wire +ve power from batteries to pca board RED
        self.gripper_grip = 0
        self.gripper_pos = 0
        
    def set_left_tread_speed(self, speed):
        """ Set the tank robot's left tread speed:

        Parameters
        ----------
        speed : float 
            value between 0.0 and 1.0. 0.0 is stop. 1.0 is maximum speed.
        """
        self.motor_left.set_speed(speed)

    def set_right_tread_speed(self, speed):
        """ Set the tank robot's right tread speed:

        Parameters
        ----------
        speed : float 
            value between 0.0 and 1.0. 0.0 is stop. 1.0 is maximum speed.
        """
        self.motor_right.set_speed(speed)

    def stop(self):
        """ Stop the vehicle by setting the left and right tread speeds to zero. """
        self.motor_left.set_speed(0)
        self.motor_right.set_speed(0)

    def drive_forward(self, speed):
        """ Drive the tank robot forward by setting the left and right tread speeds to the value given.

        Parameters
        ----------
        speed : float 
            value between 0.0 and 1.0. 0.0 is stop. 1.0 is maximum speed.
        """
        self.motor_left.set_speed(speed)
        self.motor_right.set_speed(speed)

    def drive_backward(self, speed):
        """ Drive the tank robot backward by setting the left and right tread speeds to the negative of the
            value given.

        Parameters
        ----------
        speed : float 
            value between 0.0 and 1.0. 0.0 is stop. 1.0 is maximum speed.
        """
        self.motor_left.set_speed(-1 * speed)
        self.motor_right.set_speed(-1 * speed)

    def spin_cw(self, speed):
        """ Spin the tank robot clockwise by differential driving the left and right tread speeds based on the 
            value given.

        Parameters
        ----------
        speed : float 
            value between 0.0 and 1.0. 0.0 is stop. 1.0 is maximum speed.
        """
        self.motor_left.set_speed(speed)
        self.motor_right.set_speed(-1 * speed)

    def spin_ccw(self, speed):
        """ Spin the tank robot counter-clockwise by differential driving the left and right tread speeds based
            on the  value given.

        Parameters
        ----------
        speed : float 
            value between 0.0 and 1.0. 0.0 is stop. 1.0 is maximum speed.
        """
        self.motor_left.set_speed(-1 * speed)
        self.motor_right.set_speed(speed)

    def setup_picam_video_feed(self, addr, port):
        setup_picam_video_feed(addr, port)

    def set_gripper_grip(self, angle):
        self.gripper_grip = angle

    def set_gripper_pos(self, angle):
        self.gripper_pos = angle

        


