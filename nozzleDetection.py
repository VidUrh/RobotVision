"""
    Skripta za detekcijo nozzlov.
    Definira class, ki ob konstrukciji začne konstantno detekcijo nozzlov in njihove podatke shranjuje v spremenljivko self.nozzles, ki je seznam objektov class-a Nozzle.
"""
import cv2
from parameters import *
import numpy as np
import math
import logging
import time
import threading
import pickle
import camera


class CameraReadError(Exception):
    pass


class Nozzle:
    def __init__(self, position_x, position_y, rotation):
        self.x = position_x  # x koordinata nozzla v realnem svetu, v milimetrih od izhodišča
        self.y = position_y  # y koordinata nozzla v realnem svetu, v milimetrih od izhodišča
        self.r = rotation  # kot nozzla v realnem svetu, v stopinjah merjen odmik od x osi izhodišča

    def __repr__(self):
        return f'Nozzle at ({self.x}, {self.y}) with rotation {self.r}'


class NozzleDetector:
    def __init__(self):
        self.nozzles = []
        self.cam = None
        self.thread = None
        self.running = False
        self.lock = threading.Lock()
        self.image = None
        self.setupCamera()

    def __del__(self):
        del self.cam
        cv2.destroyAllWindows()

    def detectNozzles(self):
        """
            Funkcija za detekcijo nozzlov na sliki.
            Vrne seznam objektov class-a Nozzle.
        """
        ret, self.image = self.cam.getdWarpedImage()

        # transform to binary image
        transformed = self.transformImage(self.image)

        # find contours in the frame
        contours = self.findContours(transformed)

        # filter contours by size
        filteredContours = self.filterContours(contours)

        # find nozzle positions
        nozzles = []

        # Draw helper lines in debug mode
        if DEBUG_MODE is True:
            cv2.circle(self.image, (ORIGIN_COORD_FROM_CAM_X,
                                    ORIGIN_COORD_FROM_CAM_Y), 5, (255, 0, 255), -1)

            # Draw the x and y axis
            lineLength = 2000
            cv2.line(self.image, (ORIGIN_COORD_FROM_CAM_X - lineLength, ORIGIN_COORD_FROM_CAM_Y),
                     (ORIGIN_COORD_FROM_CAM_X + lineLength, ORIGIN_COORD_FROM_CAM_Y), (0, 0, 255), 2)

            cv2.line(self.image, (ORIGIN_COORD_FROM_CAM_X, ORIGIN_COORD_FROM_CAM_Y - lineLength), (
                ORIGIN_COORD_FROM_CAM_X, ORIGIN_COORD_FROM_CAM_Y + lineLength), (0, 255, 0), 2)

        for nozzle in filteredContours:
            nozzleXpos, nozzleYpos = self.getCoordinates(nozzle)
            nozzleRotation = self.getOrientation(nozzle)
            nozzleInWorldX, nozzleInWorldY = self.transformFromCameraToOrigin(
                nozzleXpos, nozzleYpos)
            
            # offset for robot
            nozzleInWorldX += 3
            nozzleInWorldY += 7

            xOffset, yOffset = 15, 0
            #nozzleRotation = nozzleRotation * -1
            print(nozzleRotation)
            nozzleOffsetX = -xOffset * math.cos(math.radians(nozzleRotation))
            nozzleOffsetY = xOffset * math.sin(math.radians(nozzleRotation))
            nozzleInWorldX += nozzleOffsetX
            nozzleInWorldY += nozzleOffsetY

            
            nozzles.append(
                Nozzle(nozzleInWorldX, nozzleInWorldY, nozzleRotation))

            # Draw helper lines in debug mode
            if DEBUG_MODE is True:
                cv2.putText(self.image, f'({nozzleInWorldX})', (
                    nozzleXpos+50, nozzleYpos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(self.image, f'({nozzleInWorldY})', (
                    nozzleXpos+50, nozzleYpos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.circle(self.image, (nozzleXpos, nozzleYpos),
                           5, (255, 0, 255), -1)

                cv2.line(self.image, (nozzleXpos - lineLength, nozzleYpos),
                         (nozzleXpos + lineLength, nozzleYpos), (0, 0, 255), 2)

                cv2.line(self.image, (nozzleXpos, nozzleYpos - lineLength), (
                    nozzleXpos, nozzleYpos + lineLength), (0, 255, 0), 2)

        with self.lock:
            self.nozzles = nozzles
        return None

    def setupCamera(self):
        self.cam = camera.selfExpCamera()
        return self.cam

    def transformImage(self, image):
        """
            Funkcija za transformacijo začetne barvne slike v primerno binarno sliko.
        """
        # convert the frame to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # apply Gaussian blur to the frame
        gray = cv2.GaussianBlur(gray, (5, 5), 2)

        # apply thresholding to the frame
        ret, thresh = cv2.threshold(
            gray, GRAYSCALE_THRESHOLD, 255, cv2.THRESH_BINARY)

        # define the kernel
        kernel = np.ones((3, 3), np.uint8)

        # erode the frame
        eroded = cv2.erode(thresh, kernel, iterations=8)

        # dilate the frame
        dilated = cv2.dilate(eroded, kernel, iterations=6)

        return dilated

    def findContours(self, image):
        """
            Funkcija za iskanje kontur na sliki.
            Vrne seznam kontur.
        """
        # find the contours
        contours, hierarchy = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return contours

    def filterContours(self, contours):
        """
            Funkcija za filtriranje kontur (robov).
        """
        # filter the contours
        filtered_contours = []
        for index, contour in enumerate(contours):
            # calculate the perimeter of the contour
            nozzleCircumference = cv2.arcLength(contour, True)
            # if the perimeter is greater than 20, the contour is a plastic object
            if nozzleCircumference > MINIMUM_OBJECT_ARC and nozzleCircumference < MAXIMUM_OBJECT_ARC:
                filtered_contours.append(contour)
                cv2.drawContours(self.image, contours, index, (0, 255, 0), 2)
        return filtered_contours

    def getCoordinates(self, contour):
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

    def getOrientation(self, objectContour):
        """
        Function to get object orientation from its contour
        Args:
            objectContour: contour of the object
        Returns:
            orientation: orientation of the object
        """
        # Default orientation is 0
        orientation = 0

        # get rotated rectangle from outer contour
        rotatedRect = cv2.minAreaRect(objectContour)
        box = cv2.boxPoints(rotatedRect)
        box = np.intp(box)

        # orientation is stored in the last element of the tuple returned by minAreaRect
        orientation = rotatedRect[-1]
        # Round orientation to 2 decimal places
        orientation = round(orientation, 2)

        # get width and height from rotated rectangle (first element is width, second is height)
        width, height = rotatedRect[-2]
        # Get orientation of the nozzle (if width is smaller than height, the nozzle is rotated 90 degrees)
        if width < height:
            orientation = orientation - 90

        rectCx, rectCy = rotatedRect[0]
        cX, cY = self.getCoordinates(objectContour)
        # Determine if the object is upside down
        isUpside = self.getTopBottomOrientation(
            rectCx, rectCy, cX, cY, orientation)
        # Fix orientation if flipped
        orientation = orientation + 180 * isUpside

        # Fix orientation if negative
        if orientation < 0:
            orientation = orientation + 360

        return 360 - orientation  # Subtracting for the rotation to rise counter-clockwise

    def getTopBottomOrientation(self, rectCx, rectCy, cX, cY, orientation):
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

    def transformFromCameraToOrigin(self, x, y):
        """
        Function to transform coordinates from camera frame to origin frame
        Args:
            x: x coordinate of the object
            y: y coordinate of the object
        Returns:
            x: x coordinate of the object in origin frame
            y: y coordinate of the object in origin frame
        """
        # Transform coordinates from camera frame to origin frame
        x = (x - ORIGIN_COORD_FROM_CAM_X) * PIXEL_TO_MM
        y = (y - ORIGIN_COORD_FROM_CAM_Y) * PIXEL_TO_MM

        # Rotate coordinates from camera frame to origin frame
        rotatedX = x * math.cos(ORIGIN_ROTATION_FROM_CAM) - \
            y * math.sin(ORIGIN_ROTATION_FROM_CAM)
        rotatedY = x * math.sin(ORIGIN_ROTATION_FROM_CAM) + \
            y * math.cos(ORIGIN_ROTATION_FROM_CAM)
        return rotatedX, rotatedY

    def detectingThread(self):
        self.running = True
        while self.running:
            self.detectNozzles()
            self.cam.showImage("image", self.image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stopDetecting()
            time.sleep(0.1)

    def startDetecting(self):
        self.thread = threading.Thread(
            target=self.detectingThread, daemon=True)
        self.thread.start()

    def stopDetecting(self):
        self.running = False


if __name__ == "__main__":
    # Create an instance of the class
    detector = NozzleDetector()
    detector.startDetecting()
    while True:
        with detector.lock:
            print(detector.nozzles)
        time.sleep(2)
