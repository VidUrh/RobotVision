from xarm.wrapper import XArmAPI
from parameters import *
import tkinter as tk
import vodenjeRobota as vr
import logging

import time

timeout = 2
rspeed = 70

# Constants
START_X = 400
START_Y = 0
START_Z = 3 # in mm negative value is up

SLIDER_RESOLUTION = 0.5 # in mm

# Make gui for user to set robot to base position
# Make window for user to set robot to base position with buttons and sliders in thread
# Make thread
class window:
    def __init__(self, master, robot):
        self.robot = robot
        # make empty list for 3 list of coordinates
        self.points = [[], [], []]
        self.setRotationIter = 0 # number of times set rotation button is pressed

        self.CLICK_XZ = 0

        # set start coordinates
        self.START_X = START_X
        self.START_Y = START_Y
        self.START_Z = START_Z

        self.master = master
        self.master.title("Robot calibration")
        self.master.geometry("1000x300")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Make 10x10 grid
        for i in range(10):
            self.master.columnconfigure(i, weight=1)
            self.master.rowconfigure(i, weight=1)

        self.master.bind("<Left>", self.on_key_press_y)
        self.master.bind("<Right>", self.on_key_press_y)
        self.master.bind("<Up>", self.on_key_press_x_or_z)
        self.master.bind("<Down>", self.on_key_press_x_or_z)

        # add base coord buttons, stay in while user press again
        self.btBaseCoord = tk.Button(self.master, text="Base coord", bg="#43b0f1", font=("Helvetic", 11), command=self.baseCoord)
        self.btBaseCoord.grid(row=0, column=1, sticky="nsew")

        # add user coord buttons
        self.btUserCoord = tk.Button(self.master, text="User coord", bg="#43b0f1", font=("Helvetic", 11), command=self.userCoord)
        self.btUserCoord.grid(row=0, column=0, sticky="nsew")

        # add start button
        self.btStart = tk.Button(self.master, text="Start", bg="#e2ac4d", font=("Helvetice", 11), command=self.start)
        self.btStart.grid(row=1, column=0, sticky="nsew")

        # add home button
        self.btHome = tk.Button(self.master, text="Home", bg="#e2ac4d", font=("Helvetic", 11), command=self.home)
        self.btHome.grid(row=1, column=1, sticky="nsew")

        # add check button
        self.btCheck = tk.Button(self.master, text="Check", bg="#e2ac4d", font=("Helvetic", 11), command=self.check)
        self.btCheck.grid(row=2, column=1, sticky="nsew")

        # add set rotation button
        self.btSetRotation = tk.Button(self.master, text="Set rotation", bg="#e2ac4d", font=("Helvetic", 11), command=self.setRotation)
        self.btSetRotation.grid(row=2, column=0, sticky="nsew")

        # add check origin button
        self.btCheckOrigin = tk.Button(self.master, text="Check origin", bg="#e2ac4d", font=("Helvetic", 11), command=self.checkOrigin)
        self.btCheckOrigin.grid(row=3, column=1, sticky="nsew")

        # add set origin button
        self.btSetOrigin = tk.Button(self.master, text="Set origin", bg="#e2ac4d", font=("Helvetic", 11), command=self.setOrigin)
        self.btSetOrigin.grid(row=4, column=0, sticky="nsew")

        # add done button
        self.btDone = tk.Button(self.master, text="done", bg="#e2ac4d", font=("Helvetica", 11), command=self.done)
        self.btDone.grid(row=4, column=1, sticky="nsew")

        # add slider for x axis on 1 decimal point
        self.xSlider = tk.Scale(self.master, from_=1000, to=-1000, length=1000, orient=tk.HORIZONTAL,  
                                resolution=SLIDER_RESOLUTION, label="X axis (mm)", command=self.moveX, bg="#bfecff")
        self.xSlider.bind("<Button-1>", self.clickX)
        self.xSlider.grid(row=8, column=0, columnspan=10)

        # add slider for y axis on 1 decimal point
        self.ySlider = tk.Scale(self.master, from_=1000, to=-1000, length=1000, orient=tk.HORIZONTAL,
                                resolution=SLIDER_RESOLUTION, label="Y axis (mm)", command=self.moveY, bg="#bfecff")
        self.ySlider.grid(row=9, column=0, columnspan=10)

        # add slider for z axis on 1 decimal point
        self.zSlider = tk.Scale(self.master, from_=300, to=-50, length=200, orient=tk.VERTICAL,
                                resolution=0.1, label="Z (mm)", command=self.moveZ, bg="#bfecff")
        self.zSlider.bind("<Button-1>", self.clickZ)
        self.zSlider.grid(row=0, column=9, rowspan=7, columnspan=2)
        
        # make button for 1. calibration point on right side
        self.point1 = tk.Button(self.master, text="Point 1", bg="#43b0f1", command=self.storePoint1)
        self.point1.grid(row=2, column=8, sticky="E")

        # add button for 2. calibration point on right side
        self.point2 = tk.Button(self.master, text="Point 2", background="#43b0f1", command=self.storePoint2)
        self.point2.grid(row=3, column=8, sticky="E")

        # add button for 3. calibration point on right side
        self.point3 = tk.Button(self.master, text="Point 3", background="#43b0f1", command=self.storePoint3)
        self.point3.grid(row=4, column=8, sticky="E")

        # add terminal for user to see what is happening
        self.terminal = tk.Text(self.master, height=10, width=55, bg="#bfecff", font=("Helvetica", 13))
        self.terminal.grid(row=0, column=2, columnspan=7, rowspan=5, sticky="nsw")

        self.refreshSlider()
    
    def refreshSlider(self):
        self.robotPosition = self.robot.getPosition()
        self.xSlider.set(self.robotPosition[0])
        self.ySlider.set(self.robotPosition[1])
        self.zSlider.set(self.robotPosition[2])
        print(self.robotPosition)

    def printTerminal(self, text):
        self.terminal.insert(tk.END, text)
        self.terminal.see(tk.END)

    def baseCoord(self):
        self.btBaseCoord.config(relief=tk.SUNKEN)
        self.btUserCoord.config(relief=tk.RAISED)
        self.xSlider.config(from_=80, to=400)
        self.ySlider.config(from_=250, to=-250)
        self.zSlider.config(from_=100, to=-2)
        self.xSlider.set(self.robot.getPosition()[0])
        self.ySlider.set(self.robot.getPosition()[1])
        self.zSlider.set(self.robot.getPosition()[2])
        self.START_X = 350
        self.START_Y = 0
        self.START_Z = 3
        self.printTerminal("Base coord\n")

    def userCoord(self):
        self.btUserCoord.config(relief=tk.SUNKEN)
        self.btBaseCoord.config(relief=tk.RAISED)
        self.xSlider.config(from_=-100, to=100)
        self.ySlider.config(from_=-500, to=500)
        self.zSlider.config(from_=-100, to=100)
        self.xSlider.set(self.robot.getPosition()[0])
        self.ySlider.set(self.robot.getPosition()[1])
        self.zSlider.set(self.robot.getPosition()[2])
        self.START_X = 0
        self.START_Y = 0
        self.START_Z = -3
        self.printTerminal("User coord\n")

    def start(self):
        self.printTerminal("Start robot calibration\n")
        #Move robot in zero position
        self.printTerminal("Move robot to zero position\n")
        self.robot.home()
        self.refreshSlider()
        # print start coordinates
        self.printTerminal("Start coordinates: X: "+str(self.START_X)+" Y: "+str(self.START_Y)+" Z: "+str(self.START_Z)+"\n")
        # set slider to start coordinates
        self.xSlider.set(self.START_X)
        self.ySlider.set(self.START_Y)
        self.zSlider.set(self.START_Z)
        # move robot to start coordinates in z axis
        pass

    def home(self):
        self.printTerminal("Move robot to home position\n")
        self.robot.home()
        self.refreshSlider()
        pass

    def storePoint1(self):
        self.storePoint(1)

    def storePoint2(self):
        self.storePoint(2)

    def storePoint3(self):
        self.storePoint(3)
    
    def storePoint(self, point):
        # overwrite list of coordinate to points on frst place
        self.points[point-1] = self.robot.getPosition()
        self.printTerminal("Point "+str(point)+" stored\n")
        self.printTerminal(str(self.points[point-1])+"\n")
        self.setRotationIter = 0
        pass


    def moveX(self, value):
        self.robot.move(x=value, speed=200, wait=False)
        print(value)
        pass

    def moveY(self, value):
        self.robot.move(y=value, speed=200, wait=False)
        print(value)
        pass

    def moveZ(self, value):
        self.robot.move(z=value, speed=200, wait=False)
        print(value)
        pass

    def check(self):
        # Check teach points
        self.robot.move(x = self.points[0][0], y = self.points[0][1], z = self.points[0][2], speed=100, wait=True)
        time.sleep(1)
        self.robot.move(x = self.points[1][0], y = self.points[1][1], z = self.points[1][2], speed=100, wait=True)
        time.sleep(1)
        self.robot.move(x = self.points[2][0], y = self.points[2][1], z = self.points[2][2], speed=100, wait=True)
        time.sleep(1)

    def setRotation(self):
        self.rotationOffset = self.robot.calibrateUserOrientationOffset(self.points, mode=0, trust_ind=0, input_is_radian=False, return_is_radian=False)[1]
        self.printTerminal("Rotation offset: "+str(self.rotationOffset)+"\n")

    def checkOrigin(self):
        #self.robot.move(x = 0, y = 0, z = -2, speed=100, wait=True)
        time.sleep(1)

    def setOrigin(self):
        print("Set origin")
        pass

    def done(self):
        print(self.points)
        self.master.destroy()

    def on_key_press_x_or_z(self, event):
        if self.CLICK_XZ == 0:
            self.on_key_press_x(event)
        elif self.CLICK_XZ == 1:
            self.on_key_press_z(event)

    def on_key_press_x(self, event):
        if event.keysym == "Down":
            self.xSlider.set(self.xSlider.get() - SLIDER_RESOLUTION)
        elif event.keysym == "Up":
            self.xSlider.set(self.xSlider.get() + SLIDER_RESOLUTION)

    def on_key_press_y(self, event):
        if event.keysym == "Left":
            self.ySlider.set(self.ySlider.get() + SLIDER_RESOLUTION)
        elif event.keysym == "Right":
            self.ySlider.set(self.ySlider.get() - SLIDER_RESOLUTION)

    def on_key_press_z(self, event):
        if event.keysym == "Up":
            self.zSlider.set(self.zSlider.get() + 0.1)
        elif event.keysym == "Down":
            self.zSlider.set(self.zSlider.get() - 0.1)

    def clickX(self, event):
        self.CLICK_XZ = 0 # 0 = button for x

    def clickZ(self, event):
        self.CLICK_XZ = 1 # 1 = button for z

    def on_closing(self):
        self.master.destroy()


