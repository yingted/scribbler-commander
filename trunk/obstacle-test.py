from myro import *
import struct
for dev in'/dev/rfcomm0','/dev/tty.scribbler':
	if os.path.exists(dev):
		initialize(dev)
		break
else:
	initialize('COM40')
robot.setIRPower(133)
def get_obstacle(lrc):
	try:
		robot.lock.acquire()
		robot.ser.write(struct.pack('>BHB',157,200,1<<lrc))
		return(robots.scribbler.read_2byte(robot.ser)+2**15)%2**16-2**15
	finally:
		robot.lock.release()
get_obstacle(0b111)
import math
lambd=math.exp(-1./5)
val=0.
while True:
		val=lambd*val+(1-lambd)*get_obstacle(2)
		x=int(val)
		print '\x1b[%dm%s\x1b[0m'%(31+(x>=0),'#'*(abs(x)/40))
