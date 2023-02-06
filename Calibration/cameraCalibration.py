from tqdm import tqdm
import pickle
import numpy as np
import cv2
import glob
import sys
sys.path.insert(0, '../RobotVision/Clean')
from parameters import *

# Step 1: Prepare a checkerboard pattern
chessboardSize = CHECKERBOARD
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Step 2: Take photos of the checkerboard
# List to hold the checkerboard images # Load the images here...
images = [cv2.imread(filename)
          for filename in glob.glob('./Calibration/images/*png')]


# Step 3: Detect checkerboard corners
objPoints = []  # 3D points in real world space
imgPoints = []  # 2D points in image plane # object points will be the same for all images
objp = np.zeros((np.prod(chessboardSize), 3), np.float32)

objp[:, :2] = np.mgrid[0:chessboardSize[0],
                       0:chessboardSize[1]].T.reshape(-1, 2) * CHECKERBOARD_SQUARE_SIZE # 3D points in real world space

for img in tqdm(images):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, chessboardSize, None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objPoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgPoints.append(corners)
        # Draw and display the corners
        cv2.drawChessboardCorners(img, chessboardSize, corners2, ret)


cv2.destroyAllWindows()

# Step 5: Calculate camera calibration and distortion coefficients
ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(
    objPoints, imgPoints, gray.shape[::-1], None, None)


with open('Clean\\calibrationData.pkl', 'wb') as f:
    data = {'cameraMatrix': cameraMatrix, 'dist': dist, 'rvecs': rvecs, 'tvecs': tvecs}
    pickle.dump(data, f)
