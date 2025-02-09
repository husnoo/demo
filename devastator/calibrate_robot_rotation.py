"""
Calibrate robot's rotation


>>> 
>>> 
>>> robot.spin_cw(0.5)
>>> robot.spin_ccw(0.5)

Over the range of speeds from 0 to 1, say in steps of 0.2, count how long it takes to make say 10-20 turns.
Calculate and plot degrees/second for each rotation speed.
"""

import datetime
import time
import numpy

#from src.robot import Robot


def main():
    #robot = Robot()
    print('START')

    speeds = numpy.arange(0.2,1.01,0.2)
    time_cw = numpy.zeros(len(speeds))
    time_ccw = numpy.zeros(len(speeds))
    for i, rotation_speed in enumerate(speeds):
        print(f'rotation_speed: {rotation_speed}, CW')
        input('Press Enter to begin...')
        start = datetime.datetime.now()
        #robot.spin_cw(rotation_speed)
        input('Press Enter when 20 rotations have happened')
        stop = datetime.datetime.now()
        time_cw[i] = (stop-start).total_seconds()

        print(f'rotation_speed: {rotation_speed}, CCW')
        input('Press Enter to begin...')
        start = datetime.datetime.now()
        #robot.spin_cw(-rotation_speed)
        input('Press Enter when 20 rotations have happened')
        stop = datetime.datetime.now()
        time_ccw[i] = (stop-start).total_seconds()
        
        print('---')

    print(time_cw, time_ccw)


if __name__=='__main__':
    main()


