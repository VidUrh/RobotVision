"""
Skripta, ki vsebuje robotski cikel. Skrbi za premikanje robota preko XArm API-ja

PREDPRIPRAVA:
- [ ] Robot zažene zaznavo objektov
- [ ] Robot resetira svoje errorje in postavi na "ZERO" position

CIKEL:
- [ ] Robot se umakne na "home" pozicijo
- [ ] Robot prebere koordinate objektov, če ni nobenega, čez 5 sekund poskusi znova
- [ ] Robot vsak objekt pobere in spusti na predoločenem mestu
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
from nozzleDetection import NozzleDetector

from xarm.wrapper import XArmAPI


class Robot:
    def __init__(self, ip, logger):
        self.logger = logger
        self.logger.info("Connecting to robot...")
        self.robot = XArmAPI(ip)
        self.robot.clean_error()
        self.robot.motion_enable(enable=True)
        self.robot.set_mode(0)
        self.robot.set_state(state=0)
        self.logger.info("Robot connected!")

    # move roboto set default parameters
    def move(self, x=None, y=None, z=None, roll=None, pitch=None, yaw=None, speed=SPEED_MIDDLE, mvacc=None, wait=True, timeout=0):
        self.robot.set_position(x, y, z, roll, pitch, yaw, speed=speed, mvacc=mvacc, wait=wait, timeout=timeout)

    def pick(self):
        self.robot.open_lite6_gripper()
        time.sleep(1)

    def drop(self):
        self.robot.close_lite6_gripper()

    def home(self):
        self.robot.move_gohome(wait=True)

    def move_todrop(self):
        self.robot.set_servo_angle(
            angle=[90, 0, 90, 0.0, 90, 0], speed=SPEED_FAST, acceleration=5, is_radian=False, wait=True)

    def close(self):
        self.robot.disconnect()

    def standby(self):
        self.robot.set_servo_angle(
            angle=[90, 0, 90, 0.0, 90, 0], speed=SPEED_FAST, acceleration=5, is_radian=False, wait=True)

    def getPosition(self):
        return self.robot.get_position()[1]

    def set_position(self, x, y, z, speed, relative=False, wait=True):
        self.robot.set_position(
            x=x, y=y, z=z, speed=speed, relative=relative, wait=wait)
        
    def calibrateUserOrientationOffset(self, points, mode=0, trust_ind=0, input_is_radian=False, return_is_radian=False):
        return self.robot.calibrate_user_orientation_offset(points, mode, trust_ind, input_is_radian, return_is_radian)

    def setState(self, state=0):
        self.robot.set_state(state)

    def getState(self):
        return self.robot.get_state()
    
    def getIsMoving(self):
        return self.robot.get_is_moving()

    def setWorldOffset(self, offset, is_radian=False):
        ret =  self.robot.set_world_offset(offset, is_radian)
        self.setState(0)

    def stop(self):
        self.setState(4)


if __name__ == "__main__":
    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOGGING_FILE_PATH),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger()

    # Robot
    robot = Robot(ROBOT_IP, logger)
    robot.home()

    # Detector
    detector = NozzleDetector()
    detector.startDetecting()

    while 1:
        robot.standby()
        time.sleep(1)

        with detector.lock:
            if len(detector.nozzles) == 0:
                logger.info("No objects detected, waiting 5 seconds...")
                time.sleep(4)
                continue
            else:
                logger.info("Objects detected, starting cycle...")
                for nozzle in detector.nozzles:

                    logger.info("Moving to object...")
                    robot.set_position(
                        x=0, y=0, z=-5.5, speed=SPEED_SLOW, relative=True, wait=True)
                    robot.set_position(
                        x=nozzle.x, y=nozzle.y, z=APPROACH_NOZZLE_Z, speed=SPEED_MIDDLE, wait=True)
                    robot.set_position(
                        x=0, y=0, z=10.5, speed=SPEED_VERY_SLOW, relative=True, wait=True)

                    logger.info("Picking up object...")
                    robot.pick()

                    logger.info("Moving to drop position...")
                    robot.move_todrop()

                    logger.info("Dropping object...")
                    robot.drop()
                    logger.info("Moving to home...")
                    robot.standby()
                    logger.info("Object picked up and dropped!")

    robot.close()
