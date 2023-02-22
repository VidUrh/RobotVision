import sys
sys.path.append('.')

import cv2
import logging
from parameters import *
import numpy as np
import pandas as pd
import pickle
import time

'''
Ta skripta je namenjena za testiranje kamere in njene kalibracije.
Najprej zajamemo sliko kamere.
Nato uporabimo kalibracijske parametere in z njimi popravimo sliko.
Ko smo sliko popravili, na njej najdemo vse kvadrate in jih označimo.
Izračunamo dimenzije vseh kvadratov in jih izpišemo na sliki.
Sledi preverjanje ali so kvadrati pravilno označeni in ali so dimenzije pravilne (kvadrati imajo znane dimenzije).
Na koncu vse dimenzije primerjamo in izračunamo napako med njimi.
'''

NUMBER_OF_IMAGES = 1 # Number of images to take for calibration

# Make camera class
class Camera:
    def __init__(self):
        self.cam = cv2.VideoCapture(CAMERA_PORT, cv2.CAP_DSHOW)
        
        self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self.cam.set(cv2.CAP_PROP_EXPOSURE, CAMERA_EXPOSURE)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)

        # print camera settings
        # print("Camera settings:")
        # print("Frame width: ", cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        # print("Frame height: ", cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # print("Auto exposure: ", cam.get(cv2.CAP_PROP_AUTO_EXPOSURE))
        # print("Auto white balance: ", cam.get(cv2.CAP_PROP_AUTO_WB))
        # print("Auto focus: ", cam.get(cv2.CAP_PROP_AUTOFOCUS))
        # print("Auto bandwidth calculation: ", cam.get(cv2.CAP_PROP_XI_AUTO_BANDWIDTH_CALCULATION))
        # print("Auto white balance: ", cam.get(cv2.CAP_PROP_XI_AUTO_WB))
        # print("Auto step: ", cam.get(cv2.MAT_AUTO_STEP))
        # print("White balance temperature: ", cam.get(cv2.CAP_PROP_WB_TEMPERATURE))
        print("Exposure: ", self.cam.get(cv2.CAP_PROP_EXPOSURE))

    def getImage(self):
        self.ret, self.image = self.cam.read()
        if not self.ret:
            logging.error("Could not read image from camera")
            return None
        return self.image
    
    def saveImage(self, image, path, number, extension):
        if image is None:
            return None
        
        path = path + "image" + str(number) + extension
        cv2.imwrite(path, image)
        return image
    
    def loadImage(self, path, number, extension):
        path = path + "image" + str(number) + extension
        image = cv2.imread(path)
        return image

    def __del__(self):
        self.cam.release()
        cv2.destroyAllWindows()
        

# Undistort image
def undistortImage(image):
    # Read camera calibration data
    with open(CALIBRATION_DATA_PATH, 'rb') as calibrationFile:
        data = pickle.load(calibrationFile)
        cameraMatrix = data['cameraMatrix']
        dist = data['dist']
        rvecs = data['rvecs']
        tvecs = data['tvecs']
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        cameraMatrix, dist, (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT), 1, (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT))
    
    # Undistort image
    imageUndistorted = cv2.undistort(image, newcameramtx, dist)
    return imageUndistorted

# Correct image
def correctImage(image):
    # convert image to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # apply gaussian blur to the image
    imageBlur = cv2.medianBlur(imageGray, 3)

    # sharpen image
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(imageBlur, 0, sharpen_kernel)
    return sharpen

# Check pattern
def checkPattern(image):
    ret, corners = cv2.findChessboardCorners(image, CALIBRATION_SQUARES, None)
    if ret == True:
        # Show cornes on image
        cv2.drawChessboardCorners(image, CALIBRATION_SQUARES, corners, ret)
        # Show image
        cv2.imshow("image", image)
        key = cv2.waitKey(0)
        print("key: ", key)
        if key == ord('q'):
            # close window
            cv2.destroyAllWindows()
            return None
        elif key == ord('s'):
            # close window
            cv2.destroyAllWindows()
            return True
        elif key == ord('e'):
            # close window
            cv2.destroyAllWindows()
            return False
    
