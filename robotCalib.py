from xarm.wrapper import XArmAPI
# import parameters from clean folder
import sys
sys.path.insert(0, '../RobotVision/Clean')
from parameters import *
# adding clean folder to the system path

CALIBRATION_SQUARE_SIZE
import time

robot = XArmAPI(ROBOT_IP)
#robot.reset(wait=True)
robot.motion_enable(enable=True)
robot.set_mode(0)
robot.set_state(state=0)
time.sleep(1)

timeout = 2
rspeed = 70
squareSize = CALIBRATION_SQUARE_SIZE # in mm

x = 400
y = 0
rZ = 2 # in mm negative value is up

robot.set_position(x=x, y =y,z = rZ, speed=rspeed, wait=True)


def setXYOffset(x, y, rZ, rspeed):
    robot.set_position(x = x, y = y,z = rZ, speed=rspeed, wait=True)
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

def setZOffset(x, y, rZ, rspeed):
    while 1:
        # check z axis
        if input("Is z ok? Y/n: ") == "n":
            rZ = rZ + float(input("Enter z: "))
            robot.set_position(x = x, y = y,z = rZ, speed=rspeed, wait=True)
        else:
            print("Calibration ofset is: z = ", -rZ)
            break

def setRotation(x, y, rZ, rspeed):
    # check rotation
    xRot = x
    yRot = y

    # Teach robot 3 points
    # make list of teach points
    points = []
    points.append(robot.get_position()[1])
    # move robot in x direction
    setXYOffset(xRot, yRot, rZ, rspeed)
    points.append(robot.get_position()[1])

    # move robot in y direction
    setXYOffset(200, yRot, rZ, rspeed)
    points.append(robot.get_position()[1])

    # Check teach points
    robot.set_position(x = points[0][0], y = points[0][1], z = points[0][2], speed=rspeed, wait=True)
    time.sleep(1)
    robot.set_position(x = points[1][0], y = points[1][1], z = points[1][2], speed=rspeed, wait=True)
    time.sleep(1)
    robot.set_position(x = points[2][0], y = points[2][1], z = points[2][2], speed=rspeed, wait=True)
    time.sleep(1)

    print("Teach points are: ", points)
    rotationOffset = robot.calibrate_user_orientation_offset(points, mode=0, trust_ind=0, input_is_radian=False, return_is_radian=False)[1]
    rotationOffset = list(map(lambda x: -x, rotationOffset))
    print("Rotation offset is: ", rotationOffset)
    robot.set_position(x = x, y = y, z = rZ, yaw = yaw, speed=rspeed, is_radian = False, wait=True)
    
    # move robot in x direction
    robot.set_position(x = x, y = y, z = rZ, speed=rspeed, wait=True)
    for i in range (1, 6):
        robot.set_position(x = x+(i*squareSize), y = y, z = rZ, speed=rspeed, wait=True)
    print(robot.get_position())
    robot.set_position(x = x, y = y, z = rZ, speed=rspeed, wait=True)

def checkRotation():
    # move robot in x direction
    while 1:
        robot.set_position(x = 0, y = 0, z = -2, speed=rspeed, wait=True)
        for i in range (1, 6):
            robot.set_position(x = (i*squareSize), y = 0, z = rZ, speed=rspeed, wait=True)
        print(robot.get_position())
        robot.set_position(x = 0, y = 0, z = -2, speed=rspeed, wait=True)
        if input("Will finish? Y/n: ") == "y":
            break


if __name__ == "__main__":
    setXYOffset(x, y, rZ, rspeed)
    #setRotation(x, y, rZ, rspeed)
    #setZOffset(x, y, rZ, rspeed)
    #checkRotation()


# while 1:
#     for j in range (0, 2):
#         robot.set_position(x = x, y = y, z = rZ, yaw = yaw, speed=rspeed, is_radian = True, wait=True)
#         # move robot in x direction
#         for i in range (1, 6):
#             robot.set_position(x = x+(i*squareSize), y = y, z = rZ, yaw = yaw, speed=rspeed, is_radian=True, wait=True)
#         print(robot.get_position())
#         robot.set_position(x = x, y = y, z = rZ, yaw = yaw, speed=rspeed, is_radian=True, wait=True)
        
#         inChar = input("Is rotation ok? Y/n or c for continue: ")
#         if inChar == "n":
#             print("Previous yaw is: ", yaw)
#             yaw = yaw + float(input("Enter yaw offset: "))
#             print("New yaw is: ", yaw)    
#         elif inChar == "c":
#             continue
#         else:
#             print("Calibration ofset is: yaw = ", -yaw)
#             exit()
        