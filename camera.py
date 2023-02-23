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
    '''
    Camera class for handling camera and images operations
    '''

    def __init__(self, cam):
        # Initialize camera
        self.cam = cam
        self.homographyMatrix = None

        with open(CALIBRATION_DATA_PATH, 'rb') as calibrationFile:
            data = pickle.load(calibrationFile)
            cameraMatrix = data['cameraMatrix']
            dist = data['dist']
            self.dist = dist
            self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(
                cameraMatrix, dist, (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT), 1, (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT))

        with open(HOMOGRAPHY_DATA_PATH, 'rb') as homographyFile:
            self.homographyMatrix = pickle.load(homographyFile)

    def getImage(self):
        '''
        Get image from camera

        Returns
        -------
        ret : bool True if image is captured
        image : numpy.ndarray Captured image

        Raises
        ------
        logging.error : Failed to grab frame
        '''
        self.ret, self.image = self.cam.read()
        if not self.ret:
            logging.error("Failed to grab frame")
            exit(1)

        return self.ret, self.image

    def getUndistortedImage(self, path=None):
        '''
        Get undistorted image from camera

        Returns
        -------
        ret : bool True if image is captured
        image : numpy.ndarray Captured image

        Raises
        ------
        logging.error : Failed to grab frame
        '''
        if path == None:
            self.ret, self.image = self.getImage()
        else:
            self.image = self.loadImage(path)
            self.ret = True

        self.image = cv2.undistort(self.image, self.newcameramtx, self.dist)
        cv2.imwrite("undistorted.jpg", self.image)

        return self.ret, self.image

    # make function which undistort and warp image
    def getdWarpedImage(self, path=None):
        '''
        Get undistorted and warped image from camera

        Returns
        -------
        ret : bool True if image is captured
        image : numpy.ndarray Captured image
        '''
        if path == None:
            self.ret, self.image = self.getImage()
        else:
            self.image = self.loadImage(path=path)
            self.ret = True

        self.image = cv2.undistort(self.image, self.newcameramtx, self.dist)
        self.image = self.warpPerspective(self.image)
        cv2.imwrite("warped.jpg", self.image)

        return self.ret, self.image
    
    def warpImage(self, image):
        """
        Function to warp perspective of image and returns transformed image.
        Args:
            image (numpy.ndarray): Image to be transformed.
        Returns:
            transformed_img (numpy.ndarray): Transformed image.
        """
        self.image = cv2.undistort(self.image, self.newcameramtx, self.dist)
        self.image = self.warpPerspective(self.image)

        return self.image

    def warpPerspective(self, image):
        """
        Function to warp perspective of image and returns transformed image.
        Args:
            image (numpy.ndarray): Image to be transformed.
        Returns:
            transformed_img (numpy.ndarray): Transformed image.
        """

        transformed_img = cv2.warpPerspective(
            image, self.homographyMatrix,  (int(HOMOGRAPHY_SCALING_FACTOR * CALIBRATION_SQUARE_WIDTH * HOMOGRAPHY_FIELD_OUTER_SPACE_BOTTOMRIGHT),
                                            int(HOMOGRAPHY_SCALING_FACTOR * CALIBRATION_SQUARE_HEIGHT * HOMOGRAPHY_FIELD_OUTER_SPACE_BOTTOMRIGHT)))

        return transformed_img
    
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


    def saveImage(self, path, image, number='', extension=".png"):
        '''
        Save image to path with number and extension

        Parameters
        ----------
        path : str Path to save image
        image : numpy.ndarray Image to save
        number : int Number of image
        extension : str Extension of image
        '''
        if image is None:
            return None

        path = path + "image" + str(number) + extension
        cv2.imwrite(path, image)
        return image

    def loadImage(self, path):
        '''
        Load image from path with number and extension

        Parameters
        ----------
        path : str Path to load image
        number : int Number of image
        extension : str Extension of image

        Returns
        -------
        image : numpy.ndarray Loaded image
        '''
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

        Returns
        -------
        key : int Key pressed
        '''
        image = cv2.resize(image,(768*2,512*2))
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
        '''
        Release camera and destroy windows

        Raises
        ------
        logging.info : Camera released
        logging.info : Camera and windows destroyed
        logging.info : Windows already destroyed
        '''
        if IMAGE_PATH == None:
            self.cam.release()

        logging.info("Camera released")
        try:
            cv2.destroyAllWindows()
            logging.info("Camera and windows destroyed")
        except:
            logging.info("Windows already destroyed")


class selfExpCamera(Camera):
    '''
    selfExpCamera class for handling camera and images operations for self exposure mode
    '''

    def __init__(self):
        if IMAGE_PATH == None:
            self.cam = cv2.VideoCapture(CAMERA_PORT, cv2.CAP_DSHOW)
            self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            self.cam.set(cv2.CAP_PROP_EXPOSURE, CAMERA_EXPOSURE)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
            print(self.cam.get(cv2.CAP_PROP_EXPOSURE))
        else:
            self.cam = None

        # initialize camera class
        Camera.__init__(self, self.cam)


class autoExpCamera(Camera):
    '''
    autoCamera class for handling camera and images operations for auto exposure mode
    '''
    def __init__(self):
        if IMAGE_PATH == None:
            self.cam = cv2.VideoCapture(CAMERA_PORT, cv2.CAP_DSHOW)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
            self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            self.cam.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.cam.set(cv2.CAP_PROP_AUTO_WB, 1)
        else:
            self.cam = None

        # initialize camera class
        Camera.__init__(self, self.cam)

        self.image = None
        self.alpha = None
        self.beta = None

    def imageSettings(self):
        '''
        Function for setting image settings with convertScaleAbs function
        alpha = 300/100 -> min 0, max 3
        beta = 200-100 -> min -100, max 100
        '''
        cv2.namedWindow('image')
        # Hue is from 0-179 for Opencv
        cv2.createTrackbar('Aplha', 'image', 0, 300, self.setAlpha)
        cv2.createTrackbar('Beta', 'image', 0, 200, self.setBeta)
        cv2.setTrackbarPos('Aplha', 'image', 100)
        cv2.setTrackbarPos('Beta', 'image', 100)
        self.image = Camera.getImage(self)[1]
        cv2.imshow('image', self.image)
        cv2.moveWindow('image', 0, 0)

        while True:
            self.image = Camera.getImage(self)[1]
            print(self.alpha, self.beta)
            adjImage = cv2.convertScaleAbs(
                self.image, alpha=self.alpha, beta=self.beta)
            cv2.imshow('image', adjImage)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break

    def setAlpha(self, x):
        self.alpha = x / 100
        # print(alpha)
        self.image = cv2.convertScaleAbs(self.image, alpha=self.alpha, beta=self.beta)
        cv2.imshow('image', self.image)

    def setBeta(self, x):
        self.beta = x - 100
        # print(beta)
        self.image = cv2.convertScaleAbs(self.image, alpha=self.alpha, beta=self.beta)
        cv2.imshow('image', self.image)

    def setBrightness(self, image, alpha=None, beta=None):
        '''
        Function for setting image brightness with convertScaleAbs function
        '''
        if alpha == None:
            alpha = self.alpha
        if beta == None:
            beta = self.beta
        print("alpha: ", alpha, "beta: ", beta)
        setImage = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        cv2.imshow('image da je', setImage)
        cv2.waitKey(0)

        return setImage


# Main functions or tests
def selfExpCameraMain():
    # Test camera class
    expCam = selfExpCamera()  # Initialize camera with self exposure
    cam = expCam.cam
    ret, image = cam.getImage()
    cam.showImage("test", image)
    cam.saveImage("test", image, 1, ".png")
    image = cam.loadImage("test", 1, ".png")
    cam.showImage("test1", image, 0)


def autoExpCameraMain():
    autoCam = autoExpCamera()  # Initialize camera with auto exposure
    cam = autoCam.cam
    while True:
        _, image = cam.getImage()
        if cam.showImage("test", image, 1) == ord('q'):
            break


def imageSettingsMain():
    cam = autoExpCamera()
    cam.imageSettings()


def test():
    cam = autoExpCamera()
    cam.imageSettings()
    while True:
        _, image = cam.getImage()
        if cam.showImage("test", image, 1) == ord('q'):
            break


if __name__ == "__main__":
    # selfExpCameraMain()
    # autoExpCameraMain()
    # imageSettingsMain()
    test()
