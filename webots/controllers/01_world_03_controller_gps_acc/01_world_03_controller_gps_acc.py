""" 03_controller_gps_acc """
from controller import Robot

import pylab
import numpy


robot = Robot()
timestep = int(robot.getBasicTimeStep())
print()

#cam = robot.getDevice('camera')
#cam.enable(timestep)


acc = robot.getDevice('accelerometer') # m/s^2
acc.enable(timestep)
gyro = robot.getDevice('gyro') # rad/s
gyro.enable(timestep)
gps = robot.getDevice('gps') # (m, m/s)
gps.enable(timestep)


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


def set_motors(xs):
    for motor in left_motors:
        motor.setVelocity(xs[0])
    for motor in right_motors:
        motor.setVelocity(xs[1])
    

acc_arr = []
gyro_arr = []
gps_arr = []
gps_vel_arr = []
gps_vel_vec_arr = []

#while robot.step(timestep) != -1:
N = 50
for i in range(N):
    if robot.step(timestep) == -1:
        break
    #move_forward(10)
    #rotate_left(10)
    #rotate_right(2)
    set_motors([10,10])

    # (m/s^2, rad/s, (m, m/s/)
    print(i, 'acc', acc.getValues())
    print(i, 'gyro', gyro.getValues())
    print(i, 'gps', gps.getValues())
    print(i, 'gpsvel', gps.getSpeed(), gps.getSpeedVector())

    acc_arr.append(acc.getValues())
    gyro_arr.append(gyro.getValues())
    gps_arr.append(gps.getValues())
    gps_vel_arr.append(gps.getSpeed())
    gps_vel_vec_arr.append(gps.getSpeedVector())
        
    #0 acc [0.0004176030086272211, -0.0007379078923794832, 9.799259397088786]
    #0 gps [-3.149413776645793e-10, 5.736683386910233e-10, -1.0998444791094492e-05]
    #8 gyro [0.0003525941266113061, -2.970808642280195e-07, -1.7639748951589503e-05]
    #9 gpsvel 0.14007441085831165 [-0.14007441085695937, 6.150071619416907e-07, -2.4701087913521578e-08]



# plot these values
acc_arr = numpy.array(acc_arr)
gyro_arr = numpy.array(gyro_arr)
gps_arr = numpy.array(gps_arr)
gps_vel_arr = numpy.array(gps_vel_arr)
gps_vel_vec_arr = numpy.array(gps_vel_vec_arr)
t = numpy.arange(N) * timestep / 1000

pylab.ion()
pylab.figure()

pylab.subplot(2,2,1)
pylab.plot(t, acc_arr[:,0], color='r', label='x')
pylab.plot(t, acc_arr[:,1], color='g', ls='--', label='y')
pylab.plot(t, acc_arr[:,2], color='b', label='z')
pylab.legend()
pylab.title('acc')

pylab.subplot(2,2,2)
pylab.plot(t, gyro_arr[:,0], color='r', label='x')
pylab.plot(t, gyro_arr[:,1], color='g', ls='--', label='y')
pylab.plot(t, gyro_arr[:,2], color='b', label='z')
pylab.legend()
pylab.title('gyro_arr')

pylab.subplot(2,2,3)
pylab.plot(t, gps_arr[:,0], color='r', label='x')
pylab.plot(t, gps_arr[:,1], color='g', ls='--', label='y')
pylab.plot(t, gps_arr[:,2], color='b', label='z')
pylab.legend()
pylab.title('gps_arr')

pylab.subplot(2,2,4)
pylab.plot(t, gps_vel_vec_arr[:,0], color='r', label='x')
pylab.plot(t, gps_vel_vec_arr[:,1], color='g', ls='--', label='y')
pylab.plot(t, gps_vel_vec_arr[:,2], color='b', label='z')
pylab.plot(t, gps_vel_arr, color='k', label='v')
pylab.legend()
pylab.title('gps_vel_arr')

input('')







    