# Start calibration
# while input("Set coordinate system of robot to base? Y/n: ") != "y":
#     pass
# robot.set_position(x = 300, y = 0,z = rZ, speed=rspeed, wait=True)


def setXYOffset(x, y, rZ, rspeed):
    robot.set_position(x = x, y = y,z = rZ, speed=rspeed, wait=True)
    while 1:
        # go to the first corner
        
        # ask user if it is ok if not, user defin move in x,y,z direction
        # if ok, move to the next corner
        if input("Is x,y ok? Y/n: ") == "n":
            x = x + float(input("Enter x: "))
            y = y + float(input("Enter y: "))
            robot.set_position(x = x, y = y,z = rZ, speed=rspeed, wait=True)
        else:
            # prin calibration check is finish
            if x==0 and y==0:  
                print("Calibration check for x,y is finish")
                break
            else:
                #x = x*(-1)
                #y = y*(-1)
                print("Calibration ofset is: x = ", -x, " y = ", -y)
                break

def setZOffset(x, y, rZ, rspeed):
    while 1:
        # check z axis
        if input("Is z ok? Y/n: ") == "n":
            rZ = rZ + float(input("Enter z: "))
            robot.set_position(x = x, y = y,z = rZ, speed=rspeed, wait=True)
        else:
            print("Calibration ofset is: z = ", -rZ)
            break

