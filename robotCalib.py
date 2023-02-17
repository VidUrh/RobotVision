from xarm.wrapper import XArmAPI
from parameters import *
import tkinter as tk
import vodenjeRobota as vr
import logging
import time
import threading
import pickle
import os

timeout = 2
rspeed = 70

# Constants
START_X = 150
START_Y = -100
START_Z = 0 # in mm negative value is up

SLIDER_RESOLUTION = 0.5 # in mm

# Make gui for user to set robot to base position
class App:
    def __init__(self, master, robot=None):
        self.robot = robot
        # make empty list for 3 list of coordinates
        self.points = [[], [], []]
        self.coordOffset = [[], [], [], [], [], []]

        self.mvacc = 500
        self.robotSpeed = 120

        self.CLICK_XZ = 0
        self.COORD_SYSTEM = 1 # 0 for base, 1 for user

        # set start coordinates
        self.START_X = START_X
        self.START_Y = START_Y
        self.START_Z = START_Z

        self._job = None # for slider delay

        self.pointPklPath = 'robotCalibPoints.pickle'
        self.coordOffPklPath = 'robotCalibCoordOffset.pickle'

        self.master = master
        self.master.title("Robot calibration")
        self.master.geometry("1000x300")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.master.destroy)
        # Make 10x10 grid
        for i in range(10):
            self.master.columnconfigure(i, weight=1)
            self.master.rowconfigure(i, weight=1)

        self.master.bind("<Left>",  self.on_key_press_y)
        self.master.bind("<Right>", self.on_key_press_y)
        self.master.bind("<Up>",    self.on_key_press_x_or_z)
        self.master.bind("<Down>",  self.on_key_press_x_or_z)

        # add base coord buttons, stay in while user press again
        self.btCoord = tk.Button(self.master, text="Base coord", bg="#43b0f1", font=("Helvetic", 13), command=self.coord)
        self.btCoord.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # add start button
        self.btStart = tk.Button(self.master, text="Start", bg="#e2ac4d", font=("Helvetice", 11), command=self.start)
        self.btStart.grid(row=1, column=0, sticky="nsew")

        # add home button
        self.btHome = tk.Button(self.master, text="Home", bg="#e2ac4d", font=("Helvetic", 11), command=self.home)
        self.btHome.grid(row=1, column=1, sticky="nsew")

        # add check points button
        self.btCheckPoints = tk.Button(self.master, text="Check points", bg="#e2ac4d", font=("Helvetic", 11), command=self.check_points)
        self.btCheckPoints.grid(row=2, column=1, sticky="nsew")

        # add set rotation button
        self.btSetRotation = tk.Button(self.master, text="Set rotation", bg="#e2ac4d", font=("Helvetic", 11), command=self.set_rotation)
        self.btSetRotation.grid(row=2, column=0, sticky="nsew")

        # add check origin button
        self.btCheckOrigin = tk.Button(self.master, text="Check origin", bg="#e2ac4d", font=("Helvetic", 11), command=self.check_origin)
        self.btCheckOrigin.grid(row=3, column=1, sticky="nsew")

        # add set origin button
        self.btSetOrigin = tk.Button(self.master, text="Set origin", bg="#e2ac4d", font=("Helvetic", 11), command=self.set_origin)
        self.btSetOrigin.grid(row=3, column=0, sticky="nsew")

        # add done button
        self.btDone = tk.Button(self.master, text="done", bg="#e2ac4d", font=("Helvetica", 11), command=self.done)
        self.btDone.grid(row=4, column=0, sticky="nsew")

        # add stop button in red color
        self.btStop = tk.Button(self.master, text="Stop", bg="#ff0000", font=("Helvetica", 11), command=self.stop)
        self.btStop.grid(row=4, column=1, sticky="nsew")

        # add slider for x axis on 1 decimal point
        self.xSlider = tk.Scale(self.master, from_=450, to=-450, length=1000, orient=tk.HORIZONTAL,  
                                resolution=SLIDER_RESOLUTION, label="X axis (mm)", command=self.move_X, bg="#bfecff")
        self.xSlider.bind("<Button-1>", self.click_X)
        self.xSlider.grid(row=8, column=0, columnspan=10)

        # add slider for y axis on 1 decimal point
        self.ySlider = tk.Scale(self.master, from_=450, to=-450, length=1000, orient=tk.HORIZONTAL,
                                resolution=SLIDER_RESOLUTION, label="Y axis (mm)", command=self.move_Y, bg="#bfecff")
        self.ySlider.grid(row=9, column=0, columnspan=10)

        # add slider for z axis on 1 decimal point
        self.zSlider = tk.Scale(self.master, from_=200, to=-100, length=200, orient=tk.VERTICAL,
                                resolution=0.1, label="Z (mm)", command=self.move_Z, bg="#bfecff")
        self.zSlider.bind("<Button-1>", self.click_Z)
        self.zSlider.grid(row=0, column=9, rowspan=7, columnspan=2)
        
        # make button for 1. calibration point on right side
        self.btPoint1 = tk.Button(self.master, text="Point 1", bg="#43b0f1", command=self.store_point_1)
        self.btPoint1.grid(row=2, column=8, sticky="E")

        # add button for 2. calibration point on right side
        self.btPoint2 = tk.Button(self.master, text="Point 2", background="#43b0f1", command=self.store_point_2)
        self.btPoint2.grid(row=3, column=8, sticky="E")

        # add button for 3. calibration point on right side
        self.btPoint3 = tk.Button(self.master, text="Point 3", background="#43b0f1", command=self.store_point_3)
        self.btPoint3.grid(row=4, column=8, sticky="E")

        # add terminal for user to see what is happening
        self.terminal = tk.Text(self.master, height=10, width=55, bg="#bfecff", font=("Helvetica", 13))
        self.terminal.grid(row=0, column=2, columnspan=7, rowspan=5, sticky="nsw")
    
        # check if there is pickle file with points and read it
        if os.path.isfile(self.pointPklPath):
        # read points pickle file
            with open(self.pointPklPath, 'rb') as f:
                self.readPoints = pickle.load(f)
                for point in self.readPoints:
                    if point != None:
                        self.print_terminal("Point "+str(self.readPoints.index(point)+1)+": "+str(point)+"\n")
                        self.points[self.readPoints.index(point)] = point
                        if self.readPoints.index(point) == 0:
                            self.btPoint1.config(bg="#e2ac4d")
                        elif self.readPoints.index(point) == 1:
                            self.btPoint2.config(bg="#e2ac4d")
                        elif self.readPoints.index(point) == 2:
                            self.btPoint3.config(bg="#e2ac4d")
                    else:
                        self.print_terminal("Point "+str(self.readPoints.index(point)+1)+": None\n")
        else:
            self.print_terminal("No pickle file with points\n")

        if self.robot == None:
            self.print_terminal("No robot connected\n")
        else:
            self.print_terminal("Robot connected\n")
            self.refresh_slider()


    def stop(self):
        # stop robot
        self.print_terminal("Stop,  NEED TO FINISH IT\n")

        self.master.attributes("-disabled", True)
        self.master.after(0, self.master.destroy)

    def start(self):
        if self.robot == None:
            pass
        else:
            self.robot.home()

        self.refresh_slider()
        # print start coordinates
        self.print_terminal("Start coordinates: X: "+str(self.START_X)+" Y: "+str(self.START_Y)+" Z: "+str(self.START_Z)+"\n")
        # set slider to start coordinates
        self.xSlider.set(self.START_X)
        self.ySlider.set(self.START_Y)
        self.zSlider.set(self.START_Z)
        # move robot to start coordinates in z axis
        pass

    def home(self):
        self.print_terminal("Move robot to home position\n")
        if self.robot == None:
            return
        else:
            self.robot.home()
        self.refresh_slider()
        time.sleep(1)

        self.robot.setWorldOffset([0, 0, 0, 0, 0, 0])

        self.refresh_slider()

    def check_points(self):
        self.print_terminal("Check\n")
        self.checkThread = threading.Thread(target=self.checkPoints)
        self.checkThread.start()

    def checkPoints(self):
        self.btCheckPoints.config(relief=tk.SUNKEN)
        if self.robot == None:
            time.sleep(2)
            self.print_terminal("No robot connected\n")
        else:
            # Check teach points
            self.robot.move(x = self.points[0][0], y = self.points[0][1], 
                            z = self.points[0][2], speed=self.robotSpeed, mvacc=self.mvacc, wait=True)
            time.sleep(1)
            self.robot.move(x = self.points[1][0], y = self.points[1][1], 
                            z = self.points[1][2], speed=self.robotSpeed, mvacc=self.mvacc, wait=True)
            time.sleep(1)
            self.robot.move(x = self.points[2][0], y = self.points[2][1], 
                            z = self.points[2][2], speed=self.robotSpeed, mvacc=self.mvacc, wait=True)
            time.sleep(1)
        self.btCheckPoints.config(relief=tk.RAISED)

    def coord(self):
        if self.COORD_SYSTEM == 0:
            self.print_terminal("Base coord\n")
            self.btCoord.config(text="Base coord", bg="#43b0f1")
            if self.robot != None:
                self.xSlider.set(self.robot.getPosition()[0])
                self.ySlider.set(self.robot.getPosition()[1])
                self.zSlider.set(self.robot.getPosition()[2])
            
            self.COORD_SYSTEM = 1

        elif self.COORD_SYSTEM == 1:
            self.print_terminal("User coord\n")
            self.btCoord.config(text="User coord", bg="light green")
            if self.robot != None:
                self.xSlider.set(self.robot.getPosition()[3])
                self.ySlider.set(self.robot.getPosition()[4])
                self.zSlider.set(self.robot.getPosition()[5])

            self.COORD_SYSTEM = 0

        elif self.COORD_SYSTEM == -1:
            self.print_terminal("Finish with origin calibration\n")   

    def set_rotation(self):
        if self.robot == None:
            self.coordOffset[3:] = self.robot.calibrateUserOrientationOffset()
            self.print_terminal("Rotation offset roll: "+str(self.coordOffset[3])+" pitch: "+str(self.coordOffset[4])+" yaw: "+str(self.coordOffset[5])+"\n")
            self.robot.setWorldOffset(self.coordOffset)
            self.btCoord.config(text="Rotation offset", bg="red")
            self.USER_COORD = -1
            self.refresh_slider()
            self.print_terminal("Rotation offset set\n")
        else:
            self.print_terminal("Robot not connected\n")

    def set_origin(self):
        if self.robot != None:
            self.coordOffset[:3] = self.robot.getPosition()[:3]    
            self.print_terminal("Robot coordinates: X: "+str(self.coordOffset[0])+
                                " Y: "+str(self.coordOffset[1])+" Z: "+str(self.coordOffset[2])+"\n")
            self.robot.setWorldOffset([-self.coordOffset[0], -self.coordOffset[1], -self.coordOffset[2], 
                                        self.coordOffset[3], self.coordOffset[4], self.coordOffset[5]])
            self.refresh_slider()

            self.btCoord.config(text="Origin coord", bg="light green")
            self.print_terminal("Origin offset set\n")
            self.USER_COORD = 0
        else:
            self.print_terminal("Robot not connected\n")
        

    def check_origin(self):
        # make thread for checking origin
        self.checkOriginThread = threading.Thread(target=self.checkOrigin)
        self.checkOriginThread.start()
    
    def checkOrigin(self):
        # set button check origin to sunken
        self.btCheckOrigin.config(relief=tk.SUNKEN)
        if self.robot != None:
            # move robot in x direction
            self.x = 0
            self.y = 0
            self.z = -2
            self.robot.move(x = 0, y = 0, z = -5, speed=self.robotSpeed, wait=True)
            for i in range(0, 6):
                self.robot.move(x = (self.x+(i*CALIBRATION_SQUARE_SIZE*1000)), y = self.y, z = self.z, speed=self.robotSpeed, wait=True)
                # Wait for robot to move
                time.sleep(0.5)

            self.robot.move(x = 0, y = 0, speed=self.robotSpeed, wait=True)
            time.sleep(0.5)

            for i in range(1, 6):
                self.robot.move(x = self.x, y = (i*CALIBRATION_SQUARE_SIZE*1000), z = self.z, speed=100, wait=True)
                time.sleep(0.5)

            self.robot.move(x = 0, y = 0, speed=100, wait=True)
            self.robot.move(x = (6*CALIBRATION_SQUARE_SIZE*1000), y = (6*CALIBRATION_SQUARE_SIZE*1000), z = self.z, speed=100, wait=True)
            time.sleep(5)

            self.robot.move(x = 0, y = 0, speed=100, wait=True)
            time.sleep(1)
            self.refresh_slider()
            self.print_terminal("Origin coordinates checked\n")
        else:
            self.print_terminal("Robot not connected\n")

        # set button check origin to raised
        self.print_terminal("Check origin\n")
        self.btCheckOrigin.config(relief=tk.RAISED)

    def done(self):
        # store points to pickle file
        # check if all points are stored
        if len(self.points) == 3:
            with open(self.pointPklPath, 'wb') as f:
                pickle.dump(self.points, f)
            self.print_terminal("Points stored\n")
        else:
            self.print_terminal("Not all points are set\n")
        
        # store rotation and origin offset to pickle file
        if len(self.coordOffset) == 6:
            with open(self.coordOffPklPath, 'wb') as f:
                pickle.dump(self.coordOffset, f)
            self.print_terminal("Rotation and origin offset stored\n")
        else:
            self.print_terminal("Rotation and origin offset not set\n")

        # disabel master window from clicking
        self.master.attributes("-disabled", True)

        #Automatically close the window after 3 seconds
        self.master.after(3000, self.master.destroy)

    def move_X(self, value):
        if self._job:
            self.master.after_cancel(self._job)
        self._job = self.master.after(200, self.moveX)

    def moveX(self):
        self._job = None
        if self.robot == None:
            self.print_terminal("Cant move robot, no robot connected\n")
            return
        else:
            self.robot.move(x = self.xSlider.get(), y = self.ySlider.get(), z = self.zSlider.get(), speed=50, mvacc=self.mvacc, wait=True)
        print("move X: "+str(self.xSlider.get()))

    def click_X(self, event):
        print("click X")

    def move_Y(self, value):
        if self._job:
            self.master.after_cancel(self._job)
        self._job = self.master.after(200, self.moveY)

    def moveY(self):
        self._job = None
        if self.robot == None:
            self.print_terminal("Cant move robot, no robot connected\n")
            return
        else:
            self.robot.move(x = self.xSlider.get(), y = self.ySlider.get(), z = self.zSlider.get(), speed=50, mvacc=self.mvacc, wait=True)
        print("move Y: "+str(self.ySlider.get()))

    def move_Z(self, value):
        if self._job:
            self.master.after_cancel(self._job)
        self._job = self.master.after(200, self.moveZ)
    
    def moveZ(self):
        self._job = None
        if self.robot == None:
            self.print_terminal("Cant move robot, no robot connected\n")
            return
        else:
            self.robot.move(x = self.xSlider.get(), y = self.ySlider.get(), z = self.zSlider.get(), speed=50, mvacc=self.mvacc, wait=True)
        print("move Z: "+str(self.zSlider.get()))

    def click_Z(self, event):
        print("click Z")

    def store_point_1(self):
        self.storePoint(1)
        self.btPoint1.config(bg="light green")

    def store_point_2(self):
        self.storePoint(2)
        self.btPoint2.config(bg="light green")

    def store_point_3(self):
        self.storePoint(3)
        self.btPoint3.config(bg="light green")
    
    def storePoint(self, point):
        # overwrite list of coordinate to points on frst place
        if self.robot == None:
            self.print_terminal("Cant get robot position, no robot connected\n")
            return
        else:
            self.points[point-1] = self.robot.getPosition()
            self.print_terminal("Point "+str(point)+" stored: "+str(self.points[point-1])+"\n")

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
        if self.COORD_SYSTEM == 0:
            if event.keysym == "Up":
                self.zSlider.set(self.zSlider.get() + 0.1)
            elif event.keysym == "Down":
                self.zSlider.set(self.zSlider.get() - 0.1)
        elif self.COORD_SYSTEM == 1:
            if event.keysym == "Up":
                self.zSlider.set(self.zSlider.get() - 0.1)
            elif event.keysym == "Down":
                self.zSlider.set(self.zSlider.get() + 0.1)

    def click_X(self, event):
        self.CLICK_XZ = 0 # 0 = button for x

    def click_Z(self, event):
        self.CLICK_XZ = 1 # 1 = button for z
    
    def print_terminal(self, text):
        self.terminal.insert(tk.END, text)
        self.terminal.see(tk.END)

    def refresh_slider(self):
        if self.robot == None:
            self.print_terminal("REFRESHSLIDER: Cant get robot position, no robot connected\n")
        else:
            self.robotPosition = self.robot.getPosition()
            self.xSlider.set(self.robotPosition[0])
            self.ySlider.set(self.robotPosition[1])
            self.zSlider.set(self.robotPosition[2])
            print(self.robotPosition)  
# ---------------------------- MAIN --------------------------------------------
# make main for testing gui
def main():
    logger = logging.getLogger()
    robot = vr.Robot(ROBOT_IP, logger)
    app = App(tk.Tk(), robot=robot)
    app.master.mainloop()
    
def appTest():
    app = App(tk.Tk())
    app.master.mainloop()

if __name__ == "__main__":
    #main()
    appTest()
