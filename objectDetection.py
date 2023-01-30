"""
Script to detect plastic objects in a video stream using a mathematical morphology approach. 
"""
import cv2
import numpy as np


# Function to get object coordinates from a contour
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


# Function to get the orientation of an object
def getOrientation(objectContour, img):
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

    cv2.drawContours(img, [box], 0, (255, 0, 0), 1)

    # Get true orientation from calculated angle
    if width < height:
        orientation = orientation - 90

    isUpside = getTopBottomOrientation(objectContour, rotatedRect, orientation)

    # orientation = orientation + 180*isUpside

    cv2.putText(img, str(orientation),
                (int(rotatedRect[0][0]), int(rotatedRect[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return orientation


# Function to get the top-bottom orientation of an object
def getTopBottomOrientation(contour, rotatedRect, orientation):
    """
    Function to get the top-bottom orientation of an object
    Args:
        contour: contour of the object
        rotatedRect: rotated rectangle around the object
        orientation: orientation of the object
    Returns:
        isUpside: bool() value if the object is upside down
    """

    # get the center of the rotated rectangle
    center = rotatedRect[0]
    rectCx = int(center[0])
    rectCy = int(center[1])

    # get the center of the contour
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return False
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])

    r = 5

    cv2.rectangle(img, (cX-r, cY-r), (cX+r, cY+r), (0, 0, 255), 1)
    cv2.rectangle(img, (rectCx-r, rectCy-r),
                  (rectCx+r, rectCy+r), (255, 0, 255), 1)

    width = rotatedRect[-2][0]
    height = rotatedRect[-2][1]

    # if the contour is above the center of the rotated rectangle and the height is greater than the width, the object is upside down
    # elif the contour is to the right of the center of the rotated rectangle and the width is greater than the height, the object is upside down
    # else the object is right side up
    if (cY < rectCy and height > width) or (cX > rectCx and width > height):
        return True
    else:
        return False


# Function to extract plastic objects from a frame
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
    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # define the kernel
    kernel = np.ones((5, 5), np.uint8)

    # erode the frame
    eroded = cv2.erode(thresh, kernel, iterations=4)

    # dilate the frame
    dilated = cv2.dilate(eroded, kernel, iterations=3)

    # find contours in the frame
    contours, hierarchy = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Show frames
    cv2.imshow("gray", gray)
    cv2.imshow("thresh", thresh)
    cv2.imshow("eroded", eroded)
    cv2.imshow("dilated", dilated)

    # loop over the contours
    for i, contour in enumerate(contours):

        # calculate the perimeter of the contour
        t = cv2.arcLength(contour, True)

        # if the perimeter is greater than 20, the contour is a plastic object
        if t > 20:

            # add the contour to the objects array
            objects.append(contour)

            # draw the contour on the frame
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

    # return the frame and the objects array
    return frame, objects


if __name__ == "__main__":

    # For each image in the images array, extract plastic objects from the frame
    images = [
        cv2.imread("Slike\\template.jpg"),
        cv2.imread("Slike\\no-overlap.jpg"),
        cv2.imread("Slike\\overlap.jpg")
    ]
    for img in images:
        img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)
        cv2.imshow("start", img)

        # extract plastic objects from the frame
        frame, objects = extractPlasticObjects(frame=img)
        for objectContour in objects:
            x, y = getCoordinates(objectContour)
            orientation = getOrientation(objectContour, frame)
        # show the extracted frame
        cv2.imshow("end", frame)
        # wait for a key to be pressed
        cv2.waitKey(0)
        # close all windows
        cv2.destroyAllWindows()
