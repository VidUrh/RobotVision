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
        self.robot.reset()
        self.robot.clean_error()
        self.robot.motion_enable(enable=True)
        self.robot.set_mode(0)
        self.robot.set_state(state=0)
        self.logger.info("Robot connected!")

    def move(self, x, y, z, roll, pitch, yaw, wait=True):
        self.robot.set_position(x, y, z, roll, pitch, yaw, wait=wait)

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

    def set_position(self, x, y, z, speed, relative=False, wait=True):
        self.robot.set_position(
            x=x, y=y, z=z, speed=speed, relative=relative, wait=wait)


if __name__ == "__main__":
    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("robot.log"),
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
