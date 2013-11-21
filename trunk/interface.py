#!/usr/bin/python
import cherrypy
import os
import myro
import util
import sys
util.connect_async()
class ScribblerCommander(object):
	@cherrypy.expose
	def index(self, do=None):
		# check if action is safe
		if do in ("forward", "backward", "stop", "left", "right"):
			# TODO replace with a proper RPC mechanism
			# and expose REST API
			getattr(self,do)()
		# switch POST to a GET
		raise cherrypy.HTTPRedirect('/')
	# some simple methods, which will be decorated later
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
	@cherrypy.expose
	def battery(self):
		try:
			return str(myro.getBattery()/9.)
		except AttributeError:
			raise cherrypy.HTTPError(503, 'Service Unavailable')


current_dir = os.path.dirname(os.path.abspath(__file__))
cherrypy.quickstart(ScribblerCommander(),config={
	'/' : {
		'tools.staticdir.root' : current_dir,
		'tools.staticfile.root' : current_dir,
		'tools.staticfile.on' : True,
		'tools.staticfile.filename' : 'index.html',
		'tools.staticfile.match' : '^/$', # only match the exact url /
	},
	'/static' : {
		'tools.staticdir.on' : True,
		'tools.staticdir.dir' : 'static',
	},
})
