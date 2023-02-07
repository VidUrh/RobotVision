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
    def __init__(self, ip, port, logger):
        self.logger = logger
        self.logger.info("Connecting to robot...")
        self.robot = XArmAPI(ip, port)
        self.robot.motion_enable(enable=True)
        self.robot.set_mode(0)
        self.robot.set_state(state=0)
        self.robot.clean_error()
        self.robot.set_position(0, 0, 0, 0, wait=True)
        self.logger.info("Robot connected!")

    def move(self, x, y, z, roll, pitch, yaw, wait=True):
        self.robot.set_position(x, y, z, roll, pitch, yaw, wait=wait)

    def pick(self):
        self.robot.set_gripper_enable(True)
        self.robot.set_gripper_mode(0)
        self.robot.set_gripper_speed(1000)
        self.robot.set_gripper_position(0)

    def drop(self):
        self.robot.set_gripper_enable(True)
        self.robot.set_gripper_mode(0)
        self.robot.set_gripper_speed(1000)
        self.robot.set_gripper_position(100)

    def home(self):
        self.robot.set_position(0, 0, 0, 0, wait=True)

    def close(self):
        self.robot.disconnect()

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
    robot = Robot("192.168.64.55", 63352, logger)