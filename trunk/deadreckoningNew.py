#from util import get_encoders
def get_encoders(reset):
    return [10000,9999]
import time
import threading
import math
DISTANCE_PER_COUNT = 0.491426637992914#MILLIMETERS
ROBOT_DIAMETER = 147#Measurement in millimeters
DEFAULT_DIGITS = 6
PRINT_COORDINATES = True
UPDATE_INTERVAL = 0.1#seconds
runThread = True

x_pos = 0.0#IN MILLIMETERS
y_pos = 0.0#IN MILLIMETERS
robotHeading = 0.0
moveHistory = []
previousTime = time.time()

#resets coordinates
def reset_deadReckoning():
    global x_pos, y_pos, robotHeading, moveHistory, previousTime
    x_pos = 0.0
    y_pos = 0.0
    robotHeading = 0.0
    moveHistory = []
    previousTime = time.time()
    get_encoders(True)

#initializes dead reckoning odometry thread
def i():#nitialize_deadReckoning
    global runThread
    reset_deadReckoning()
    runThread = True
    dRThread = threading.Thread(target=deadReckoningThread)
    dRThread.start()

#dead reckoning thread
def deadReckoningThread():
    global previousTime
    while runThread:
        update()
        previousTime = time.time()
        if(PRINT_COORDINATES):
            getCoords(DEFAULT_DIGITS)
        while time.time()<previousTime+UPDATE_INTERVAL:
            pass

#updates the position
def update():
    global x_pos, y_pos, robotHeading
    encoders = get_encoders(True)#gets number of encoder counts and reset it to 0
    distanceLeft = float(encoders[0])*DISTANCE_PER_COUNT#gets distance travelled by left wheel
    distanceRight = float(encoders[1])*DISTANCE_PER_COUNT#gets distance travelled by right wheel
    moveHistory.append([distanceLeft,distanceRight,time.time()-previousTime])
    cosCurrentAngle = math.cos(robotHeading)#cosine of current angle
    sinCurrentAngle = math.sin(robotHeading)#sine of current angle
    if(encoders[0]==encoders[1]):#if the distances are equal (robot is going straight)
        x_pos += distanceLeft * sinCurrentAngle#xPos global coordinate is updated
        y_pos += distanceLeft * cosCurrentAngle#yPos global coordinate is updated
    else:
        distRatio = ROBOT_DIAMETER * (distanceLeft + distanceRight) / 2.0 / (distanceRight - distanceLeft)#ratio modifier
        distDiff = distanceRight - distanceLeft#difference between distances travelled by left and right wheels
        x_pos += distRatio * (math.cos(distDiff/ROBOT_DIAMETER+robotHeading)-cosCurrentAngle)#updates global coordinate x
        y_pos += distRatio * (math.sin(distDiff/ROBOT_DIAMETER+robotHeading)-sinCurrentAngle)#updates global coordinate y
        robotHeading += distDiff/ROBOT_DIAMETER#updates current robot heading

def stopThread():
    global runThread
    runThread = False

#gets coordinates
def getCoords(numberOfDigits=DEFAULT_DIGITS):
    print "(" + str(round(x_pos*0.001,numberOfDigits)) + "," + str(round(y_pos*0.001,numberOfDigits)) + " at angle "+str(round(robotHeading,numberOfDigits))+")"

def getX():
    return x_pos

def getY():
    return y_pos

def getHeading():
    return robotHeading

def getMoveHistory(depth):#returns in reverse chronological order
    output = []
    for i in range(len(moveHistory)-1,len(moveHistory)-1-depth,-1):
        output.append(moveHistory[i])
    return output

'''
if __name__=='__main__':
    from util import *
    xp_initialize()
'''
