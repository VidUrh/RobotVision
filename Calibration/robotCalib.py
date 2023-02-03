from xarm.wrapper import XArmAPI
# import parameters from clean folder
import sys
sys.path.insert(0, 'C:/Users/mohor/Documents/1_PROJEKTI/1_odprti/RobotVision/Clean')
from parameters import ROBOT_IP, CHECKERBOARD_SQUARE_SIZE
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
squareSize = CHECKERBOARD_SQUARE_SIZE # in mm

x = 0
y = 0
rZ = -0.5 # in mm negative value is up

robot.set_position(x=0, y = 0,z = rZ, speed=rspeed, wait=True)

while 1:
    # go to the first corner
    
    # ask user if it is ok if not, user defin move in x,y,z direction
    # if ok, move to the next corner
    if input("Is x,y ok? Y/n: ") == "n":
        x = x + float(input("Enter x: "))
        y = y + float(input("Enter y: "))
        robot.set_position(x = x, y = y,z = rZ, speed=rspeed, wait=True)
    else:
        # prin calibration check is finish
        if x==0 and y==0:  
          print("Calibration check for x,y is finish")
          break
        else:
          #x = x*(-1)
          #y = y*(-1)
          print("Calibration ofset is: x = ", -x, " y = ", -y)
          break

while 1:
    # check z axis
    if input("Is z ok? Y/n: ") == "n":
        rZ = rZ + float(input("Enter z: "))
        robot.set_position(x = x, y = y,z = rZ, speed=rspeed, wait=True)
    else:
        print("Calibration ofset is: z = ", -rZ)
        break
        
