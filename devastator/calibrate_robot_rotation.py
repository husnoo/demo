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
try:
    from src.robot import Robot
except:
    pass

def analysis():
    speeds = numpy.array([0.57, 0.58, 0.59, 0.6, 0.7, 0.8, 0.9, 1. ])
    counts = numpy.array([1,1,1,5,5,10,20,20])
    ccw_time = numpy.array([77.96, 59.40, 47.37, 147.13,  41.26,  45.56,   59.80,  43.38])
    cw_time = numpy.array([43.63, 45.01, 37.52, 149.36,  40.58,   43.93,  58.37,  42.39])
    
    avg_time = (ccw_time + cw_time) / 2.0
    time_per_rotation = avg_time / counts
    degrees_per_second = 360 / time_per_rotation

    coeffs = numpy.polyfit(speeds, degrees_per_second, 2)
    qfunc = numpy.poly1d(coeffs)
    print("coeffs:", coeffs)
    # coeffs: [237.70067705   8.99598535 -78.82208964]
    # coeffs: [252.2557391  -15.07425675 -69.11377422]

    speeds_fit = numpy.linspace(0.55, 1, 100)
    degrees_fit = qfunc(speeds_fit)

    pylab.ion()
    pylab.plot(speeds, degrees_per_second, marker='s')
    pylab.plot(speeds_fit, degrees_fit, label='Fitted', color='red')
    pylab.xlabel('speed')
    pylab.ylabel('deg/s')
    pylab.grid(True)

    # So if the distance is about 2m, and an object is about 30cm to the right, we need to move 
    # 180*numpy.arctan(30/200)/numpy.pi = 8.530 degrees
    # the VM takes about 2-3 seconds to respond, so we don't want to move more than  8.530 / 3 == 2.84deg/s
    # this is around 0.567 in terms of driving speed
    

def main():
    robot = Robot()
    print('START')

    # Something weird - 0.2 is quite fast, 0.4,0.6 are slow, 0.8 and 1.0 are very fast.
    # 0.5 seems to stall, 0.6 is very slow
    # so maybe calibrate around 0.6-1.0
    # also 20 rotations at 0.6 will take forever. Let's just do 5.
    
    
    #speeds = numpy.arange(0.6,1.01,0.1)
    #counts = numpy.array([5,5,10,20,20])

    speeds = numpy.array([0.57, 0.58, 0.59])
    counts = numpy.array([1,1,1])
    
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


if __name__=='__main__':
    main()


