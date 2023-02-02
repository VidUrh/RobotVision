import pickle
import numpy as np
import cv2
import glob

# Step 1: Prepare a checkerboard pattern
pattern_size = (9, 13)

# Step 2: Take photos of the checkerboard
images = []  # List to hold the checkerboard images # Load the images here... 
cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
cam.set(cv2.CAP_PROP_EXPOSURE, -9)

ret, frame = cam.read()
while not ret:
    ret, frame = cam.read()
images.append(frame)
cv2.imshow("frame", frame)
cv2.imwrite("calibrationImage.png", frame)
cv2.waitKey(0)
# Step 3: Convert images to grayscale
gray_images = []
for img in images:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_images.append(gray)
#    cv2.imshow('image', gray)
#    cv2.waitKey(0)

# Step 4: Detect checkerboard corners
objpoints = []  # 3D points in real world space
imgpoints = []  # 2D points in image plane # object points will be the same for all images
objp = np.zeros((np.prod(pattern_size), 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * 0.01918 # 0.01918 is the size of the checkerboard square in meters
for gray in gray_images:
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
    if ret:
        imgpoints.append(corners)
        objpoints.append(objp)
        cv2.drawChessboardCorners(gray, pattern_size, corners, ret)
        cv2.imshow("gray", gray)
        cv2.waitKey(0)

# Step 5: Calculate camera calibration and distortion coefficients
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None)


with open('calibrationData.pkl', 'wb') as f:
    data = {'mtx': mtx, 'dist': dist}
    pickle.dump(data, f)
