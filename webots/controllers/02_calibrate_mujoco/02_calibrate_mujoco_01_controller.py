"""02_calibrate_mujoco_01_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot





robot = Robot()


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

def set_motors(xs):
    for motor in left_motors:
        motor.setVelocity(xs[0])
    for motor in right_motors:
        motor.setVelocity(xs[1])




timestep = int(robot.getBasicTimeStep())
#acc = robot.getDevice('accelerometer') # m/s^2
#acc.enable(timestep)
#gyro = robot.getDevice('gyro') # rad/s
#gyro.enable(timestep)
#gps = robot.getDevice('gps') # (m, m/s)
#gps.enable(timestep)
cam = robot.getDevice('camera')
cam.enable(timestep)



N = 70
for i in range(N):
    if robot.step(timestep) == -1:
        break
    set_motors([10,10]) # radian per second [rad/s] for rotational motors

    # (m/s^2, rad/s, (m, m/s/)
    #print(i, 'acc', acc.getValues())
    #print(i, 'gyro', gyro.getValues())
    #print(i, 'gps', gps.getValues())
    #print(i, 'gpsvel', gps.getSpeed(), gps.getSpeedVector())













