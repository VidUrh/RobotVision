

from xarm.wrapper import XArmAPI
# import parameters from clean folder
import sys
sys.path.insert(0, './Clean')
from parameters import ROBOT_IP, CHECKERBOARD_SQUARE_SIZE
# adding clean folder to the system path

import time

robot = XArmAPI(ROBOT_IP)
robot.reset(wait=True)
robot.motion_enable(enable=True)
robot.set_mode(0)
robot.set_state(state=0)
time.sleep(1)

timeout = 1
rspeed = 70
squareSize = CHECKERBOARD_SQUARE_SIZE # in mm
rZ = -3 # in mm

robot.set_position(x=0, y = 0,z = rZ, speed=rspeed, wait=True)
rspeed = 40
numSquares = 9

while 1:
    robot.set_position(x=0, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=numSquares*squareSize, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=numSquares*squareSize, y = numSquares*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=0, y = numSquares*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=0, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=0, y = numSquares*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=numSquares*squareSize, y = numSquares*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=numSquares*squareSize, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=0, y = numSquares*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=0, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=numSquares*squareSize, y = numSquares*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
