from math import *
#import myro
from time import sleep
#Constants
SPEED_CONSTANT = 0.147#Measured
ROBOT_DIAMETER = 0.15#Measured
DEBUGMODE = True
PRINT_COORDS = True
CALCULATE_OFFSET = False #Only should work in theory if offset is linearly proportionate to angle turned
PRINTING_DIGITS = 4
if(DEBUGMODE):
    ROBOT_DIAMETER = 2#Assumes radius 1 in debugmode
ROBOT_RADIUS = ROBOT_DIAMETER>>1
EPSILON = 0.0001
#Variables
x_pos = 0
y_pos = 0
robotHeading = 0

#Robot headings are rotated clockwise = positive, counterclockwise = negative
def deadReckoning(leftMotorConstant,rightMotorConstant,deltaTime):
    leftMotorSpeed = leftMotorConstant*SPEED_CONSTANT
    rightMotorSpeed = rightMotorConstant*SPEED_CONSTANT
    if(fabs(leftMotorSpeed-rightMotorSpeed)<EPSILON):
        deltaX = leftMotorSpeed*deltaTime*sin(robotHeading)
        deltaY = leftMotorSpeed*deltaTime*cos(robotHeading)
        return [0,deltaX,-deltaY]
    else:
        deltaRobotHeading = (leftMotorSpeed-rightMotorSpeed)*deltaTime/ROBOT_DIAMETER
        distRatio = ROBOT_RADIUS*(rightMotorSpeed+leftMotorSpeed)/(rightMotorSpeed-leftMotorSpeed)
        deltaX = (cos(robotHeading+deltaRobotHeading)-cos(robotHeading))*distRatio
        deltaY = (sin(robotHeading+deltaRobotHeading)-sin(robotHeading))*distRatio
    return [deltaRobotHeading,deltaX,deltaY]

#change in deltaY per radian if linearly proportionate:
#offsetYRatioFromRotation = ldexp(fdiv(mpf("0.085"),pi),-5)#(2^-5)/pi=1/(32pi)=1/(16(2pi))


OFFSET_Y_RATIO = 0.085/(32*pi) #ratio of y offset in m per change in deltaHeading Radians
OFFSET_X_RATIO = 0.045/(32*pi) #very unprecise calculation
#perhaps implement code:
#y_pos = fadd(y_pos,fmul(deltaRobotHeading,offsetYRatioFromRotation))
#x_pos = ...same (find offset ratio)
#after 16 full rotations clockwise, y increases by 8.5 cm +/- 1 cm
#after 16 full rotations counterclockwise, y increases by 8.5 cm +/- 1 cm
#after 16 full rotations clockwise, x increases by <UNMEASURED> > 0
#after 16 full rotations counterclockwise, x increases by <UNMEASURED> > 0
#check if linearly proportionate
def update(leftMotorConstant,rightMotorConstant,deltaTime,isSpeed=False):
    global x_pos, y_pos, robotHeading
    if(isSpeed):
        leftMotorConstant = leftMotorConstant/SPEED_CONSTANT
        rightMotorConstant = rightMotorConstant/SPEED_CONSTANT
    #if over max speed, scales constants so that they are below or equal to 1, and increases time proportionally
    if(leftMotorConstant>1 or rightMotorConstant>1):
        scaler = max(leftMotorConstant,rightMotorConstant)
        leftMotorConstant = leftMotorConstant/scaler
        rightMotorConstant = rightMotorConstant/scaler
        deltaTime = scaler*deltaTime
    if(leftMotorConstant<-1 or rightMotorConstant<-1):
        scaler = abs(min(leftMotorConstant,rightMotorConstant))
        leftMotorConstant = leftMotorConstant/scaler
        rightMotorConstant = rightMotorConstant/scaler
        deltaTime = scaler*deltaTime
    #moves the scribbler if not in debug mode
    if(DEBUGMODE==False):
        myro.motors(leftMotorConstant,rightMotorConstant)
        sleep(deltaTime)
        myro.stop()
    #dead reckoning position calculations
    dR = deadReckoning(leftMotorConstant,rightMotorConstant,deltaTime)
    if(CALCULATE_OFFSET):
        y_pos += fabs(dR[0])*OFFSET_Y_RATIO
        x_pos += fabs(dR[0])*OFFSET_X_RATIO
    robotHeading = (robotHeading+dR[0]+pi)%(2*pi)-pi
    x_pos = x_pos+dR[1]
    y_pos = y_pos-dR[2]
    if(PRINT_COORDS):
        getCoords(PRINTING_DIGITS)

#Completely scrapped due to errors
'''
#Fast but just approximation, not accurate (very bad at handling circular arcs), uses different dead reckoning algorithm
#Don't use unless using without turning much or in very small intervals
def updateFast(leftMotorConstant,rightMotorConstant,deltaTime,isSpeed=False):
    global x_pos, y_pos, robotHeading
    if(isSpeed):
        leftMotorDistance = fmul(leftMotorConstant,deltaTime)
        rightMotorDistance = fmul(rightMotorConstant,deltaTime)
    else:
        leftMotorDistance = fmul(fmul(leftMotorConstant,SPEED_CONSTANT),deltaTime)
        rightMotorDistance = fmul(fmul(rightMotorConstant,SPEED_CONSTANT),deltaTime)
    averageDistance = ldexp(fadd(leftMotorDistance,rightMotorDistance),-1)
    robotHeading = fadd(robotHeading,fdiv(fsub(leftMotorDistance,rightMotorDistance),ldexp(ROBOT_DIAMETER,1)))
    x_pos = fadd(x_pos,fmul(averageDistance,sin(robotHeading)))
    y_pos = fadd(y_pos,fmul(averageDistance,cos(robotHeading)))
    if(PRINT_COORDS):
        getCoords(PRINTING_DIGITS)
'''
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
