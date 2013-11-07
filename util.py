try:
	from myro import *
except ImportError:
	pass
import os
import struct
def xp_initialize():
	"""cross-platform initialization"""
	for dev in'/dev/rfcomm0','/dev/tty.scribbler':
		if os.path.exists(dev):
			initialize(dev)
			break
	else:
		initialize('COM40')
def get_obstacle(emitters):
	"""count IR bounces using emitters"""
	if isinstance(emitters,str):
		emitters=1<<'lrc'.index(emitters[0])
	try:
		robot.lock.acquire()
		robot.ser.write(struct.pack('>BHB',157,400,emitters))
		return(robots.scribbler.read_2byte(robot.ser)+2**15)%2**16-2**15
	finally:
		robot.lock.release()
def memoize(func):
	cache={}
	def wrapped(*args):
		if args not in cache:
			cache[args] = func(*args)
		return cache[args]
	return wrapped
