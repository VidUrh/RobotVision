"""
    Script for full camera calibration
"""
# Import required modules
import numpy as np
import cv2
import glob
import os
import pickle
from parameters import *
import tqdm


CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

####################################################################################################################################################################
#                                                                           FUNCTIONS                                                                              #
####################################################################################################################################################################
def detectCheckerBoard(image, grayImage, criteria, boardDimension):
    ret, corners = cv2.findChessboardCorners(grayImage, boardDimension)
    if ret == True:
        corners1 = cv2.cornerSubPix(grayImage, corners, (3, 3), (-1, -1), criteria)
        image = cv2.drawChessboardCorners(image, boardDimension, corners1, ret)

    return image, ret

def setupCamera():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    cap.set(cv2.CAP_PROP_EXPOSURE, CAMERA_EXPOSURE)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap

# Take calibration images
def takeCalibrationImages(camera):
    n = 0  # image_counter
    # checking if  images dir is exist not, if not then create images directory

    directoryExist = os.path.isdir(CALIBRATION_IMAGE_DIR)
    # if directory does not exist create
    if not directoryExist:
        os.makedirs(CALIBRATION_IMAGE_DIR)
        print(f'"{CALIBRATION_IMAGE_DIR}" Directory is created')
    else:
        print(f'"{CALIBRATION_IMAGE_DIR}" Directory already Exists.')
        n = len(os.listdir(CALIBRATION_IMAGE_DIR))
   
    
    while True:
        ret, calibrationImage = camera.read()
        gray = cv2.cvtColor(calibrationImage, cv2.COLOR_BGR2GRAY)
        image, board_detected = detectCheckerBoard(calibrationImage, gray, CRITERIA, CALIBRATION_SQUARES)
        # print(ret)
        cv2.putText(calibrationImage, f"saved_img : {n}",(30, 40), cv2.FONT_HERSHEY_PLAIN, 1.4, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("Calibration image", calibrationImage)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break
        if key == ord("s") and board_detected == True:
            # storing the checker board image
            cv2.imwrite(f"{CALIBRATION_IMAGE_DIR}/image{n}.png", gray)
            print(f"saved image number {n}")
            n += 1  # incrementing the image counter
    print("Total saved Images:", n)

def calibrateCamera():


    objPoints = []  # 3D points in real world space
    imgPoints = []  # 2D points in image plane # object points will be the same for all images
    objp = np.zeros((np.prod(CALIBRATION_SQUARES), 3), np.float32)

    objp[:, :2] = np.mgrid[0:CALIBRATION_SQUARES[0],
                        0:CALIBRATION_SQUARES[1]].T.reshape(-1, 2) * CALIBRATION_SQUARE_SIZE # 3D points in real world space


    images = [cv2.imread(filename) for filename in glob.glob(CALIBRATION_IMAGE_DIR+'/*png')]

    for gray in tqdm(images):
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, CALIBRATION_SQUARES, None)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objPoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), CRITERIA)
            imgPoints.append(corners)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, CALIBRATION_SQUARES, corners2, ret)

camera = setupCamera()
takeCalibrationImages(camera)
calibrateCamera(camera)
camera.release()
cv2.destroyAllWindows()