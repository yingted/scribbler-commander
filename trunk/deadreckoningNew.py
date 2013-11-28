from util import *
import time
import threading
import math
DISTANCE_PER_COUNT = 0.511#0.511864406#0.51090604#0.491493382#Millimeters
COUNTS_PER_METER = 1000.0/DISTANCE_PER_COUNT
ROBOT_DIAMETER = 142.5#Measurement in millimeters
DEFAULT_DIGITS = 6
PRINT_COORDINATES = False
UPDATE_INTERVAL = 0.1#Seconds
SPEED_CHANGE_SENSITIVITY = 2#in number of update intervals, lower = more sensitive
runThread = True
individualTest = False
motorValues = [[0.0,0]]
for i in range(19,107,8):
    motorValues.append([float(i)/-100.0,-1.0*((i-19.0)/8.0*48.0+103.0)])
    motorValues.append([float(i)/100.0,(i-19.0)/8.0*48.0+103.0])
multiplierValues = []
for value in motorValues:
    multiplierValues.append([value[0],float(value[1])/float(motorValues[len(motorValues)-1][1])])
    #print value[0]
    #print float(value[1])/float(motorValues[len(motorValues)-1][1])
x_pos = 0.0#In millimeters
y_pos = 0.0#In millimeters
robotHeading = 0.0
moveHistory = []
beginTime = time.time()
previousTime = time.time()
lastMove = 0#number of update intervals ago

def getClosestMotorMultiplierValues(multiplierValue):
    diff = math.fabs(multiplierValues[0][1]-multiplierValue)
    position = 0
    for i in range(1,len(multiplierValues)):
        if math.fabs(multiplierValues[i][1]-multiplierValue)<diff:
            diff = math.fabs(multiplierValues[i][1]-multiplierValue)
            position = i
    return multiplierValues[position]
        

#resets coordinates
def reset_deadReckoning():
    global x_pos, y_pos, robotHeading, moveHistory, beginTime, previousTime
    x_pos = 0.0
    y_pos = 0.0
    robotHeading = 0.0
    moveHistory = []
    beginTime = time.time()
    previousTime = time.time()
    get_encoders(False)

#initializes dead reckoning odometry thread
def initialize_deadReckoning():
    '''initializes dead reckoning odometry thread'''    
    global runThread
    reset_deadReckoning()
    update()
    runThread = True
    dRThread = threading.Thread(target=deadReckoningThread)
    dRThread.start()

#dead reckoning thread
def deadReckoningThread():
    '''dead reckoning odometry thread'''
    global previousTime, lastMove
    while runThread:
        update()
        #lastMove += 1
        #if(len(moveHistory)>SPEED_CHANGE_SENSITIVITY and not withinError(getAverageSpeedSinceLastChange(SPEED_CHANGE_SENSITIVITY),getRecentAverageSpeed(SPEED_CHANGE_SENSITIVITY))):
            #lastMove = 0
        previousTime = time.time()
        if(PRINT_COORDINATES):
            getCoords(DEFAULT_DIGITS)
        time.sleep(max(0.0,UPDATE_INTERVAL-time.time()+previousTime))

#updates the position
def update():
    global x_pos, y_pos, robotHeading
    encoders = get_encoders(False)#gets number of encoder counts and reset it to 0
    distanceLeft = float(encoders[0])*DISTANCE_PER_COUNT/2.0#gets distance travelled by left wheel
    distanceRight = float(encoders[1])*DISTANCE_PER_COUNT/2.0#gets distance travelled by right wheel
    delta_t=time.time()-previousTime
    moveHistory.append([distanceLeft*0.001,distanceRight*0.001,delta_t])
    if(not individualTest):
        state['trail']=distanceLeft*0.001,distanceRight*0.001
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
    while robotHeading > math.pi:
        robotHeading -= 2.0*math.pi
    while robotHeading < -math.pi:
        robotHeading += 2.0*math.pi
    if(not individualTest):
        state['where']=getX(),getY(),getHeading()

