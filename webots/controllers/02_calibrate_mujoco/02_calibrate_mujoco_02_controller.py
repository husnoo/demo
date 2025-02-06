"""02_calibrate_mujoco_01_controller controller."""

from controller import Robot, Motor, DistanceSensor, Supervisor
from controller import Robot, Emitter


import pylab
#import pynng

trajectories = {}


"""
manual guesswork showed:

mujoco
| F |  T  || L | R  |
|---+-----++---+----|
| 2 | 0   || 1 | 1  |
| 0 | 0.5 || 2 | -2 |

This means F = (L+R)
           T = (L-R)/8
Or         L = (F+8T)/2
           R = (F-8T)/2

probably want to stick to ranges F=-2,2, T=-2,2, L=-1,1, R=-1,1 (maybe - not really tried this thoroughly, but much faster and mujoco starts to skid and jump)

"""


def webots_robot():
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    emitter = robot.getDevice("emitter")
   
    #with pynng.Req0() as req:
    #    req.dial("tcp://127.0.0.1:5555")  # Connect to the server
    #    message = "World"
    #    print(f"Sending: {message}")
    #    req.send(message.encode())  # Send request
    #    print("sent")

    message = "Hello, Robot!"
    emitter.send(message.encode('utf-8'))
    
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
    
    acc = robot.getDevice('accelerometer') # m/s^2
    acc.enable(timestep)
    gyro = robot.getDevice('gyro') # rad/s
    gyro.enable(timestep)
    gps = robot.getDevice('gps') # (m, m/s)
    gps.enable(timestep)
    cam = robot.getDevice('camera')
    cam.enable(timestep)
    imu = robot.getDevice('imu')
    imu.enable(timestep)


    N = 70
    trajectories['webots'] = {}
    trajectories['webots']['time'] = numpy.zeros(N)
    trajectories['webots']['position'] = numpy.zeros((N,3))
    trajectories['webots']['velocity'] = numpy.zeros((N,3))
    trajectories['webots']['acceleration'] = numpy.zeros((N,3))
    trajectories['webots']['rotation_speed'] = numpy.zeros((N,3))
    trajectories['webots']['rotation_angle'] = numpy.zeros((N,3))
    for i in range(N):
        if robot.step(timestep) == -1:
            break
        
        # ROBOT CONTROL
        set_motors([1,1]) # radian per second [rad/s] for rotational motors # this matches linear motion in mujoco
        #set_motors([2,-2]) # radian per second [rad/s] for rotational motors - rotate to match the mujoco version

        # (m/s^2, rad/s, (m, m/s/)
        #print(i, 'acc', acc.getValues())
        #print(i, 'gyro', gyro.getValues())
        #print(i, 'gps', gps.getValues())
        #print(i, 'gpsvel', gps.getSpeed(), gps.getSpeedVector())
        trajectories['webots']['time'][i] = robot.getTime()
        trajectories['webots']['position'][i] = gps.getValues()
        trajectories['webots']['velocity'][i] = gps.getSpeedVector()
        trajectories['webots']['acceleration'][i] = acc.getValues()
        trajectories['webots']['rotation_speed'][i] = gyro.getValues()
        trajectories['webots']['rotation_angle'][i] = imu.getRollPitchYaw()










import mujoco as mj
import numpy
import os
import sys


sys.path.append('/home/nawal/data/calcifer/src')
import mujoco_viz





