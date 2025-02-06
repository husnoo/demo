"""simple_controller_02 controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot

# create the Robot instance.
#robot = Robot()

# get the time step of the current world.
#timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
#while robot.step(timestep) != -1:
#    # Read the sensors:
#        # Enter here functions to read sensor data, like:
#    #  val = ds.getValue()#
#
#    # Process sensor data here.#
#
#    # Enter here functions to send actuator commands, like:
#    #  motor.setPosition(10.0)
#    pass
# Enter here exit cleanup code.


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


while robot.step(timestep) != -1:
    move_forward(10)
    #rotate_left(10)
    #rotate_right(2)




