'''
This script is used to calibrate the origin of the camera.

It is used to find the coordinates of the origin of the camera in the robot frame.
'''
import cv2
import time
from parameters import *
import json
import camera

cam = camera.selfExpCamera()

while True:
    ret, frame = cam.getUndistortedImage()
    if not ret:
        print("Failed to grab frame")
        break
    if cam.showImage("test", frame, 1) == ord("q"):
        cam.saveImage("calibration_", frame)
        break

if frame is None:
    print("No image captured")
    exit()


def dist(p1):
    return ((p1[0]**2+p1[1])**2)**0.5


def detectCheckerBoard(image, grayImage, criteria, boardDimension):
    ret, corners = cv2.findChessboardCorners(grayImage, boardDimension)
    if ret == True:
        corners1 = cv2.cornerSubPix(
            grayImage, corners, (3, 3), (-1, -1), criteria)
        image = cv2.drawChessboardCorners(image, boardDimension, corners1, ret)

        if dist(corners1[0][0]) > dist(corners1[-1][0]):
            corners = list(reversed(corners1))

        # Get coordinates of corners
        # Top left corner
        xTopL = corners[0][0][0]
        yTopL = corners[0][0][1]
        cv2.putText(image, "TopLeft", (int(xTopL), int(yTopL)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # Print "TopLeft" near the circle
        cv2.circle(image, (int(xTopL), int(yTopL)), 7,
                   (0, 0, 255), 2)  # Draw a circle on the corner

        # Top right corner
        xTopR = corners[NUM_SQUARES][0][0]
        yTopR = corners[NUM_SQUARES][0][1]
        cv2.putText(image, "TopRight", (int(xTopR), int(yTopR)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)  # Print "TopRight" near the circle
        cv2.circle(image, (int(xTopR), int(yTopR)), 7,
                   (0, 255, 255), 2)  # Draw a circle on the corner

        with open(CORNERS_DATA_PATH, "w") as f:
            json.dump({
                "origin": [int(xTopL), int(yTopL)],
                "x": [int(xTopR), int(yTopR)]
            }, f)

    return image, ret


CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
image, board_detected = detectCheckerBoard(
    frame, gray, CRITERIA, (CALIBRATION_SQUARE_WIDTH-1, CALIBRATION_SQUARE_HEIGHT-1))

cam.showImage("test1", image, 0)