def setRotation(x, y, rZ, rspeed):
    # check rotation
    xRot = x
    yRot = y

    # Teach robot 3 points
    # make list of teach points
    points = []
    points.append(robot.get_position()[1])
    # move robot in x direction
    setXYOffset(xRot, yRot, rZ, rspeed)
    points.append(robot.get_position()[1])

    # move robot in y direction
    setXYOffset(200, yRot, rZ, rspeed)
    points.append(robot.get_position()[1])

    # Check teach points
    robot.set_position(x = points[0][0], y = points[0][1], z = points[0][2], speed=rspeed, wait=True)
    time.sleep(1)
    robot.set_position(x = points[1][0], y = points[1][1], z = points[1][2], speed=rspeed, wait=True)
    time.sleep(1)
    robot.set_position(x = points[2][0], y = points[2][1], z = points[2][2], speed=rspeed, wait=True)
    time.sleep(1)

    print("Teach points are: ", points)
    rotationOffset = robot.calibrate_user_orientation_offset(points, mode=0, trust_ind=0, input_is_radian=False, return_is_radian=False)[1]
    rotationOffset = list(map(lambda x: -x, rotationOffset))
    print("Rotation offset is: ", rotationOffset)
    robot.set_position(x = x, y = y, z = rZ, yaw = yaw, speed=rspeed, is_radian = False, wait=True)
    
    # move robot in x direction
    robot.set_position(x = x, y = y, z = rZ, speed=rspeed, wait=True)
    for i in range (1, 6):
        robot.set_position(x = x+(i*CALIBRATION_SQUARE_SIZE), y = y, z = rZ, speed=rspeed, wait=True)
    print(robot.get_position())
    robot.set_position(x = x, y = y, z = rZ, speed=rspeed, wait=True)

