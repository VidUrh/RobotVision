"""
    This file is used to get the homography matrix of the camera.
    The homography matrix is used to transform the image from the perspective of the camera to the top-down view of the arena.
    We obtain the homography matrix by using the checkerboard pattern. We first detect the corners of the checkerboard pattern in the distorted image.
    Then we compute the coordinates of the checkerboard pattern in the top-down view to compute the homography matrix.

    Returns:
        None, but saves the homography matrix in the file HOMOGRAPHY_DATA_PATH (defined in parameters.py)
"""

# Import the necessary packages
import cv2
import numpy as np
import camera
from parameters import *
import pickle
import time

# Setup camera
cameraObj = camera.autoExpCamera()

time.sleep(2)


# Get the distorted image
ret, img = cameraObj.getUndistortedImage(path=IMAGE_PATH)

if not ret:
    raise Exception("[ERROR]: Failed to get image from camera!")


def dist(p1):
    """Function that returns the distance of the point to the origin.

    Args:
        p1 ((x, y)): The point whose distance to the origin is calculated.

    Returns:
        dist (float): The distance of the point to the origin.
    """

    return ((p1[0]**2+p1[1])**2)**0.5


def detectCheckerBoard(grayImage, boardDimension):
    """Function that detects the checkerboard corners in the image and returns the coordinates of the corners.
    Args:
        grayImage (numpy.ndarray): The grayscale image in which the checkerboard corners are detected.
        boardDimension ((int, int)): The dimension of the checkerboard pattern.

    Returns:
        ret (bool): True if the checkerboard corners are detected, False otherwise.
        corners (numpy.ndarray): The coordinates of the checkerboard corners. None if the checkerboard corners are not detected.
    """
    ret, corners = cv2.findChessboardCorners(grayImage, boardDimension)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners = cv2.cornerSubPix(grayImage, corners, (3, 3), (-1, -1), criteria)

    if dist(corners[0][0]) > dist(corners[-1][0]):
        corners = list(reversed(corners))

    if ret == True:
        return ret, corners
    else:
        return ret, None


grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Get the checkerboard corners in the distorted image
ret, corners = detectCheckerBoard(grayImg, CALIBRATION_SQUARES)

# Change corners format to 2D array
corners = np.array([corners[i][0] for i in range(len(corners))])


# Define the corners of the desired top-down view [(0,0),(HOMOGRAPHY_SCALING_FACTOR,0),(2*HOMOGRAPHY_SCALING_FACTOR,0),...] for the full checkerboard
dst = np.array([[x * HOMOGRAPHY_SCALING_FACTOR + HOMOGRAPHY_FIELD_OUTER_SPACE_LEFT, y * HOMOGRAPHY_SCALING_FACTOR + HOMOGRAPHY_FIELD_OUTER_SPACE_TOP]
               for y in range(CALIBRATION_SQUARE_HEIGHT) for x in range(CALIBRATION_SQUARE_WIDTH)])

# Compute the homography matrix using openCV function findHomography
cameraObj.homographyMatrix, _ = cv2.findHomography(corners, dst)

# Check the result by applying the homography transformation to the distorted image
while 1:
    ret, transformed_img = cameraObj.getdWarpedImage(IMAGE_PATH)

    cv2.imshow("transformed", transformed_img)
    cv2.imshow("original", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Save the homography matrix in the file HOMOGRAPHY_DATA_PATH
with open(HOMOGRAPHY_DATA_PATH, 'wb') as f:
    pickle.dump(cameraObj.homographyMatrix, f)