def stopThread():
    global runThread
    runThread = False

#gets coordinates
def getCoords(numberOfDigits=DEFAULT_DIGITS):
    print "(" + str(round(getX(),numberOfDigits)) + "," + str(round(getY(),numberOfDigits)) + " at angle "+str(round(getHeading(),numberOfDigits))+")"

def withinError(a,b,maxRelativeError):
    if((b-a)/a<maxRelativeError):
        return True
    else:
        return False

def getX():
    return x_pos*0.001

def getY():
    return y_pos*0.001

def getHeading():
    return (float(robotHeading)+3.0*math.pi/2.0)%(2.0*math.pi)-math.pi

def getSpeed(move):
    return (move[0]+move[1])/2.0/move[2]

def convMoveListToSpeed(moveList):
    speedList = []
    for move in moveList:
        speedList.append(getSpeed(move))
    return speedList

def getAverageSpeedSinceLastChange(begin):
    speedList = convMoveListToSpeed(getMoveHistory(begin,lastMove))
    sumSpeed = 0.0
    for speed in speedList:
        sumSpeed += speed
    sumSpeed /= float(len(speedList))
    return sumSpeed

def getRecentAverageSpeed(numberOfMoves):
    speedList = convMoveListToSpeed(getMoveHistory(0,numberOfMoves+1))
    sumSpeed = 0.0
    for speed in speedList:
        sumSpeed += speed
    sumSpeed /= float(len(speedList))
    return sumSpeed

def getMoveExpected(time):
    pass#to be edited

def arcLengthToSpeedTime(arcLengthLeft,arcLengthRight):
    if(math.fabs(arcLengthRight-arcLengthLeft)<0.00001):
        countsLeft = COUNTS_PER_METER*arcLengthLeft
        countsRight = COUNTS_PER_METER*arcLengthRight
        motorsRight = 1.0
        motorsLeft = 1.0
        timeTaken = float(arcLengthRight) * COUNTS_PER_METER / motorValues[len(motorValues)-1][1] * 2
    elif(arcLengthRight>arcLengthLeft):
        countsRight = COUNTS_PER_METER*arcLengthRight
        countsLeft = countsRight*getClosestMotorMultiplierValues(arcLengthLeft/arcLengthRight)[1]
        motorsRight = 1.0
        motorsLeft = getClosestMotorMultiplierValues(arcLengthLeft/arcLengthRight)[0]
        timeTaken = float(arcLengthRight) * COUNTS_PER_METER / motorValues[len(motorValues)-1][1] * 2
    else:
        countsLeft = COUNTS_PER_METER*arcLengthLeft
        countsRight = countsLeft*getClosestMotorMultiplierValues(arcLengthRight/arcLengthLeft)[1]
        motorsLeft = 1.0
        motorsRight = getClosestMotorMultiplierValues(arcLengthRight/arcLengthLeft)[0]
        timeTaken = float(arcLengthLeft) * COUNTS_PER_METER / motorValues[len(motorValues)-1][1] * 2
    return [motorsLeft,motorsRight,timeTaken]

def getMoveHistory(begin=0,end=None):#returns in reverse chronological order, end is exclusive
    '''returns list of (left_arclength,right_arclength) in reverse chronological order'''
    output = []
    if end is None:
        end=len(moveHistory)
    for i in range(len(moveHistory)-1-begin,len(moveHistory)-1-end,-1):
        output.append(moveHistory[i])
    return output

if __name__=='__main__':
    xp_initialize()
    pass

def calibrate():
    get_encoders(False)
    for i in range(1,51,1):
        print float(i)/50.0
        motors(float(i)/50.0,float(i)/50.0)
        time.sleep(1)
        print get_encoders(False)
        print "__________"
    stop()

def go():
    get_encoders(False)
    motors(1,1)
    time.sleep(1.0)
    stop()
    get_encoders(False)
