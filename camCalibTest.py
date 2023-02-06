import cv2
import logging
from parameters import *
import numpy as np

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
# find camera port
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.7)
#cam.set(cv2.CAP_PROP_EXPOSURE, -5)

ret, image = cam.read()
if not ret:
    logging.error("Could not read image from camera")

####################################################################################################
#       Popravimo sliko kamere
####################################################################################################
# convert image to grayscale
imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#cv2.imshow('imageGray', imageGray)

# apply gaussian blur to the image
imageBlur = cv2.medianBlur(imageGray, 3)
#cv2.imshow('imageBlur', imageBlur)

sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
sharpen = cv2.filter2D(imageBlur, 0, sharpen_kernel)


####################################################################################################
#       Na sliki najdemo vse kvadrate in jih označimo
####################################################################################################
# Threshold and morph close
thresh = cv2.threshold(sharpen, 160, 255, cv2.THRESH_BINARY)[1]
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

# Find contours and filter using threshold area
cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

min_area = 9000
max_area = 100000
image_number = 0
for c in cnts:
    area = cv2.contourArea(c)
    if area > min_area and area < max_area:
        x,y,w,h = cv2.boundingRect(c)
        print(str(image_number) + " distance = " + str(w-h))
        if w-h < 10 and w-h > -10:
            ROI = image[y:y+h, x:x+w]
            #cv2.imwrite('ROI_{}.png'.format(image_number), ROI)
            print(cv2.minAreaRect(c))
            cv2.drawContours(image, [c], -1, (36,255,12), 2)
            image_number += 1

# cv2.imshow('sharpen', sharpen)
# cv2.imshow('close', close)
# cv2.imshow('thresh', thresh)
# cv2.imshow('kernel', kernel)
cv2.imshow('image', image)
# close camera
cam.release()
cv2.waitKey(0)



####################################################################################################
#       Izračunamo dimenzije vseh kvadratov in jih izpišemo na sliki
####################################################################################################


####################################################################################################
#       Prikaz slike
####################################################################################################


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
if __name__ == "__main__":
    
    pass