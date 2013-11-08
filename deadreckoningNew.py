'''
from myro.robots.scribbler import Scribbler
from time import time
_oldSet = Scribbler._set
_left = 100
_right = 100
_time = time()
def _update():
    global _left, _right, _time
    otime = _time
    _time = time()
    def f(x):
            return cmp(x, 100) * abs((x - 100) / 100)**0.67016601562499989
    update(f(_left), f(_right), _time - otime)
    #print 'getCoords', getCoords(PRINTING_DIGITS)
def _newSet(self, *values):
    global _left, _right
    _update()
    if values==(Scribbler.SET_MOTORS_OFF,):
        _left = _right = 100
    elif len(values)==3 and values[0]==Scribbler.SET_MOTORS:
        _left, _right = values[1:]
    _oldSet(self, *values)
Scribbler._set = _newSet
'''
 
from math import *
from myro import *
from time import time
#Constants
Y_OFFSET_PER_RADIAN = 0.078/12/pi#7.8 cm per 6 revolutions
X_OFFSET_PER_RADIAN = -0.01/12/pi#1 cm per 6 revolutions
SPEED_CONSTANT = 0.127/0.8#Measured
HEADING_CONSTANT = pi*12/23.075#Measured
DEBUGMODE = False
PRINT_COORDS = True
CALCULATE_OFFSET = True #Only should work in theory if offset is linearly proportionate to angle turned
PRINTING_DIGITS = 4

def a():
    initialize("/dev/tty.Scribbler")

EPSILON = 0.0001
#Variables
x_pos = 0
y_pos = 0
robotHeading = 0
positions = []
 
timeSpent = 0.0
def moveMotor(x,y,t):
    global timeSpent
    timeSpent += t
    if(DEBUGMODE):
        update(x,y,t)
    else:
        motors(x,y)
        beginTime = time()
        update(x,y,t)
        while (time()<(beginTime+t)):
            pass
        stop()
 
def forward(t):
    moveMotor(0.8,0.8,t)
 
def turnRight(t):
    moveMotor(0.1,-0.1,t)
 
def turnLeft(t):
    moveMotor(-0.1,0.1,t)
 
def distTo(target_x,target_y):
    distance = ((x_pos-target_x)**2+(y_pos-target_y)**2)**0.5
    if(fabs(x_pos-target_x)<EPSILON):
        targetHeading = pi/2
        if((y_pos-target_y)>(-1*EPSILON)):
            targetHeading = 3*pi/2
    else:
        targetHeading = atan((y_pos*1.0-target_y)/(x_pos-target_x))
    if((x_pos-target_x)>EPSILON):
        targetHeading -= pi
    deltaHeading = pi/2-robotHeading-targetHeading
    deltaHeading = (deltaHeading+pi)%(2*pi)-pi
    return [distance,deltaHeading]
 
#Robot headings are rotated clockwise = positive, counterclockwise = negative
def deadReckoning(leftMotorSpeed,rightMotorSpeed,deltaTime):
    if(fabs(leftMotorSpeed-rightMotorSpeed)<EPSILON):
        deltaX = leftMotorSpeed*deltaTime*sin(robotHeading)*SPEED_CONSTANT
        deltaY = leftMotorSpeed*deltaTime*cos(robotHeading)*SPEED_CONSTANT
        return [0,deltaX,-deltaY]
    else:
        deltaRobotHeading = (leftMotorSpeed-rightMotorSpeed)*deltaTime*HEADING_CONSTANT
        return [deltaRobotHeading, 0, 0]
 
#change in deltaY per radian if linearly proportionate:
def update(leftMotorConstant,rightMotorConstant,deltaTime):
    global x_pos, y_pos, robotHeading
    dR = deadReckoning(leftMotorConstant,rightMotorConstant,deltaTime)
    if(CALCULATE_OFFSET):
        y_pos += abs(dR[0])*Y_OFFSET_PER_RADIAN
        x_pos += abs(dR[0])*X_OFFSET_PER_RADIAN
    robotHeading = (robotHeading+dR[0]+pi)%(2*pi)-pi
    x_pos = x_pos+dR[1]
    y_pos = y_pos-dR[2]
    currentPos = [x_pos,y_pos,robotHeading]
    if(PRINT_COORDS):
        getCoords(PRINTING_DIGITS)
 
def testForward(deltaTime):
    myro.motors(1,1)
    sleep(deltaTime)
    myro.stop()
 
def reset():
    global x_pos, y_pos, robotHeading
    x_pos = 0
    y_pos = 0
    robotHeading = 0
       
def getCoords(numberOfDigits):
    print "(" + str(round(x_pos,numberOfDigits)) + "," + str(round(y_pos,numberOfDigits)) + " at angle "+str(round(robotHeading,numberOfDigits))+")"
 
def test():
    update(2,0,pi*ROBOT_RADIUS,-True)#goes in a semicircle towards the right with radius equal to the robot's
    update(1,-1,pi/2*ROBOT_RADIUS,True)#turns 90 degrees clockwise
    update(1,1,2*ROBOT_RADIUS,True)#forward by a distance equal to twice the robot radius
    update(1,1,2*ROBOT_RADIUS,True)#forward by a distance equal to twice the robot radius
    update(1,-1,pi/2*ROBOT_RADIUS,True)#turns 90 degrees clockwise
    update(1,0,pi*ROBOT_RADIUS*2,True)#goes in a semicircle towards the right with radius equal to the robot's at half the speed but twice the time
    update(-1,1,pi*ROBOT_RADIUS,True)#turns 180 degrees counterclockwise
    update(0,1,4*pi*ROBOT_RADIUS,True)#goes in a full circle towards the left with radius equal to the robot's
    update(1,1,5,True)#goes forward by 5m
    update(1,-1,pi/2*ROBOT_RADIUS,True)#turns 90 degrees clockwise
    update(1,1,12,True)#goes forward by 12m
    update(1,-1,pi/2*ROBOT_RADIUS,True)#turns 90 degrees clockwise
    update(1,-1,(pi/2-acos(12.0/13.0))*ROBOT_RADIUS,True)#turns by pi/2 minus the angle between the 12 and 13 side in a 5-12-13 triangle
    update(1,1,13,True)#goes forward by 13m
    update(1,-1,acos(12.0/13.0)*ROBOT_RADIUS,True)#turns by the angle between the 12 and 13 side in a 5-12-13 triangle
    update(0.5,-0.5,pi*ROBOT_RADIUS,True)#turns by pi/2
    for i in range(0,16):
        update(2,1,pi*ROBOT_RADIUS/4,True)#approximate circle function
