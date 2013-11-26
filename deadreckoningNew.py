from util.py import *
import threading
DISTANCE_PER_COUNT = 0.491
ROBOT_DIAMETER = 0.15#Measurement
DEFAULT_DIGITS = 6
PRINT_COORDINATES = True

x_pos#IN MILLIMETERS
y_pos#IN MILLIMETERS
robotHeading

def reset_deadReckoning():
    global x_pos, y_pos, robotHeading
    x_pos = 0
    y_pos = 0
    robotHeading = 0
    get_encoders(True)
    
def initialize_deadReckoning():
    reset_deadReckoning()
    dRThread = threading.Thread(target=deadReckoningThread)
    dRThread.start()

def deadReckoningThread():
    while True:
        time.sleep(0.1)
        update()
        if(PRINT_COORDINATES):
            getCoords()

def update():
    global x_pos, y_pos, robotHeading
    encoders = get_encoders(True)
    distanceLeft = encoders[0]*DISTANCE_PER_COUNT
    distanceRight = encoders[1]*DISTANCE_PER_COUNT
    cosCurrentAngle = cos(robotHeading)
    sinCurrentAngle = sin(robotHeading)
    if(encoders[0]==encoders[1]):
        x_pos += distanceLeft * cosCurrentAngle
        y_pos += distanceLeft * sinCurrentAngle
    else:
        distRatio = ROBOT_DIAMETER * (distanceLeft + distanceRight)
        distDiff = distanceRight - distanceLeft
        x_pos += distRatio * (sin(distDiff/ROBOT_DIAMETER+robotHeading)-sinCurrentAngle)
        y_pos -= distRatio * (cos(distDiff/ROBOT_DIAMETER+robotHeading)-cosCurrentAngle)
        robotHeading = (robotHeading + distDiff/ROBOT_DIAMETER + pi)%(2*pi)-pi

def getCoords(numberOfDigits=DEFAULT_DIGITS):
    print "(" + str(round(x_pos*0.001,numberOfDigits)) + "," + str(round(y_pos*0.001,numberOfDigits)) + " at angle "+str(round(robotHeading,numberOfDigits))+")"

def getX():
    return x_pos

def getY():
    return y_pos

def getHeading():
    return robotHeading
