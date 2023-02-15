'''
Camera class for capturing images from camera and saving them to disk

Parameters
----------
CAMERA_PORT : int Camera port
CAMERA_EXPOSURE : int Camera exposure
CAMERA_FRAME_WIDTH : int Camera frame width
CAMERA_FRAME_HEIGHT : int Camera frame height
CALIBRATION_DATA_PATH : str Path to calibration data
'''
import cv2
from parameters import *
import logging
import pickle

class Camera:
    def __init__(self):
        # Initialize camera
        self.cam = cv2.VideoCapture(CAMERA_PORT, cv2.CAP_DSHOW)
        self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self.cam.set(cv2.CAP_PROP_EXPOSURE, CAMERA_EXPOSURE)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)

        print("Exposure: ", self.cam.get(cv2.CAP_PROP_EXPOSURE))
        with open(CALIBRATION_DATA_PATH, 'rb') as calibrationFile:
            data = pickle.load(calibrationFile)
            cameraMatrix = data['cameraMatrix']
            dist = data['dist']
            self.dist = dist
            rvecs = data['rvecs']
            tvecs = data['tvecs']
            self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(
        cameraMatrix, dist, (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT), 1, (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT))

    def getImage(self):
        self.ret, self.image = self.cam.read()
        if not self.ret:
            logging.error("Failed to grab frame")
            exit(1)

        return self.ret, self.image
    
    def getUndistortedImage(self):
        image = self.getImage()

        self.image = cv2.undistort(self.image, self.newcameramtx, self.dist)
        return self.ret, self.image

    def saveImage(self, path, image, number='', extension=".png"):
        if image is None:
            return None
        
        path = path + "image" + str(number) + extension
        cv2.imwrite(path, image)
        return image
    
    def loadImage(self, path, number, extension):
        path = path + "image" + str(number) + extension
        image = cv2.imread(path)
        return image

    def showImage(self, name, image, ms=-1):
        '''
        Show image with name and wait for ms milliseconds
        
        Parameters
        ----------
        name : str Name of the window
        image : numpy.ndarray Image to show
        ms : int Time to wait for key press
        '''
        cv2.imshow(name, image)
        if ms != -1:
            key = cv2.waitKey(ms)
            return key
            
    
    def release(self):
        self.cam.release()
        logging.info("Camera released")

    def destroyAllWindows(self):
        try:
            cv2.destroyAllWindows()
            logging.info("Camera and windows destroyed")
        except:
            logging.info("Windows already destroyed")

    def __del__(self):
        self.cam.release()
        logging.info("Camera released")
        try:
            cv2.destroyAllWindows()
            logging.info("Camera and windows destroyed")
        except:
            logging.info("Windows already destroyed")

if __name__ == "__main__":
    # Test camera class
    cam = Camera()
    ret, image = cam.getImage()
    cam.showImage("test", image)
    cam.saveImage("test", image, 1, ".png")
    image = cam.loadImage("test", 1, ".png")
    cam.showImage("test1", image, 0)