# Find checkerboard corners
def findCheckerboardCorners(name, image):
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(image, CALIBRATION_SQUARES, None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        # Get coordinates of corners
        # Top left corner
        xTopL = corners[0][0][0]
        yTopL = corners[0][0][1]
        cv2.putText(image, str(1), (int(xTopL), int(yTopL)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
        cv2.circle(image, (int(xTopL), int(yTopL)), 5, (0, 0, 255), 2)

        # Top right corner
        xTopR = corners[CALIBRATION_SQUARE_WIDTH-1][0][0]
        yTopR = corners[CALIBRATION_SQUARE_WIDTH-1][0][1]
        cv2.putText(image, str(2), (int(xTopR), int(yTopR)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
        cv2.circle(image, (int(xTopR), int(yTopR)), 5, (0, 0, 255), 2)

        # Bottom right corner
        xBotR = corners[CALIBRATION_SQUARE_WIDTH*CALIBRATION_SQUARE_HEIGHT-1][0][0]
        yBotR = corners[CALIBRATION_SQUARE_WIDTH*CALIBRATION_SQUARE_HEIGHT-1][0][1]
        cv2.putText(image, str(3), (int(xBotR), int(yBotR)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
        cv2.circle(image, (int(xBotR), int(yBotR)), 5, (0, 0, 255), 2)

        # Bottom left corner
        xBotL = corners[CALIBRATION_SQUARE_WIDTH*(CALIBRATION_SQUARE_HEIGHT-1)][0][0]
        yBotL = corners[CALIBRATION_SQUARE_WIDTH*(CALIBRATION_SQUARE_HEIGHT-1)][0][1]
        cv2.putText(image, str(4), (int(xBotL), int(yBotL)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
        cv2.circle(image, (int(xBotL), int(yBotL)), 5, (0, 0, 255), 2)

        # Calculate all possible distances
        # Calculate distance between top left and top right corner
        dTop = math.sqrt((xTopL-xTopR)**2 + (yTopL-yTopR)**2)
        dBot = math.sqrt((xBotL-xBotR)**2 + (yBotL-yBotR)**2)
        dLeft = math.sqrt((xTopL-xBotL)**2 + (yTopL-yBotL)**2)
        dRight = math.sqrt((xTopR-xBotR)**2 + (yTopR-yBotR)**2)
        dTopLBotR = math.sqrt((xTopL-xBotR)**2 + (yTopL-yBotR)**2)
        dTopRBotL = math.sqrt((xTopR-xBotL)**2 + (yTopR-yBotL)**2)

        # Draw lines between corners
        cv2.line(image, (int(xTopL), int(yTopL)), (int(xTopR), int(yTopR)), (0, 255, 0), 1)
        cv2.line(image, (int(xTopL), int(yTopL)), (int(xBotL), int(yBotL)), (0, 255, 0), 1)
        cv2.line(image, (int(xTopR), int(yTopR)), (int(xBotR), int(yBotR)), (0, 255, 0), 1)
        cv2.line(image, (int(xBotL), int(yBotL)), (int(xBotR), int(yBotR)), (0, 255, 0), 1)
        cv2.line(image, (int(xTopL), int(yTopL)), (int(xBotR), int(yBotR)), (0, 255, 0), 1)
        cv2.line(image, (int(xTopR), int(yTopR)), (int(xBotL), int(yBotL)), (0, 255, 0), 1)

        # Write distances in center of line on image
        cv2.putText(image, str(round(dTop, 2)),      (int((xTopL+xTopR)/2), int((yTopL+yTopR)/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(image, str(round(dBot, 2)),      (int((xBotL+xBotR)/2), int((yBotL+yBotR)/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(image, str(round(dLeft, 2)),     (int((xTopL+xBotL)/2), int((yTopL+yBotL)/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(image, str(round(dRight, 2)),    (int((xTopR+xBotR)/2), int((yTopR+yBotR)/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # Write ditsances in upper quarter of diagonal lines
        cv2.putText(image, str(round(dTopLBotR, 2)), (int((xTopL+xBotR)/2)-int((xTopL-xBotR)/4), int((yTopL+yBotR)/2)-int((yTopL-yBotR)/4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(image, str(round(dTopRBotL, 2)), (int((xTopR+xBotL)/2)-int((xTopR-xBotL)/4), int((yTopR+yBotL)/2)-int((yTopR-yBotL)/4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Calculate error between opoosite distances
        errTopBot = abs(dTop-dBot)
        errLeftRight = abs(dLeft-dRight)
        errTopLBotRTopRBotL = abs(dTopLBotR-dTopRBotL)
        # print(name)
        # print("Error top-bot: ", errTopBot)
        # print("Error left-right: ", errLeftRight)
        # print("Error topL-botR-topR-botL: ", errTopLBotRTopRBotL)
        return errTopBot, errLeftRight, errTopLBotRTopRBotL

    else:
        print("No corners found")
        return None

# Make data class storing results in dataframe
class Data:
    # Constructor
    def __init__(self, dfName):
        # Make empty dataframe without columns
        self.df = pd.DataFrame()

    
    # Add new row to dataframe
    def addRow(self, image, data):
        # Add image name to tuple
        data = (image,) + data
        print(data)

        # add data to dataframe
        self.df = self.df.append([data], ignore_index=True)

    # Print dataframe
    def print(self):
        print(self.df)

    # Calculate mean for each column without first column
    def mean(self):
        # Make empty list
        meanList = []

        # Calculate mean for each column
        for i in range(1, len(self.df.columns)):
            meanList.append(self.df[i].mean())

        return meanList
    

####################################################################################################
#       MAIN
####################################################################################################
def mainCheckerboard():
    # Make camera object
    cam = Camera()

    # Make data objects
    distortedResults = Data("Distorted results")
    undistortedResults = Data("Undistorted results")
    i = 0

    while True:
        #image = loadImage("./images/", i, ".png")
        image = cam.getImage()
        #cv2.imshow("Original", image)
        imageDistorted = image.copy()
        imageUndistorted = image.copy()
        
        check = checkPattern(image)
        # Distorted image
        if check == True:
            # Distorted image
            distortedResults.addRow(i, findCheckerboardCorners("Distorted", imageDistorted))

            # Undistorted image
            imageUndistorted = undistortImage(imageUndistorted)
            undistortedResults.addRow(i, findCheckerboardCorners("Undistorted", imageUndistorted))
            i += 1
        elif check == False:
            print("No corners found, exiting")
            break
        else:
            print("No corners found, try again")


    print("Distorted results")
    distortedResults.print()

    print("\nUndistorted results")
    undistortedResults.print()

    # Calculate mean of results
    print("\nDistorted mean")
    print(distortedResults.mean())

    print("\nUndistorted mean")
    print(undistortedResults.mean())

if __name__ == "__main__":
    # mainSquares()
    # mainLines()
    mainCheckerboard()
    pass