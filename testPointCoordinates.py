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

# make camera object
cam = camera.selfExpCamera()
# make nozzle detector object
detector = NozzleDetector()

# make data frame for reference
dfRef = pd.DataFrame(columns=["xRef", "yRef"])

# make same as points25 but in dfRef (dont use points25 because it is a numpy array)
for y in range(CALIBRATION_SQUARE_HEIGHT-1):
    for x in range(CALIBRATION_SQUARE_WIDTH-1):
        dfRef.loc[y*(CALIBRATION_SQUARE_WIDTH-1)+x] = [x*25, y*25]

# maka data frame for error
dfErr = pd.DataFrame(columns=["id", "xError", "yError"])
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
            x, y = detector.transformFromCameraToOrigin(*corner[0])

            #print(f"Point {i} refr coordinates: ({dfRef.loc[i][0]}, {dfRef.loc[i][1]})")
            #print(f"Point {i} coordinates: ({x}, {y})")
            xError = abs(dfRef.loc[i][0] - x)
            yError = abs(dfRef.loc[i][1] - y)
            #print(f"Point {i} error: ({xError}, {yError})")

            xError = round(xError, 2)
            yError = round(yError, 2)

            # add error to data frame
            dfErr.loc[i] = [i, xError, yError]

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

    return image, ret

def main():
    while True:
        ret, frame = cam.getdWarpedImage(IMAGE_PATH)
        if not ret:
            print("Failed to grab frame")
            break
        else:
            print("Image captured")
            break

    CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    image, board_detected = detectCheckerBoard(frame, gray, CRITERIA, (CALIBRATION_SQUARE_WIDTH-1, 
                                                                       CALIBRATION_SQUARE_HEIGHT-1))
    
    cam.showImage("test1", image, 0)


if __name__ == "__main__":
    main()