def checkRotation():
    # move robot in x direction
    while 1:
        robot.set_position(x = 0, y = 0, z = -2, speed=rspeed, wait=True)
        for i in range (1, 6):
            robot.set_position(x = (i*CALIBRATION_SQUARE_SIZE), y = 0, z = rZ, speed=rspeed, wait=True)
        print(robot.get_position())
        robot.set_position(x = 0, y = 0, z = -2, speed=rspeed, wait=True)
        if input("Will finish? Y/n: ") == "y":
            break

def main():
    logger = logging.getLogger()
    robot = vr.Robot(ROBOT_IP, logger)
    calibWindow = window(tk.Tk(), robot=robot)
    # open window
    calibWindow.master.mainloop()


if __name__ == "__main__":
    main()
    pass
    #setXYOffset(x, y, rZ, rspeed)
    #setRotation(x, y, rZ, rspeed)
    #setZOffset(x, y, rZ, rspeed)
    #checkRotation()


# while 1:
#     for j in range (0, 2):
#         robot.set_position(x = x, y = y, z = rZ, yaw = yaw, speed=rspeed, is_radian = True, wait=True)
#         # move robot in x direction
#         for i in range (1, 6):
#             robot.set_position(x = x+(i*CALIBRATION_SQUARE_SIZE), y = y, z = rZ, yaw = yaw, speed=rspeed, is_radian=True, wait=True)
#         print(robot.get_position())
#         robot.set_position(x = x, y = y, z = rZ, yaw = yaw, speed=rspeed, is_radian=True, wait=True)
        
#         inChar = input("Is rotation ok? Y/n or c for continue: ")
#         if inChar == "n":
#             print("Previous yaw is: ", yaw)
#             yaw = yaw + float(input("Enter yaw offset: "))
#             print("New yaw is: ", yaw)    
#         elif inChar == "c":
#             continue
#         else:
#             print("Calibration ofset is: yaw = ", -yaw)
#             exit()
        