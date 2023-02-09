from xarm.wrapper import XArmAPI
from parameters import *
import tkinter as tk
import vodenjeRobota as vr
import logging

import time

timeout = 2
rspeed = 70

START_X = 400
START_Y = 0
START_Z = 3 # in mm negative value is up

# Make gui for user to set robot to base position
# Make window for user to set robot to base position with buttons and sliders in thread
# Make thread
class window:
    def __init__(self, master, robot):
        self.robot = robot
        self.master = master
        self.master.title("Robot calibration")
        self.master.geometry("1000x300")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Make 10x10 grid
        for i in range(10):
            self.master.columnconfigure(i, weight=1)
            self.master.rowconfigure(i, weight=1)

        self.master.bind("<Left>", self.on_key_press_x)
        self.master.bind("<Right>", self.on_key_press_x)
        self.master.bind("<Up>", self.on_key_press_y)
        self.master.bind("<Down>", self.on_key_press_y)

        self.label = tk.Label(self.master, text="Set robot default coordinate system to base", 
                              fg="RED", font=("Helvetica", 11), bg="#bfecff")
        self.label.grid(row=0, column=0, sticky="nsew")

        # add start button
        self.btStart = tk.Button(self.master, text="Start", bg="#e2ac4d", font=("Helvetice", 11), command=self.start)
        self.btStart.grid(row=1, column=0, sticky="nsew")

        # add set rotation button
        self.btSetRotation = tk.Button(self.master, text="Set rotation", bg="#e2ac4d", font=("Helvetic", 11), command=self.setRotation)
        self.btSetRotation.grid(row=2, column=0, sticky="nsew")

        # add set origin button
        self.btSetOrigin = tk.Button(self.master, text="Set origin", bg="#e2ac4d", font=("Helvetic", 11), command=self.setOrigin)
        self.btSetOrigin.grid(row=3, column=0, sticky="nsew")

        # add cancel button
        self.btCancel = tk.Button(self.master, text="Cancel", bg="#e2ac4d", font=("Helvetica", 11), command=self.cancel)
        self.btCancel.grid(row=4, column=0, sticky="nsew")

        # add slider for x axis on 1 decimal point
        self.xSlider = tk.Scale(self.master, from_=0, to=50, length=1000, orient=tk.HORIZONTAL,  
                                resolution=0.1, label="X axis (mm)", command=self.moveX, bg="#bfecff")
        self.xSlider.grid(row=8, column=0, columnspan=10)

        # add slider for y axis on 1 decimal point
        self.ySlider = tk.Scale(self.master, from_=0, to=50, length=1000, orient=tk.HORIZONTAL,
                                resolution=0.1, label="Y axis (mm)", command=self.moveY, bg="#bfecff")
        self.ySlider.grid(row=9, column=0, columnspan=10)
        
        # make button for 1. calibration point on right side
        self.point1 = tk.Button(self.master, text="Point 1", bg="#43b0f1", command=self.storePoint1)
        self.point1.grid(row=2, column=9)

        # add button for 2. calibration point on right side
        self.point2 = tk.Button(self.master, text="Point 2", background="#43b0f1", command=self.storePoint2)
        self.point2.grid(row=3, column=9)

        # add button for 3. calibration point on right side
        self.point3 = tk.Button(self.master, text="Point 3", background="#43b0f1", command=self.storePoint3)
        self.point3.grid(row=4, column=9)

        # add terminal for user to see what is happening
        self.terminal = tk.Text(self.master, height=10, width=10, bg="#bfecff", font=("Helvetica", 13))
        self.terminal.grid(row=0, column=2, columnspan=7, rowspan=5, sticky="nsew")

    def printTerminal(self, text):
        self.terminal.insert(tk.END, text)
        self.terminal.see(tk.END)

    def start(self):
        print("Start")
        self.printTerminal("Start robot calibration\n")
        pass

    def storePoint1(self):
        self.storePoint(1)

    def storePoint2(self):
        self.storePoint(2)

    def storePoint3(self):
        self.storePoint(3)
    
    def storePoint(self, point):
        print("Point stored "+str(point))
        pass

    def move(sef, value):
        print(value)
        pass

    # Check if last value is changed more than 2s ago

    def moveX(self, value):
        print(value)
        pass

    def moveY(self, value):
        print(value)
        pass

    def set(self):
        self.master.destroy()

    def setRotation(self):
        print("Set rotation")
        self.printTerminal("Set rotation\n")
        pass

    def setOrigin(self):
        print("Set origin")
        pass

    def cancel(self):
        self.master.destroy()

    def on_key_press_x(self, event):
        if event.keysym == "Left":
            self.xSlider.set(self.xSlider.get() - 0.1)
        elif event.keysym == "Right":
            self.xSlider.set(self.xSlider.get() + 0.1)

    def on_key_press_y(self, event):
        if event.keysym == "Up":
            self.ySlider.set(self.ySlider.get() + 0.1)
        elif event.keysym == "Down":
            self.ySlider.set(self.ySlider.get() - 0.1)

    def on_closing(self):
        self.master.destroy()

    class RoundButton(tk.Canvas):
        def __init__(self, parent, text, command, bg, fg, activebackground, font, width, height, **kwargs):
            tk.Canvas.__init__(self, parent, bg=bg, width=width, height=height, **kwargs)
            self.parent = parent
            self.text = text
            self.command = command
            self.bg = bg
            self.fg = fg
            self.activebackground = activebackground
            self.font = font
            self.width = width
            self.height = height
            self.bind("<1>", self.click)
            self._draw_button()

        def draw_button(self):
            x0 = self.width / 2
            y0 = self.height / 2
            r = min(self.width, self.height) / 2 - 5
            self.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, fill=self.bg, width=0)
            self.create_text(x0, y0, text=self.text, font=self.font, fill=self.fg)

        def click(self, event):
            self.config(bg=self.activebackground)
            self.command()
        


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
    #logger = logging.getLogger()
    #robot = vr.Robot(ROBOT_IP, logger)
    calibWindow = window(tk.Tk(), robot=None)
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
        