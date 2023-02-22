import csv
import numpy as np
import pickle
from parameters import *

with open(DIST_CSV_PATH, 'r') as f:
    reader = csv.reader(f)
    dist = np.array(list(reader)).astype('float')

with open(MATRIX_CSV_PATH, 'r') as f:
    reader = csv.reader(f)
    cameraMatrix = np.array(list(reader)).astype('float')

calibrationData = {
    "cameraMatrix": cameraMatrix,
    "dist": dist,
}
with open(CALIBRATION_DATA_PATH, "wb") as f:
    print(calibrationData)
    pickle.dump(calibrationData, f)
    print(f"Calibration data saved to {CALIBRATION_DATA_PATH}")
