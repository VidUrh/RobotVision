from xarm.wrapper import XArmAPI
from parameters import *
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
rZ = -2

while 1:
    # wait for user input

    robot.set_position(x=0, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    
    robot.set_position(x=8*squareSize, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    #input("Press Enter to continue...")
    robot.set_position(x=8*squareSize, y = 8*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=0, y = 8*squareSize,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
