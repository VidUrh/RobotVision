'''
This script is used to test the coordinates of the points on the checkerboard.
It finds the coordinates of the checkerboard points and displays their coordinates on the image.
On fresh origin calibration the coordinates should be multiples of 25.
If the coordinates are not multiples of 25, then the camera scripts are not working properly.

We calculate the average error and print 10 points with the highest error.
We also show this 10 points on the image.
'''
import cv2
from parameters import *
import camera
from nozzleDetection import NozzleDetector
import pandas as pd
import time
import vodenjeRobota as vr
import logging

# make camera object
cam = camera.autoExpCamera()
robot = vr.worldCoordRobot(ROBOT_IP, logging.getLogger())

# make data frame for reference
dfRef = pd.DataFrame(columns=["xRef", "yRef"])

# make same as points25 but in dfRef (dont use points25 because it is a numpy array)
for y in range(CALIBRATION_SQUARE_HEIGHT):
    for x in range(CALIBRATION_SQUARE_WIDTH):
        dfRef.loc[y*(CALIBRATION_SQUARE_WIDTH)+x] = [x*25, y*25]

# maka data frame for error
dfErr = pd.DataFrame(columns=["id", "x", "y", "xError", "yError"])
dfErr["id"] = dfErr["id"].astype(int)

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
            x, y = cam.transformFromCameraToOrigin(*corner[0])

            #print(f"Point {i} refr coordinates: ({dfRef.loc[i][0]}, {dfRef.loc[i][1]})")
            #print(f"Point {i} coordinates: ({x}, {y})")
            xError = abs(dfRef["xRef"].loc[i] - x)
            yError = abs(dfRef["yRef"].loc[i] - y)
            #print(f"Point {i} error: ({xError}, {yError})")

            xError = round(xError, 2)
            yError = round(yError, 2)

            # add error to data frame
            dfErr.loc[i] = [i, x, y, xError, yError]

        # find average error
        xError = dfErr["xError"].mean()
        yError = dfErr["yError"].mean()
        print(f"Average error: ({xError}, {yError})")

        # find max error
        xError = dfErr["xError"].max()
        yError = dfErr["yError"].max()
        print(f"Max error: ({xError}, {yError})")

        # calculate mean error between x and y error and add to data frame
        dfErr["meanError"] = (dfErr["xError"] + dfErr["yError"])/2
        # ahow all data frame in terminal


        # find 10 point with max error
        meanError = dfErr.sort_values(by=["meanError"], ascending=False)
        meanError = meanError.reset_index(drop=True)
        meanError["id"] = meanError["id"].apply(int)
        print(meanError.head(10))

        for i in range(10):
            cv2.putText(image, f"{meanError.loc[i][1]}", (int(corners1[meanError["id"].loc[i]][0][0]), int(
                corners1[meanError["id"].loc[i]][0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            cv2.putText(image, f"{meanError.loc[i][2]}", (int(corners1[meanError["id"].loc[i]][0][0]), int(
                corners1[meanError["id"].loc[i]][0][1])+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            cv2.putText(image, f"{meanError.loc[i][3]}", (int(corners1[meanError["id"].loc[i]][0][0]), int(
                corners1[meanError["id"].loc[i]][0][1])+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1, cv2.LINE_AA)

            # print(f"Point {meanError['id'].loc[i]} error: ({meanError.loc[i][1]}, {meanError.loc[i][2]})")

    return image, ret, dfErr

def main():
    #cam.imageSettings()
    while True:
        ret, frame = cam.getImage()
        if cam.showImage("test", frame, 1) & 0xFF == ord('q'):
            break

    frame = cam.warpImage(frame)
    cam.saveImage("warp", frame)
    cam.showImage("warp", frame, 0)

    CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    #frame = cam.setBrightness(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cam.saveImage("gray", gray)
    image, board_detected = detectCheckerBoard(frame, gray, CRITERIA, (CALIBRATION_SQUARE_WIDTH-1, 
                                                                       CALIBRATION_SQUARE_HEIGHT-1))
    
    cam.saveImage("errPoint", image)
    cam.showImage("point", image, 0)

def moveRobot():
    #cam.imageSettings()
    while True:
        ret, frame = cam.getImage()
        if cam.showImage("test", frame, 1) & 0xFF == ord('q'):
            break

    frame = cam.warpImage(frame)
    cam.saveImage("warp", frame)
    cam.showImage("warp", frame, 0)

    CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    #frame = cam.setBrightness(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cam.saveImage("gray", gray)
    image, board_detected, corners = detectCheckerBoard(frame, gray, CRITERIA, (CALIBRATION_SQUARE_WIDTH, 
                                                                       CALIBRATION_SQUARE_HEIGHT))
    
    cam.showImage("point", image, 0)
    cam.saveImage("errPoint", image)
    
    print(corners)
    robot.setWorldOffset()
    time.sleep(0.2)
    # for all x any y in corners dataframe to move robot to point
    for i in range(len(corners)):
        vrstica   = i//CALIBRATION_SQUARE_WIDTH
        stolpec = i%CALIBRATION_SQUARE_WIDTH
        print(vrstica, stolpec)
        if vrstica not in range(2,8) or stolpec not in range(5,7):
            continue
            
        print(f"Point {i}: ({corners['x'].loc[i]}, {corners['y'].loc[i]})")
        robot.move(corners['x'].loc[i], corners['y'].loc[i], z=-2, speed=50)
        time.sleep(0.2)
        while robot.getIsMoving():
            time.sleep(0.1)

if __name__ == "__main__":
    #main()
    moveRobot()