try:
	from myro import *
except ImportError:
	pass
import os
import struct
import socket
import collections
import shelve
import time
import atexit
_use_simulator = True
def simulator_started():
	# connect to myro
	try:
		s=socket.socket()
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# test if simulator is running
		s.bind(('127.0.0.1', 60000))
		s.close()
		return False
	except socket.error, e:
		# simulator is running
		return True
def xp_initialize():
	'''cross-platform initialization'''
	for dev in'/dev/rfcomm0','/dev/tty.scribbler':
		if os.path.exists(dev):
			initialize(dev)
			break
	else:
		initialize('COM40')
def get_obstacle(emitters):
	'''count IR bounces using emitters'''
	if isinstance(emitters,str):
		emitters=1<<'lrc'.index(emitters[0])
	try:
		robot.lock.acquire()
		robot.ser.write(struct.pack('>BHB',157,400,emitters))
		return(robots.scribbler.read_2byte(robot.ser)+2**15)%2**16-2**15
	finally:
		robot.lock.release()
def get_encoders(zero=False):
	'''returns encoder values, optionally resetting them'''
	try:
		robot.lock.acquire()
		robot.ser.write(struct.pack('BB',171,zero))
		#return robot.read_uint32(),robot.read_uint32()
		return struct.unpack('<II',robot.ser.read(8))
	finally:
		robot.lock.release()
def read_jpeg_scan(out):
	while True:
		ch = robot.ser.read(1)
		out(ch)
		if ch == '\xff':
			while ch == '\xff':
				ch = robot.ser.read(1)
				out(ch)
			if ch in '\x00\x01\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9':
				if ch == '\xd9':
					break
				hi, lo = robot.ser.read(2)
				out(hi + lo)
				out(robot.ser.read((hi << 8) | lo))
	bm0 = robot.read_uint32()# Start
	bm1 = robot.read_uint32()# Read
	bm2 = robot.read_uint32()# Compress
	if robot.debug:
		freq = 60e6
		print 'got image\n%.3f %.3f' % (((bm1 - bm0) / freq), ((bm2 - bm1) / freq))
def memoize(func):
	'''decorator to naively memoize function calls'''
	cache={}
	def wrapped(*args):
		if args not in cache:
			cache[args] = func(*args)
		return cache[args]
	return wrapped
class State(shelve.DbfilenameShelf):
	'''persistent state
	TODO allow loading only part of the state'''
	def __init__(self, filename='data/log', flag='c', protocol=None, writeback=False):
		shelve.DbfilenameShelf.__init__(self, filename, flag, protocol, writeback)
		atexit.register(self.close)
		self.handlers = []
	def history(self, key):
		'''returns the history of the values of the key
		the return value should not be changed'''
		return shelve.DbfilenameShelf.__getitem__(self, key)
	def age(self, key):
		'''returns how long ago the key was set'''
		return time.time()-self.history(key)[-1][0]
	def __getitem__(self, key):
		'''returns the current value of the key'''
		return self.history(key)[-1][1]
	def watch(self, cb):
		'''adds a callback for setitem'''
		self.handlers.append(cb)
	def __setitem__(self, key, val):
		'''adds a new value to this history'''
		l = []
		if key in self:
			l = self.history(key)
		t = time.time()
		l.append((t, val))
		shelve.DbfilenameShelf.__setitem__(self, key, l)
		for cb in self.handlers:
			cb(t, key, val)
		self.sync()
state = State()

state['connected'] = False
def connect_async(cb=None):
	'''asynchronously connect to scribbler'''
	if _use_simulator:
		robot = None
		if simulator_started():
			robot = myro.globvars.robot = myro.robots.simulator.SimScribbler(None)
		else:
			# start a new simulator
			myro.simulator()
		if robot is not None and not hasattr(robot, 'robotinfo'): # prevent KeyError on KeyboardInterrupt
			robot.robotinfo = {}
	else:
		state['connected'] = False
		xp_initialize()
	state['connected'] = True
	if cb is not None:
		cb()
