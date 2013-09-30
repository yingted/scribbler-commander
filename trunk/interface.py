#!/usr/bin/python
import cherrypy
import os
import myro
import socket
import datetime

# connect to myro
try:
	s=socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# test if simulator is running
	s.bind(("127.0.0.1", 60000))
	s.close()
except socket.error, e:
	# simulator is running, so wait and connect to it
	robot = myro.globvars.robot = myro.robots.simulator.SimScribbler(None)
else:
	# start a new simulator
	myro.simulator()

if not hasattr(robot, "robotinfo"): # prevent KeyError on KeyboardInterrupt
	robot.robotinfo = {}

class ScribblerCommander(object):
	@cherrypy.expose
	def index(self, do=None,**kwargs):
		print "foo"
		# check if action is safe
		if do in ("forward", "backward", "stop", "left", "right"):
			# TODO replace with a proper RPC mechanism
			# and expose REST API
			getattr(self,do)()
		# switch POST to a GET
		elif do in ("go"):
		    getattr(self,do)(kwargs.get('actionSelection'))
		raise cherrypy.HTTPRedirect('/')
	def go(self,actionSelection=None):
            if actionSelection=="circle":
                # TODO ADD FUNCTION HERE AND START REPLACING FROM THIS LINE
                myro.forward(2)
                # END REPLACE
	def forward(self):
		myro.forward(1)
	def backward(self):
		myro.backward(1)
	def left(self):
		myro.turn(1)
	def right(self):
		myro.turn(-1)
	def stop(self):
		myro.stop()

cherrypy.quickstart(ScribblerCommander(),config={
	'/' : {
		'tools.staticfile.root' : os.path.dirname(os.path.abspath(__file__)),
		'tools.staticfile.on' : True,
		'tools.staticfile.filename' : 'index.html',
		'tools.staticfile.match' : '^/$', # only match the exact url /
	}
})
