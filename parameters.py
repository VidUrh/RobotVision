import math
import json
####################################################################################################################################################################
#      CAMERA PARAMETERS                                                                                                                                           #
####################################################################################################################################################################
CAMERA_FRAME_WIDTH = 2304  # 1280
CAMERA_FRAME_HEIGHT = 1536  # 720
CAMERA_FRAME_SIZE = (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT)
CAMERA_PORT = 0
CAMERA_EXPOSURE = -7

IMAGE_PATH = None  # if none make picture if path load picture
####################################################################################################################################################################
#      CALIBRATION PARAMETERS                                                                                                                                      #
####################################################################################################################################################################
CALIBRATION_SQUARE_SIZE_M = 0.0249  # m (25 mm)
CALIBRATION_SQUARE_SIZE_MM = 24.9  # mm
CALIBRATION_SQUARE_WIDTH = 15
CALIBRATION_SQUARE_HEIGHT = 10
CALIBRATION_SQUARES = (CALIBRATION_SQUARE_WIDTH, CALIBRATION_SQUARE_HEIGHT)

CALIBRATION_IMAGE_DIR = "./images"

CORNERS_DATA_PATH = "./corners.json"
CALIBRATION_DATA_PATH = "./calibration_data.pkl"
HOMOGRAPHY_DATA_PATH = "./homography_data.pkl"

HOMOGRAPHY_SCALING_FACTOR = 100
SCALE_HOMOGRAPHY_FIELD_FACTOR = 2
# Size of the outer space scaled from the checkerboard size.
HOMOGRAPHY_FIELD_OUTER_SPACE_LEFT = 250
HOMOGRAPHY_FIELD_OUTER_SPACE_TOP = 300
HOMOGRAPHY_FIELD_OUTER_SPACE_BOTTOMRIGHT = 1.35

MATRIX_CSV_PATH = "./mtx.csv"
DIST_CSV_PATH = "./dist.csv"

####################################################################################################################################################################
#      ROBOT PARAMETERS                                                                                                                                            #    
####################################################################################################################################################################
WORLD_COORDINATE_OFFSET_PATH = "robotCalibCoordOffset.pickle"

####################################################################################################################################################################
#      DETECTION PARAMETERS                                                                                                                                        #
####################################################################################################################################################################
DEBUG_MODE = True


MAXIMUM_OBJECT_ARC = 2400
MINIMUM_OBJECT_ARC = 900
GRAYSCALE_THRESHOLD = 90


with open(CORNERS_DATA_PATH, "r") as f:
    data = json.load(f)
    origin = data["origin"]
    x = data["x"]
    # Origin point of the main coordinate system
    ORIGIN_COORD_FROM_CAM_X = origin[0]
    ORIGIN_COORD_FROM_CAM_Y = origin[1]

    # X axis point of the main coordinate system
    X_COORD_OF_X_FROM_CAM = x[0]  # 309
    Y_COORD_OF_X_FROM_CAM = x[1]  # 92

# Number of squeares between origin and X axis point
NUM_SQUARES = 8

# Parametri za izračun koordinat
ORIGIN_ROTATION_FROM_CAM = 0 #math.atan((Y_COORD_OF_X_FROM_CAM - ORIGIN_COORD_FROM_CAM_Y) / (ORIGIN_COORD_FROM_CAM_X - X_COORD_OF_X_FROM_CAM))
print("ORIGIN_ROTATION_FROM_CAM: ", math.degrees(ORIGIN_ROTATION_FROM_CAM))

PIXEL_TO_MM = (NUM_SQUARES * CALIBRATION_SQUARE_SIZE_MM)/(math.sqrt((Y_COORD_OF_X_FROM_CAM -
                                                                     ORIGIN_COORD_FROM_CAM_Y) ** 2 + (ORIGIN_COORD_FROM_CAM_X-X_COORD_OF_X_FROM_CAM)**2))

print("PIXEL_TO_MM: ", PIXEL_TO_MM)

####################################################################################################################################################################
#      ROBOT PARAMETERS                                                                                                                                           #
####################################################################################################################################################################
ROBOT_IP = "192.168.64.55"
APPROACH_NOZZLE_Z = -30
SPEED_VERY_VERY_FAST = 250
SPEED_VERY_FAST = 150
SPEED_FAST = 100
SPEED_SLOW = 20
SPEED_VERY_SLOW = 5
SPEED_MIDDLE = 80
