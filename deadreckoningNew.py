from util import *
import time
import threading
import math
DISTANCE_PER_COUNT = 0.000491426637992914#METERS
ROBOT_DIAMETER = 0.142#Measurement in meters
DEFAULT_DIGITS = 6
PRINT_COORDINATES = False
UPDATE_INTERVAL = 0.1#seconds
runThread = True

x_pos = 0.0#IN METERS
y_pos = 0.0#IN METERS
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
    get_encoders(False)

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
    encoders = get_encoders(False)#gets number of encoder counts and reset it to 0
    distanceLeft = float(encoders[0])*DISTANCE_PER_COUNT/2.0#gets distance travelled by left wheel
    distanceRight = float(encoders[1])*DISTANCE_PER_COUNT/2.0#gets distance travelled by right wheel
    moveHistory.append([distanceLeft,distanceRight,time.time()-previousTime])
    #istate['wheel_speed']=distanceLeft/(time.time()-previousTime),distanceRight/(time.time()-previousTime)
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
    print "(" + str(round(x_pos,numberOfDigits)) + "," + str(round(y_pos,numberOfDigits)) + " at angle "+str(round(robotHeading,numberOfDigits))+")"

def getX():
    return x_pos

def getY():
    return y_pos

def getHeading():
    return robotHeading

def getMoveHistory(depth=None):#returns in reverse chronological order
    '''returns list of (left_arclength,right_arclength)'''
    output = []
    if depth is None:
        end=0
    else:
        end=len(moveHistory)-depth
    for i in range(len(moveHistory)-1,end-1,-1):
        output.append(moveHistory[i])
    return output


if __name__=='__main__':
    xp_initialize()
    
