import math
import json
####################################################################################################################################################################
#      CAMERA PARAMETERS                                                                                                                                           #
####################################################################################################################################################################
CAMERA_FRAME_WIDTH = 1280
CAMERA_FRAME_HEIGHT = 720
CAMERA_FRAME_SIZE = (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT)
CAMERA_PORT = 0
CAMERA_EXPOSURE = -7

####################################################################################################################################################################
#      CALIBRATION PARAMETERS                                                                                                                                      #
####################################################################################################################################################################
CALIBRATION_SQUARE_SIZE_M = 0.025 # m (25 mm)
CALIBRATION_SQUARE_SIZE_MM = 25 # mm
CALIBRATION_SQUARE_WIDTH = 10
CALIBRATION_SQUARE_HEIGHT = 7
CALIBRATION_SQUARES = (CALIBRATION_SQUARE_WIDTH, CALIBRATION_SQUARE_HEIGHT)

CALIBRATION_IMAGE_DIR = "./images"
CALIBRATION_DATA_PATH = "./calibration_data.pkl"

####################################################################################################################################################################
#      DETECTION PARAMETERS                                                                                                                                        #
####################################################################################################################################################################
MAXIMUM_OBJECT_ARC = 600
MINIMUM_OBJECT_ARC = 400
GRAYSCALE_THRESHOLD = 90


with open("corners.json", "r") as f:
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
ORIGIN_ROTATION_FROM_CAM = -math.atan((Y_COORD_OF_X_FROM_CAM - ORIGIN_COORD_FROM_CAM_Y) /
                                     (ORIGIN_COORD_FROM_CAM_X - X_COORD_OF_X_FROM_CAM))
print("ORIGIN_ROTATION_FROM_CAM: ", math.degrees(ORIGIN_ROTATION_FROM_CAM))

PIXEL_TO_MM = (NUM_SQUARES * CALIBRATION_SQUARE_SIZE_MM)/(math.sqrt((Y_COORD_OF_X_FROM_CAM -
                                                                  ORIGIN_COORD_FROM_CAM_Y) ** 2 + (ORIGIN_COORD_FROM_CAM_X-X_COORD_OF_X_FROM_CAM)**2))

print("PIXEL_TO_MM: ", PIXEL_TO_MM)

####################################################################################################################################################################
#      ROBOT PARAMETERS                                                                                                                                           #
####################################################################################################################################################################
ROBOT_IP = "192.168.64.55"
APPROACH_NOZZLE_Z = -30
SPEED_FAST = 100
SPEED_SLOW = 20
SPEED_VERY_SLOW = 5
SPEED_MIDDLE = 80