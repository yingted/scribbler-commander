from util import get_encoders
import threading
DISTANCEPER_COUNT = 0.491#MILLIMETERS
ROBOT_DIAMETER = 0.15#Measurement
DEFAULT_DIGITS = 6
PRINT_COORDINATES = True
UPDATE_INTERVAL = 0.1#seconds

x_pos = 0#IN MILLIMETERS
y_pos = 0#IN MILLIMETERS
robotHeading = 0

#resets coordinates
def reset_deadReckoning():
    global x_pos, y_pos, robotHeading
    x_pos = 0
    y_pos = 0
    robotHeading = 0
    get_encoders(True)

#initializes dead reckoning odometry thread
def initialize_deadReckoning():
    reset_deadReckoning()
    dRThread = threading.Thread(target=deadReckoningThread)
    dRThread.start()

#dead reckoning thread
def deadReckoningThread():
    while True:
        time.sleep(UPDATE_INTERVAL)
        update()
        if(PRINT_COORDINATES):
            getCoords(DEFAULT_DIGITS)

#updates the position
def update():
    global x_pos, y_pos, robotHeading
    encoders = get_encoders(True)#gets number of encoder counts and reset it to 0
    distanceLeft = encoders[0]*DISTANCE_PER_COUNT#gets distance travelled by left wheel
    distanceRight = encoders[1]*DISTANCE_PER_COUNT#gets distance travelled by right wheel
    cosCurrentAngle = cos(robotHeading)#cosine of current angle
    sinCurrentAngle = sin(robotHeading)#sine of current angle
    if(encoders[0]==encoders[1]):#if the distances are equal (robot is going straight)
        x_pos += distanceLeft * cosCurrentAngle#xPos global coordinate is updated
        y_pos += distanceLeft * sinCurrentAngle#yPos global coordinate is updated
    else:
        distRatio = ROBOT_DIAMETER * (distanceLeft + distanceRight) / 2.0 / (distanceRight - distanceLeft)#ratio modifier
        distDiff = distanceRight - distanceLeft#difference between distances travelled by left and right wheels
        x_pos += distRatio * (sin(distDiff/ROBOT_DIAMETER+robotHeading)-sinCurrentAngle)#updates global coordinate x
        y_pos -= distRatio * (cos(distDiff/ROBOT_DIAMETER+robotHeading)-cosCurrentAngle)#updates global coordinate y
        robotHeading = (robotHeading + distDiff/ROBOT_DIAMETER + pi)%(2*pi)-pi#updates current robot heading

#gets coordinates
def getCoords(numberOfDigits=DEFAULT_DIGITS):
    print "(" + str(round(x_pos*0.001,numberOfDigits)) + "," + str(round(y_pos*0.001,numberOfDigits)) + " at angle "+str(round(robotHeading,numberOfDigits))+")"

def getX():
    return x_pos

def getY():
    return y_pos

def getHeading():
    return robotHeading

if __name__=='__main__':
    from util import *
    xp_initialize()
    
