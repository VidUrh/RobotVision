import math
####################################################################################################################################################################
#      CAMERA PARAMETERS                                                                                                                                           #
####################################################################################################################################################################
CAMERA_FRAME_WIDTH = 1280
CAMERA_FRAME_HEIGHT = 720
CAMERA_FRAME_SIZE = (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT)
CAMERA_PORT = 1
CAMERA_EXPOSURE = -5

####################################################################################################################################################################
#      CALIBRATION PARAMETERS                                                                                                                                      #
####################################################################################################################################################################
CALIBRATION_SQUARE_SIZE = 0.025
CALIBRATION_SQUARE_WIDTH = 10
CALIBRATION_SQUARE_HEIGHT = 7
CALIBRATION_SQUARES = (CALIBRATION_SQUARE_WIDTH, CALIBRATION_SQUARE_HEIGHT)

CALIBRATION_IMAGE_DIR = "./images"
CALIBRATION_DATA_PATH = "./calibration_data.pkl"

####################################################################################################################################################################
#      DETECTION PARAMETERS                                                                                                                                        #
####################################################################################################################################################################
MAXIMUM_OBJECT_AREA = 600
MINIMUM_OBJECT_AREA = 400
GRAYSCALE_THRESHOLD = 100

# Origin point of the main coordinate system
ORIGIN_COORD_FROM_CAM_X = 402  # 141
ORIGIN_COORD_FROM_CAM_Y = 326  # 208

# X axis point of the main coordinate system
X_COORD_OF_X_FROM_CAM = 647  # 309
Y_COORD_OF_X_FROM_CAM = 154  # 92

# Number of squeares between origin and X axis point
NUM_SQUARES = 8

# Parametri za izračun koordinat
ORIGIN_ROTATION_FROM_CAM = math.atan((Y_COORD_OF_X_FROM_CAM - ORIGIN_COORD_FROM_CAM_Y) /
                                     (ORIGIN_COORD_FROM_CAM_X - X_COORD_OF_X_FROM_CAM))

PIXEL_TO_MM = (NUM_SQUARES * CALIBRATION_SQUARE_SIZE)/(math.sqrt((Y_COORD_OF_X_FROM_CAM -
                                                                  ORIGIN_COORD_FROM_CAM_Y) ** 2 + (ORIGIN_COORD_FROM_CAM_X-X_COORD_OF_X_FROM_CAM)**2))


####################################################################################################################################################################
#      ROBOT PARAMETERS                                                                                                                                           #
####################################################################################################################################################################
ROBOT_IP = "192.168.64.55"
APPROACH_NOZZLE_Z = -20
SPEED_FAST = 100
SPEED_SLOW = 20
SPEED_VERY_SLOW = 5
SPEED_MIDDLE = 80