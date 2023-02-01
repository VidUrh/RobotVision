"""
This script is responsible for reading the camera and detecting objects.
It constantly stores the objects and returns them when requested.
"""
import cv2
import numpy as np
import time
import logging
import threading
import pickle
import math
import time
from parameters import *
from objectDetection import extractPlasticObjects, getCoordinates, getOrientation


class ObjectDetectionThread(threading.Thread):
    detectedObjectsArray = []
    detectedObjectsArrayLock = threading.Lock()
    stopThread = False
    stopThreadLock = threading.Lock()
    cam = None

    def __init__(self):
        self.cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self.cam.set(cv2.CAP_PROP_EXPOSURE, CAMERA_EXPOSURE)

        # Read camera calibration data
        import pickle
        with open("Clean\\calibrationData.pkl", 'rb') as f:
            data = pickle.load(f)
            self.mtx = data['mtx']
            self.dist = data['dist']

        self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(
            self.mtx, self.dist, (FRAME_WIDTH, FRAME_HEIGHT), 1, (FRAME_WIDTH, FRAME_HEIGHT))
        super().__init__()

    def run(self):
        while True:
            with self.stopThreadLock:
                if self.stopThread:
                    break
            self.detectObjects()
            time.sleep(0.1)

    def detectObjects(self):
        # Read the image
        ret, img = self.cam.read()
        if not ret:
            logging.error("Could not read image from camera")
            return

        # Undistort the image
        dst = cv2.undistort(img, self.mtx, self.dist, None, self.newcameramtx)
        x, y, w, h = self.roi
        img = dst[y:y+h, x:x+w]

        # Detect objects
        img, objects = extractPlasticObjects(img)   
        cv2.imshow("drawn",img)
        with self.detectedObjectsArrayLock:
            self.detectedObjectsArray = objects

        if cv2.waitKey(1) & 0xFF == ord('q'):
            with self.stopThreadLock:
                self.stopThread = True
    
    def getObjects(self):
        time.sleep(0.2)
        with self.detectedObjectsArrayLock:
            return self.detectedObjectsArray

if __name__ == "__main__":
    # start the thread
    objectDetectionThread = ObjectDetectionThread()
    objectDetectionThread.start()
    while 1:
        with objectDetectionThread.detectedObjectsArrayLock:
            print(objectDetectionThread.detectedObjectsArray)
        time.sleep(1) 
