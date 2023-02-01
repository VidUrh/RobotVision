"""
This script is used to calculate the transformation matrix between poses.
"""

Z = 720 # Distance between camera and object plane in mm
X = 183 # origin X coordinate in pixels
Y = 97 # origin Y coordinate in pixels


pcm = 0.7614 # Pixel to mm conversion factor

def getCoordinatesInVmesniCoor(x, y):
    """
    Function to get coordinates in vmesni coordinate system
    Args:
        x: x coordinate of the object in camera coordinates
        y: y coordinate of the object in camera coordinates
    Returns:
        x: x coordinate of the object in vmesni koord
        y: y coordinate of the object in vmesni koord
    """
    x = (x - X) * pcm
    y = (y - Y) * pcm
    return x, y, Z

def getCoordinatesFromVmesniCoor(x,y):
    x = x / pcm + X
    y = y / pcm + Y
    return x, y

