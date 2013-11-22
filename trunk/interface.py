#!/usr/bin/python
import cherrypy
import os
import myro
import util
import sys
import itertools
util.connect_async()
def jsonify(f):
	def wrapped(*args, **kwargs):
		val = f(*args, **kwargs)
		response.headers['Content-Type'] = 'application/json'
		return json.dumps(val)
	return wrapped
def ajax(handler):
	return cherrypy.expose(cherrypy.tools.allow(methods=('POST',))(cherrypy.tools.json_out()(handler)))
class ScribblerCommander(object):
	@cherrypy.expose
	def index(self, do=None):
		# check if action is safe
		if hasattr(self, do):
			handler = getattr(self, do)
			if hasattr(handler, 'exposed') and handler.exposed:
				getattr(self, do)()
		# switch POST to a GET
		raise cherrypy.HTTPRedirect('/')
	@ajax
	def forward(self):
		myro.forward(1)
	@ajax
	def backward(self):
		myro.backward(1)
	@ajax
	def left(self):
		myro.turn(1)
	@ajax
	def right(self):
		myro.turn(-1)
	@ajax
	def stop(self):
		myro.stop()
	@ajax
	def battery(self):
		try:
			return myro.getBattery()/9.
		except AttributeError:
			raise cherrypy.HTTPError(503, 'Service Unavailable')
	@cherrypy.expose
	@cherrypy.tools.allow(methods=('POST',))
	def subscribe(self):
		"""subscribe to events"""
		class gen(object):
			def __iter__(self):
				return self
			def next(self):
				myro.wait(10**10)
		return itertools.chain((), gen())
	subscribe._cp_config = {'response.stream' : True}

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