xml = '''
<mujoco>
   <compiler autolimits="true"/>

    <worldbody>
        <geom type="plane" size="3 3 .01"/>
        <body name="car" pos="0 0 .03">
            <freejoint/>
            <light name="top light" pos="0 0 2" mode="trackcom" diffuse=".4 .4 .4"/>

            <geom name="chasis" type="box" size="0.034 0.018 0.008" rgba=".9 .9 0 1"/>


            <body name="front-left-wheel" pos=".025 .025 0" zaxis="0 1 0">
                <joint name="front-left-wheel" damping=".05" />
                <geom type="ellipsoid" size="0.015 0.015 .005" rgba=".5 .5 1 1"/>
                <site size=".003 .010 .006" type="box" rgba=".5 1 .5 1"/>
                <site size=".010 .003 .006" type="box" rgba=".5 1 .5 1"/>
            </body>

            <body name="front-right-wheel" pos=".025 -.025 0" zaxis="0 1 0">
                <joint name="front-right-wheel" damping=".05"/>
                <geom type="ellipsoid" size="0.015 0.015 .005" rgba=".5 .5 1 1"/>
                <site size=".003 .010 .006" type="box" rgba=".5 1 .5 1"/>
                <site size=".010 .003 .006" type="box" rgba=".5 1 .5 1"/>
            </body>

            <body name="back-left-wheel" pos="-.025 .025 0" zaxis="0 1 0">
                <joint name="back-left-wheel" damping=".05" />
                <geom type="ellipsoid" size="0.015 0.015 .005" rgba=".5 .5 1 1"/>
                <site size=".003 .010 .006" type="box" rgba=".5 1 .5 1"/>
                <site size=".010 .003 .006" type="box" rgba=".5 1 .5 1"/>
            </body>

            <body name="back-right-wheel" pos="-.025 -.025 0" zaxis="0 1 0">
                <joint name="back-right-wheel" damping=".05"/>
                <geom type="ellipsoid" size="0.015 0.015 .005" rgba=".5 .5 1 1"/>
                <site size=".003 .010 .006" type="box" rgba=".5 1 .5 1"/>
                <site size=".010 .003 .006" type="box" rgba=".5 1 .5 1"/>
            </body>
            <site name="IMU" pos = "0 0 0" size="0.01" />
        </body>
    </worldbody>

    <tendon>
        <fixed name="forward">
            <joint joint="front-left-wheel" coef=".25"/>
            <joint joint="front-right-wheel" coef=".25"/>
            <joint joint="back-left-wheel" coef=".25"/>
            <joint joint="back-right-wheel" coef=".25"/>
        </fixed>
        <fixed name="turn">
            <joint joint="front-left-wheel" coef="-.25"/>
            <joint joint="front-right-wheel" coef=".25"/>
            <joint joint="back-left-wheel" coef="-.25"/>
            <joint joint="back-right-wheel" coef=".25"/>
        </fixed>
    </tendon>

    <actuator>
        <motor name="forward" tendon="forward" ctrlrange="-2 2"/>
        <motor name="turn" tendon="turn" ctrlrange="-2 2"/>
    </actuator>

    <sensor>
        <accelerometer name="accelerometer" site="IMU"/>
    </sensor>

</mujoco>
'''

def debug_xml():
    with open('/tmp/test.xml','w') as f:
        f.write(xml)




        
        





class Controller:
    def __init__(self, model, data):
        self.model = model
        self.data = data
        
    def callback(self):
        # ROBOT CONTROL
        ctrl = numpy.array([2,0]) # this matches linear motion in webots
        #ctrl = numpy.array([0,0.5]) # rotate to match the webots version
        return ctrl



def mujoco_robot():
    model = mj.MjModel.from_xml_string(xml)
    data = mj.MjData(model)
    visualiser = mujoco_viz.Visualiser(model, data)
    #visualiser = None
    
    controller = Controller(model,data)
    
    #simend = 20 #simulation time
    print_camera_config = 0

    if visualiser:
        visualiser.cam.azimuth = 90.0
        visualiser.cam.elevation = -30.0
        visualiser.cam.distance = 0.7
        visualiser.cam.lookat = numpy.array([ 0 , 0 , 0 ])

    N = 120
    trajectories['mujoco'] = {}
    trajectories['mujoco']['time'] = numpy.zeros(N)
    trajectories['mujoco']['position'] = numpy.zeros((N,3))
    trajectories['mujoco']['velocity'] = numpy.zeros((N,3))
    trajectories['mujoco']['acceleration'] = numpy.zeros((N,3))
    trajectories['mujoco']['rotation_speed'] = numpy.zeros((N,3))
    trajectories['mujoco']['rotation_angle'] = numpy.zeros((N,3))
    for i in range(N):
        if visualiser and not visualiser.should_continue():
            break

        time_prev = data.time

        try:
            data.ctrl[:] = controller.callback()
        except:
            print('data.ctrl.shape: ', data.ctrl.shape)

        while (data.time - time_prev < 1.0/60.0):
            mj.mj_step(model, data)

        #print camera configuration (help to initialize the view)
        if visualiser and print_camera_config == 1:
            print('cam.azimuth =', visualiser.cam.azimuth,';','cam.elevation =',
                  visualiser.cam.elevation,';','cam.distance = ', visualiser.cam.distance)
            print('cam.lookat =numpy.array([', visualiser.cam.lookat[0],',', visualiser.cam.lookat[1],',',
                  visualiser.cam.lookat[2],'])')
        if visualiser:
            visualiser.update_scene()


        #print(data.qpos[7:])
        #x y z position of the free joint
        # print(data.qpos[0])
        # print(data.qpos[1])
        # print(data.qpos[2])
        #print(data.site_xpos[0]);
        # print('yaw = ',euler[2]);

        #if (data.time>=simend):
        #    break;
        trajectories['mujoco']['time'][i] = data.time
        trajectories['mujoco']['position'][i,:] = (data.qpos[0], data.qpos[1], data.qpos[2])
        trajectories['mujoco']['velocity'][i,:] = data.qvel[0:3]
        trajectories['mujoco']['acceleration'][i,:] = data.sensor('accelerometer').data
        trajectories['mujoco']['rotation_speed'][i,:] = data.qvel[3:6]

        quat = numpy.array([data.qpos[3],data.qpos[4],data.qpos[5],data.qpos[6]])
        euler = mujoco_viz.quat2euler(quat)
        trajectories['mujoco']['rotation_angle'][i,:] = euler / 180.0 * numpy.pi




    
    del model
    del data
    del visualiser




