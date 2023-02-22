'''
This script is used to test the coordinates of the points on the checkerboard.
It finds the coordinates of the checkerboard points and displays their coordinates on the image.
On fresh origin calibration the coordinates should be multiples of 25.
If the coordinates are not multiples of 25, then the camera scripts are not working properly.
'''
import cv2
import numpy as np
from parameters import *
import camera
from nozzleDetection import NozzleDetector

cam = camera.selfExpCamera()
detector = NozzleDetector()

points25 = np.array([[x * 25, y * 25]
                     for y in range(CALIBRATION_SQUARE_HEIGHT) for x in range(CALIBRATION_SQUARE_WIDTH)])

while True:
    ret, frame = cam.getdWarpedImage()
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
            corners1 = list(reversed(corners1))

        for i, corner in enumerate(corners1):
            x, y = detector.transformFromCameraToOrigin(*corner[0])

            x = round(x, 2)
            y = round(y, 2)

            cv2.putText(image, f"{x}", (int(corner[0][0]), int(
                corner[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            cv2.putText(image, f"{y}", (int(corner[0][0]), int(
                corner[0][1])+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    return image, ret


CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
image, board_detected = detectCheckerBoard(
    frame, gray, CRITERIA, (CALIBRATION_SQUARE_WIDTH, CALIBRATION_SQUARE_HEIGHT))
print(image.shape)
cam.showImage("test1", image, 0)
