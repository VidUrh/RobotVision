"""
This is the main file for the robot thread. It is responsible for starting the robot and
controlling it.
"""
import logging
import time
import threading
import sys
import os
import cv2
import numpy as np
import pickle
import math

from parameters import *
from objectDetectionThread import ObjectDetectionThread

from xarm.wrapper import XArmAPI


def pickup(obj):
    """
    This function controls the robot arm to pick up an object
    """
    robot.set_servo_angle(angle=[90, 0, 90, 0.0, 90, 0], speed=100, acceleration=5, is_radian=False, wait=True)
    time.sleep(1)
    robot.set_position(x=0, y = 0,z = -5.5, speed=20, relative = True, wait=True)
    robot.set_position(x=obj.x, y=obj.y,z = -20, speed=80, wait=True)
    robot.set_position(x=0, y = 0,z = 10.5, speed=20, relative = True, wait=True)
    return
    robot.open_lite6_gripper()
    time.sleep(1)
    robot.set_position(x=0, y = 0,z = -30, speed=20, relative = True, wait=True)
    robot.set_servo_angle(angle=[90, 0, 90, 0.0, 90, 0], speed=100, acceleration=5, is_radian=False, wait=True)

    robot.close_lite6_gripper()
    time.sleep(1)



objDet = ObjectDetectionThread()
objDet.start()

if ROBOT is True:
        
    robot = XArmAPI(ROBOT_IP)
    robot.reset(wait=True)
    robot.motion_enable(enable=True)
    robot.set_mode(0)
    robot.set_state(state=0)
    time.sleep(1)


    while 1:
        
        robot.set_servo_angle(angle=[90, 0, 90, 0.0, 90, 0], speed=100, acceleration=5, is_radian=False, wait=True)

        objs = objDet.getObjects()
        for obj in objs:
            print(obj)
            pickup(obj)
            break
        break