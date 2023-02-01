"""
Script to detect plastic objects in a video stream using a mathematical morphology approach. 
"""
import cv2
import numpy as np
import glob

MAXIMUM_OBJECT_AREA = 500
MINIMUM_OBJECT_AREA = 100
GRAYSCALE_THRESHOLD = 60

OFFSET_X = -30
OFFSET_Y = 3


def getCoordinates(contour):
    """
    Function to get object coordinates from a contour
    Args:
        contour: contour of the object
    Returns:
        x: x coordinate of the objects center
        y: y coordinate of the objects center
    """
    # get the moments of the contour
    moments = cv2.moments(contour)

    # if the moments are 0, return 0, 0
    if moments["m00"] == 0:
        return 0, 0

    # calculate the x and y coordinates of the objects center
    x = int(moments["m10"] / moments["m00"])
    y = int(moments["m01"] / moments["m00"])
    return x, y


def getOrientation(objectContour):
    """
    Function to get object orientation from its contour
    Args:
        objectContour: contour of the object
    Returns:
        orientation: orientation of the object
    """
    # Default orientation is -1
    orientation = -1

    # get rotated rectangle from outer contour
    rotatedRect = cv2.minAreaRect(objectContour)
    box = cv2.boxPoints(rotatedRect)
    box = np.intp(box)

    # get orientation from rotated rectangle
    orientation = rotatedRect[-1]
    # Round orientation to 2 decimal places
    orientation = round(orientation, 2)

    # get width and height from rotated rectangle
    width = rotatedRect[-2][0]
    height = rotatedRect[-2][1]

    # Get true orientation from calculated angle
    if width < height:
        orientation = orientation - 90

    # Get center coordinates of rotated rectangle and of the contour
    rectCx, rectCy = map(int, rotatedRect[0])
    cX, cY = getCoordinates(objectContour)

    # Determine if the object is upside down
    isUpside = getTopBottomOrientation(rectCx, rectCy, cX, cY, orientation)
    # Fix orientation if flipped
    orientation = orientation + 180 * isUpside

    # Fix orientation if negative
    if orientation < 0:
        orientation = orientation + 360

    return orientation


def getTopBottomOrientation(rectCx, rectCy, cX, cY, orientation):
    """
    Function to get the top-bottom orientation of an object
    Args:
        rectCx: center x coordinate of the rotated rectangle
        rectCy: center y coordinate of the rotated rectangle
        cX: center x coordinate of the contour
        cY: center y coordinate of the contour
        orientation: orientation of the object
    Returns:
        isUpside: bool() value if the object is upside down
    """

    # If the objects orientation is horizontal
    #   then check if the center of the contour is to the left of the center of the rotated rectangle,
    #   if it is, the object is upside down
    if 0 <= abs(orientation) < 45:
        if cX > rectCx:
            isUpside = 1
        else:
            isUpside = 0
    # If the objects orientation is vertical and positive,
    # check if the center of the contour is above the center of the rotated rectangle,
    #   if it is not, the object is upside down
    elif -90 <= orientation <= -45:
        if cY < rectCy:
            isUpside = 1
        else:
            isUpside = 0
    # If the objects orientation is vertical and negative,
    # check if the center of the contour is below the center of the rotated rectangle,
    #   if it is not, the object is upside down
    elif 45 <= orientation <= 90:
        if cY > rectCy:
            isUpside = 1
        else:
            isUpside = 0
    else:
        isUpside = 0
    return isUpside


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

    # find contours in the frame
    contours, hierarchy = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # loop over the contours
    for i, contour in enumerate(contours):

        # calculate the perimeter of the contour
        t = cv2.arcLength(contour, True)

        # if the perimeter is greater than 20, the contour is a plastic object
        if t > MINIMUM_OBJECT_AREA and t < MAXIMUM_OBJECT_AREA:
            # add the contour to the objects array
            objects.append(contour)

    # return the frame and the objects array
    return frame, objects
