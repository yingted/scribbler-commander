try:
	from myro import *
except ImportError:
	pass
import os
import struct
import socket
_use_simulator = True
def simulator_started():
	# connect to myro
	try:
		s=socket.socket()
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# test if simulator is running
		s.bind(("127.0.0.1", 60000))
		s.close()
		return False
	except socket.error, e:
		# simulator is running
		return True
def xp_initialize():
	"""cross-platform initialization"""
	for dev in'/dev/rfcomm0','/dev/tty.scribbler':
		if os.path.exists(dev):
			initialize(dev)
			break
	else:
		initialize('COM40')
connected=False
def connect_async(cb=None):
	"""asynchronously connect to scribbler"""
	global connected
	if _use_simulator:
		robot = None
		if simulator_started():
			robot = myro.globvars.robot = myro.robots.simulator.SimScribbler(None)
		else:
			# start a new simulator
			myro.simulator()
		if robot is not None and not hasattr(robot, "robotinfo"): # prevent KeyError on KeyboardInterrupt
			robot.robotinfo = {}
	else:
		connected = False
		xp_initialize()
	connected = True
	if cb is not None:
		cb()
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
def get_encoders(zero=False):
	"""returns encoder values, optionally resetting them"""
	try:
		robot.lock.acquire()
		robot.ser.write(struct.pack('BB',171,zero))
		#return robot.read_uint32(),robot.read_uint32()
		return struct.unpack('<II',robot.ser.read(8))
	finally:
		robot.lock.release()
def memoize(func):
	"""decorator to naively memoize function calls"""
	cache={}
	def wrapped(*args):
		if args not in cache:
			cache[args] = func(*args)
		return cache[args]
	return wrapped
