import cv2
import logging
from parameters import *
import numpy as np
import pandas as pd
import pickle
import time

'''
Ta skripta je namenjena za testiranje kamere in njene kalibracije.
Najprej zajamemo sliko kamere.
Nato uporabimo kalibracijske parametere in z njimi popravimo sliko.
Ko smo sliko popravili, na njej najdemo vse kvadrate in jih označimo.
Izračunamo dimenzije vseh kvadratov in jih izpišemo na sliki.
Sledi preverjanje ali so kvadrati pravilno označeni in ali so dimenzije pravilne (kvadrati imajo znane dimenzije).
Na koncu vse dimenzije primerjamo in izračunamo napako med njimi.
'''
####################################################################################################
#       Naložimo kalibracijske parametre
####################################################################################################


####################################################################################################
#       Zajemi sliko kamere
####################################################################################################
def getImage():
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
    cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    cam.set(cv2.CAP_PROP_EXPOSURE, -8)
    time.sleep(1)

    ret, image = cam.read()
    if not ret:
        logging.error("Could not read image from camera")
    
    cam.release()
    return image

####################################################################################################
#       Undistort slike kamere
####################################################################################################
def undistortImage(image):
    # Read camera calibration data
    with open(CALIBRATION_DATA_PATH, 'rb') as calibrationFile:
        data = pickle.load(calibrationFile)
        cameraMatrix = data['cameraMatrix']
        dist = data['dist']
        rvecs = data['rvecs']
        tvecs = data['tvecs']
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        cameraMatrix, dist, (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT), 1, (CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT))
    
    # Undistort image
    imageUndistorted = cv2.undistort(image, newcameramtx, dist)
    return imageUndistorted


####################################################################################################
#       Popravimo sliko kamere
####################################################################################################
def correctImage(image):
    # convert image to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('imageGray', imageGray)

    # apply gaussian blur to the image
    imageBlur = cv2.medianBlur(imageGray, 3)
    #cv2.imshow('imageBlur', imageBlur)

    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(imageBlur, 0, sharpen_kernel)

    return sharpen


####################################################################################################
#       Na sliki najdemo vse kvadrate in jih označimo
####################################################################################################
def findSquares(sharpen, image):
    results = pd.DataFrame(columns=['squarePlace','squareSize','error'])
    # Threshold and morph close
    thresh = cv2.threshold(sharpen, 160, 255, cv2.THRESH_BINARY)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Find contours and filter using threshold area, start in top left corner
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    min_area = 9000
    max_area = 100000
    for c in cnts:
        area = cv2.contourArea(c)
        if area > min_area and area < max_area:
            x,y,w,h = cv2.boundingRect(c)
            if w-h < 10 and w-h > -10:
                # Obkrožimo kvadrate
                cv2.drawContours(image, [c], -1, (36,255,12), 2)

                # Napiši velikost kvadrata v center kvadrata na sliki
                squarePlace,squareSize,angle = cv2.minAreaRect(c)
                
                # Zaokroiži velikost na 2 decimalki
                squareSize = (round(squareSize[0],2), round(squareSize[1],2))
                
                # Izračunamo napako med dimenzijami
                error = squareSize[0] - squareSize[1]
                error = abs(round(error,2))

                # Zaokroži pozicijo kvadrata na 0 decimalk
                squarePlace = (round(squarePlace[0],0), round(squarePlace[1],0))

                # Izračunamo realno velikost kvadrata
                # realSquareSize = (round(squareSize[0] * PIXEL_TO_MM,2), round(squareSize[1] * PIXEL_TO_MM,2))
                
                #print('Square: ', squarePlace, 'Size: ', squareSize, 'Error: ', error)
                # Dodamo rezultate v tabelo
                results = results.append({'squarePlace': squarePlace, 'squareSize': squareSize, 'error': error}, ignore_index=True)
                #print(results)

                # Napiši(blue) velikost kvadrata v center kvadrata na sliki
                cv2.putText(image, str(squareSize), (int(squarePlace[0]-70), int(squarePlace[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
            
    return image, results

# cv2.imshow('sharpen', sharpen)
# cv2.imshow('close', close)
# cv2.imshow('thresh', thresh)
# cv2.imshow('kernel', kernel)
# cv2.imshow('image', image)
# # close camera
# cam.release()
# cv2.waitKey(0)



####################################################################################################
#       Izračunamo dimenzije vseh kvadratov in jih izpišemo na sliki
####################################################################################################


####################################################################################################
#       Prikaz slike
####################################################################################################
def showImage(name, image, wait=0):
    cv2.imshow(name, image)
    if wait == 1:
        cv2.waitKey(0)

####################################################################################################
#       Izračun napake med dimenzijami
####################################################################################################


####################################################################################################
#       Izpišemo rezultate
####################################################################################################
cv2.destroyAllWindows()

####################################################################################################
#       MAIN
####################################################################################################
def main():
    resultsDistorted = pd.DataFrame(columns=['image','squarePlace','squareSize','error']) # Table for results
    resulrUndistorted = pd.DataFrame(columns=['image','squarePlace','squareSize','error']) # Table for results
    for i in range(0, 5):
        # Get image
        image = getImage()
        imageDistorted = image.copy()
        imageUndistorted = image.copy()

        # Distorted image
        sharpen = correctImage(imageDistorted) # Remove noise from image
        imageDistorted, result = findSquares(sharpen, imageDistorted) # Na sliki najdemo vse kvadrate in jih označimo
        
        result['image'] = i # Add image number to results
        resultsDistorted = resultsDistorted.append(result, ignore_index=True)

        # Undistorted image
        imageUndistorted = undistortImage(imageUndistorted)
        sharpen = correctImage(imageUndistorted) # Remove noise from image
        imageUndistorted, result = findSquares(sharpen, imageUndistorted) # Na sliki najdemo vse kvadrate in jih označimo
        
        result['image'] = i # Add image number to results
        resulrUndistorted = resulrUndistorted.append(result, ignore_index=True)

    # Show image
    showImage('Original', image, 0)
    showImage('Distorted', imageDistorted, 0)
    showImage('Undistorted', imageUndistorted, 0)

    # Sortiraj po squarePlace
    # results = results.sort_values(by=['squarePlace'])
    # print(results)

    # Calculate average error for each square place
    # square place can differ for 20 pixel
    pixelDiff = 20
    resultsDistorted['squarePlace'] = resultsDistorted['squarePlace'].apply(lambda x: (round(x[0]/pixelDiff)*pixelDiff, round(x[1]/pixelDiff)*pixelDiff))
    resultsDistorted = resultsDistorted.groupby(['squarePlace']).mean()
    resultsDistorted = resultsDistorted.reset_index()
    print("Distorted")
    print(resultsDistorted)

    resulrUndistorted['squarePlace'] = resulrUndistorted['squarePlace'].apply(lambda x: (round(x[0]/pixelDiff)*pixelDiff, round(x[1]/pixelDiff)*pixelDiff))
    resulrUndistorted = resulrUndistorted.groupby(['squarePlace']).mean()
    resulrUndistorted = resulrUndistorted.reset_index()
    print("Undistorted")
    print(resulrUndistorted)

    # Calculate average error in undistorted image and distorted image and compare them
    errorDistorted = resultsDistorted['error'].mean()
    errorUndistorted = resulrUndistorted['error'].mean()
    print("Error Distorted: ", errorDistorted)
    print("Error Undistorted: ", errorUndistorted)

    cv2.waitKey(0)


if __name__ == "__main__":
    main()
    pass