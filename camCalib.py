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
from tqdm import tqdm


CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

####################################################################################################################################################################
#    SETUP CAMERA                                                                                                                                                  #
####################################################################################################################################################################

def setupCamera():
    cap = cv2.VideoCapture(CAMERA_PORT, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    cap.set(cv2.CAP_PROP_EXPOSURE, CAMERA_EXPOSURE)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
    return cap

####################################################################################################################################################################
#    TAKE CALIBRATION IMAGES                                                                                                                                       #
####################################################################################################################################################################

def detectCheckerBoard(image, grayImage, criteria, boardDimension):
    ret, corners = cv2.findChessboardCorners(grayImage, boardDimension)
    if ret == True:
        corners1 = cv2.cornerSubPix(
            grayImage, corners, (3, 3), (-1, -1), criteria)
        image = cv2.drawChessboardCorners(image, boardDimension, corners1, ret)

    return image, ret


def takeCalibrationImages(camera):
    """
        Slikamo slike za kalibracijo kamere, shranjujemo jih v mapo images.
    """
    n = 0  # image_counter
    # checking if  images dir is exist not, if not then create images directory

    directoryExist = os.path.isdir(CALIBRATION_IMAGE_DIR)
    takeImages = True
    # if directory does not exist create
    if not directoryExist:
        os.makedirs(CALIBRATION_IMAGE_DIR)
        print(f'"{CALIBRATION_IMAGE_DIR}" Directory is created')
    else:
        makeNew = input(
            f'"{CALIBRATION_IMAGE_DIR}" Directory already Exists. Do you want to take new pictures? (y/n): ')
        if makeNew == 'y':
            # clearing the directory
            for file in os.listdir(CALIBRATION_IMAGE_DIR):
                os.remove(os.path.join(CALIBRATION_IMAGE_DIR, file))
            os.rmdir(CALIBRATION_IMAGE_DIR)
            os.makedirs(CALIBRATION_IMAGE_DIR)
            print(f'"{CALIBRATION_IMAGE_DIR}" Directory is cleared and created')
        else:
            print(f'"{CALIBRATION_IMAGE_DIR}" Directory is not cleared')
            takeImages = False
            n = len(os.listdir(CALIBRATION_IMAGE_DIR))

    while True:
        if takeImages == False:
            break

        ret, calibrationImage = camera.read()
        if not ret:
            print("Unable to capture video")
            continue
        gray = cv2.cvtColor(calibrationImage, cv2.COLOR_BGR2GRAY)
        image, board_detected = detectCheckerBoard(
            calibrationImage, gray, CRITERIA, CALIBRATION_SQUARES)
        # print(ret)
        cv2.putText(calibrationImage, f"saved_img : {n}", (
            30, 40), cv2.FONT_HERSHEY_PLAIN, 1.4, (0, 255, 0), 2, cv2.LINE_AA)

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

####################################################################################################################################################################
#    CALCULATE REPROJECTION ERROR                                                                                                                                  #
####################################################################################################################################################################

def calculateReprojectionError(cameraMatrix, dist, rvecs, tvecs, objPoints, imgPoints):
    mean_error = 0
    for i in range(len(objPoints)):
        imgPoints2, _ = cv2.projectPoints(
            objPoints[i], rvecs[i], tvecs[i], cameraMatrix, dist)
        error = cv2.norm(imgPoints[i], imgPoints2,
                         cv2.NORM_L2) / len(imgPoints2)
        mean_error += error
    print("total error: ", mean_error / len(objPoints))


####################################################################################################################################################################
#    PERFORM CALIBRATION                                                                                                                                           #
####################################################################################################################################################################

def calibrateCamera():
    objPoints = []  # 3D points in real world space
    imgPoints = []  # 2D points in image plane # object points will be the same for all images
    objp = np.zeros((np.prod(CALIBRATION_SQUARES), 3), np.float32)

    objp[:, :2] = np.mgrid[0:CALIBRATION_SQUARES[0],
                           0:CALIBRATION_SQUARES[1]].T.reshape(-1, 2) * CALIBRATION_SQUARE_SIZE  # 3D points in real world space

    images = [cv2.imread(filename)
              for filename in glob.glob(CALIBRATION_IMAGE_DIR+'/*png')]

    for gray in tqdm(images):
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(
            gray, CALIBRATION_SQUARES, None)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objPoints.append(objp)
            imgPoints.append(corners)

    # Calibrate camera
    ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(
        objPoints, imgPoints, CAMERA_FRAME_SIZE, None, None)

    # Calculate reprojection error
    calculateReprojectionError(
        cameraMatrix, dist, rvecs, tvecs, objPoints, imgPoints)

    return cameraMatrix, dist, rvecs, tvecs

####################################################################################################################################################################
#    SAVE CALIBRATION DATA                                                                                                                                        #
####################################################################################################################################################################

def saveCameraCalibration(cameraMatrix, dist, rvecs, tvecs):
    """
        Save camera calibration data to pickle file
    """
    calibrationData = {
        "cameraMatrix": cameraMatrix,
        "dist": dist,
        "rvecs": rvecs,
        "tvecs": tvecs
    }
    with open(CALIBRATION_DATA_PATH, "wb") as f:
        pickle.dump(calibrationData, f)
        print(f"Calibration data saved to {CALIBRATION_DATA_PATH}")


####################################################################################################################################################################
#                                                                           Main Code                                                                             #
####################################################################################################################################################################

if __name__ == "__main__":
    camera = setupCamera()
    takeCalibrationImages(camera)
    cameraMatrix, dist, rvecs, tvecs = calibrateCamera()
    saveCameraCalibration(cameraMatrix, dist, rvecs, tvecs)
    camera.release()
    cv2.destroyAllWindows()
