"""
This is the main file for the robot. It is responsible for running the robot. And is the only file that should be run.
"""

import cv2
import numpy as np
from objectDetection import extractPlasticObjects, getCoordinates, getOrientation
from poseTransformCalculation import getCoordinatesInVmesniCoor, getCoordinatesFromVmesniCoor
import time
import math
from xarm.wrapper import XArmAPI

# 19.18
OFFSET_X = -50
OFFSET_Y = 5

if __name__ == "__main__":

    # define the robot
    robot = XArmAPI('192.168.64.55')
    robot.reset(wait=True)
    robot.motion_enable(enable=True)
    robot.set_mode(0)
    robot.set_state(state=0)
    time.sleep(1)
    
    robot.set_servo_angle(angle=[90, 0, 90, 0.0, 90, 0], speed=100, acceleration=5, is_radian=False, wait=True)


    # Define the camera
    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    cam.set(cv2.CAP_PROP_EXPOSURE, -3)
    while True:
        ret, frame = cam.read()

        frame, objects = extractPlasticObjects(frame)

        for objectContour in objects:
            # get coordinates of the object in pixels
            x, y = getCoordinates(objectContour)

            # draw center of the object 
            cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), 1)

            # get orientation of the object in degrees
            orientation = getOrientation(objectContour)


            # transform the coordinates to vmesni coordinate system pixels -> mm
            realX, realY, realZ = getCoordinatesInVmesniCoor(x, y)


            #realX = realX + OFFSET_X * math.cos(orientation) + OFFSET_Y * math.sin(orientation)
            #realY = realY + OFFSET_Y * math.cos(orientation) + OFFSET_X * math.sin(orientation)

            #newX, newY = getCoordinatesFromVmesniCoor(realX, realY)
            #cv2.circle(frame, (int(newX), int(newY)), 5, (255, 0, 0), 1)

            cv2.putText(frame, str(f"{realX}"), (int(x), int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

            cv2.putText(frame, str(f"{realY}"), (int(x), int(y+30)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)


        cv2.imshow("frame", frame)
        
        cv2.waitKey(0)

        robot.set_position(x=0, y = 0,z = -5.5, speed=20, relative = True, wait=True)
        robot.set_position(x=realX, y=realY,z = -20, speed=80, wait=True)
        robot.set_position(x=0, y = 0,z = 10.5, speed=20, relative = True, wait=True)
        """
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        """
        
    robot.disconnect()
