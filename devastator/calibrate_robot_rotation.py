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
import pylab

from src.robot import Robot


def analysis():
    speeds = numpy.arange(0.6,1.01,0.1)
    counts = numpy.array([5,5,10,20,20])
    ccw_time = [147.137595,  41.266779,  45.56845,   59.802386,  43.389424]
    cw_time = [149.367774,  40.58986,   43.930003,  58.371789,  42.395014]
    pylab.ion()




def main():
    robot = Robot()
    print('START')

    # Something weird - 0.2 is quite fast, 0.4,0.6 are slow, 0.8 and 1.0 are very fast.
    # 0.5 seems to stall, 0.6 is very slow
    # so maybe calibrate around 0.6-1.0
    # also 20 rotations at 0.6 will take forever. Let's just do 5.
    
    
    speeds = numpy.arange(0.6,1.01,0.1)
    counts = numpy.array([5,5,10,20,20])
    
    time_cw = numpy.zeros(len(speeds))
    time_ccw = numpy.zeros(len(speeds))
    for i, rotation_speed in enumerate(speeds):
        print(f'rotation_speed: {rotation_speed}, CCW')
        input('Press Enter to begin...')
        start = datetime.datetime.now()
        robot.spin_ccw(rotation_speed)
        input(f'Press Enter when {counts[i]} rotations have happened')
        stop = datetime.datetime.now()
        time_ccw[i] = (stop-start).total_seconds()
        robot.stop()

        print(f'rotation_speed: {rotation_speed}, CW')
        input('Press Enter to begin...')
        start = datetime.datetime.now()
        robot.spin_cw(rotation_speed)
        input(f'Press Enter when {counts[i]} rotations have happened')
        stop = datetime.datetime.now()
        time_cw[i] = (stop-start).total_seconds()
        robot.stop()
        
        print('---')

    print(time_cw, time_ccw)


#if __name__=='__main__':
#    main()


