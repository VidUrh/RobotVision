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
rZ = -1
while 1:
    robot.set_position(x=0, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=150, y = 0,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=150, y = 110,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
    robot.set_position(x=0, y = 110,z = rZ, speed=rspeed, wait=True)
    time.sleep(timeout)
