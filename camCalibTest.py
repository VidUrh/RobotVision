import cv2
import logging

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
#cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cam.set(cv2.CAP_PROP_EXPOSURE, -5)

ret, image = cam.read()
if not ret:
    logging.error("Could not read image from camera")

####################################################################################################
#       Popravimo sliko kamere
####################################################################################################


####################################################################################################
#       Na sliki najdemo vse kvadrate in jih označimo
####################################################################################################


####################################################################################################
#       Izračunamo dimenzije vseh kvadratov in jih izpišemo na sliki
####################################################################################################


####################################################################################################
#       Prikaz slike
####################################################################################################
cv2.imshow('image', image)
cv2.waitKey(0)


####################################################################################################
#       Izračun napake med dimenzijami
####################################################################################################


####################################################################################################
#       Izpišemo rezultate
####################################################################################################