def main():

    



        
    webots_robot()
    debug_xml()
    mujoco_robot()
    #exit()



    if 1:
        pylab.ion()


        pylab.figure()

        distance_scale = 0.10
        trajectories['webots']['time'] = trajectories['webots']['time'] - trajectories['webots']['time'][0]

        pylab.subplot(2,3,1)
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['position'][:,0], color='red', label='wx')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['position'][:,1], color='blue', label='wy')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['position'][:,2], color='black', label='wz')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['position'][:,0]*distance_scale, color='red', ls='--', label='mx')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['position'][:,1]*distance_scale, color='blue', ls='--',label='my')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['position'][:,2]*distance_scale, color='black', ls='--',label='mz')
        pylab.title('distance')
        pylab.legend()

        pylab.subplot(2,3,2)
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['velocity'][:,0], color='red', label='x')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['velocity'][:,1], color='blue', label='y')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['velocity'][:,2], color='black', label='z')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['velocity'][:,0], color='red', ls='--', label='mx')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['velocity'][:,1], color='blue', ls='--',label='my')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['velocity'][:,2], color='black', ls='--',label='mz')
        pylab.title('velocity')
        pylab.legend()

        pylab.subplot(2,3,3)
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['acceleration'][:,0], color='red', label='x')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['acceleration'][:,1], color='blue', label='y')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['acceleration'][:,2], color='black', label='z')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['acceleration'][:,0], color='red', ls='--', label='mx')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['acceleration'][:,1], color='blue', ls='--',label='my')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['acceleration'][:,2], color='black', ls='--',label='mz')
        pylab.title('acceleration')
        pylab.legend()

        pylab.subplot(2,3,4)
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['rotation_speed'][:,0], color='red', label='x')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['rotation_speed'][:,1], color='blue', label='y')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['rotation_speed'][:,2], color='black', label='z')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['rotation_speed'][:,0], color='red', ls='--', label='mx')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['rotation_speed'][:,1], color='blue', ls='--',label='my')
        pylab.plot(trajectories['mujoco']['time'],trajectories['mujoco']['rotation_speed'][:,2], color='black', ls='--',label='mz')
        pylab.title('rotation_speed')
        pylab.legend()

        pylab.subplot(2,3,5)
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['rotation_angle'][:,0], color='red', label='x')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['rotation_angle'][:,1], color='blue', label='y')
        pylab.plot(trajectories['webots']['time'],trajectories['webots']['rotation_angle'][:,2], color='black', label='z')
        pylab.plot(trajectories['mujoco']['time'], -trajectories['mujoco']['rotation_angle'][:,0], color='red', ls='--', label='mx')
        pylab.plot(trajectories['mujoco']['time'], -trajectories['mujoco']['rotation_angle'][:,1], color='blue', ls='--',label='my')
        pylab.plot(trajectories['mujoco']['time'], -trajectories['mujoco']['rotation_angle'][:,2], color='black', ls='--',label='mz')
        pylab.title('rotation angle')
        pylab.legend()


        input()
    
    


    
    

if __name__=='__main__':
    main()




