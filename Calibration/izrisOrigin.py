import cv2
import numpy as np
import glob
import sys
sys.path.insert(0, '../RobotVision/Clean')
from parameters import *
import pickle
        


def extractPlasticObjects(frame):
    """
    Function to extract plastic objects from a frame
    Args:
        frame: frame to be processed
    Returns:
        frame: processed frame
        objects: array of the coordinates of plastic objects
    """
    objects = []
    # convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # apply Gaussian blur to the frame
    gray = cv2.GaussianBlur(gray, (5, 5), 2)

    # apply thresholding to the frame
    ret, thresh = cv2.threshold(
        gray, GRAYSCALE_THRESHOLD, 255, cv2.THRESH_BINARY)

    # define the kernel
    kernel = np.ones((3, 3), np.uint8)

    # erode the frame
    eroded = cv2.erode(thresh, kernel, iterations=4)

    # dilate the frame
    dilated = cv2.dilate(eroded, kernel, iterations=3)

    lengt = 500
    cv2.line(frame, (ORIGIN_COORD_FROM_CAM_X, ORIGIN_COORD_FROM_CAM_Y), (ORIGIN_COORD_FROM_CAM_X, ORIGIN_COORD_FROM_CAM_Y+lengt), (0, 255, 0), 1)
    cv2.line(frame, (ORIGIN_COORD_FROM_CAM_X, ORIGIN_COORD_FROM_CAM_Y), (ORIGIN_COORD_FROM_CAM_X+lengt, ORIGIN_COORD_FROM_CAM_Y), (0, 0, 255), 1)
    # return the frame and the objects array
    cv2.imwrite("frame.jpg", frame)
    return frame, objects


if __name__ == "__main__":

    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    cam.set(cv2.CAP_PROP_EXPOSURE, CAMERA_EXPOSURE)
    with open('Clean\\calibrationData.pkl', 'rb') as f:
        data = pickle.load(f)
        cameraMatrix = data['cameraMatrix']
        dist = data['dist']
        rvect = data['rvecs']
        tvect = data['tvecs']
    
    while 1:
        ret,img = cam.read()
        dst,_ = extractPlasticObjects(img.copy())
        cv2.imshow('distort', dst)
        

        h, w = img.shape[:2]
        newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))
        # Undistort
        dst = cv2.undistort(img, cameraMatrix, dist, None, newCameraMatrix)
        # crop the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        dst,_ = extractPlasticObjects(dst)
        cv2.imshow('undistort', dst)
        
        # Undistort with Remapping
        mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
        dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
        # crop the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]

        dst,_ = extractPlasticObjects(dst)

        cv2.imshow('undistort with remapping', dst)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    