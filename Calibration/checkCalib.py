from xarm.wrapper import XArmAPI
# import parameters from clean folder
import sys
sys.path.insert(0, 'C:/Users/mohor/Documents/1_PROJEKTI/1_odprti/RobotVision/Clean')
from parameters import ROBOT_IP
# adding clean folder to the system path

import time

robot = XArmAPI(ROBOT_IP)
robot.reset(wait=True)
robot.motion_enable(enable=True)
robot.set_mode(0)
robot.set_state(state=0)
time.sleep(1)

timeout = 2
rspeed = 70
squareSize = 19.18 # in mm
rZ = -0.5 # in mm

while 1:
    robot.set_position(x=0, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=8*squareSize, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=8*squareSize, y = 8*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=0, y = 8*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
