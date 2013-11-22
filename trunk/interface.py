#!/usr/bin/python
import cherrypy
import os
import myro
import util
import sys
import itertools
import shelve
import threading
import simplejson as json
import bisect
import numpy
util.connect_async()
def ajax(handler):
	return cherrypy.expose(cherrypy.tools.allow(methods=('POST',))(cherrypy.tools.json_out()(handler)))
deltas = []
deltas_change = threading.Condition()
@util.state.watch
def update(*t_key_val):
	try:
		deltas_change.acquire()
		deltas.append(t_key_val)
		deltas_change.notify_all()
	finally:
		deltas_change.release()
class Subscription(object):
	def __init__(self):
		self.prefix.reverse()
	def __iter__(self):
		return self
	def next(self):
		if self.prefix:
			return elt_to_js(self.prefix.pop())
		while True:
			if self.i < len(deltas):
				self.i += 1
				return elt_to_js(deltas[self.i-1])
			try:
				deltas_change.acquire()
				deltas_change.wait(1)
			finally:
				deltas_change.release()
			return"<script>console.log('loading')</script>"
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
	@ajax
	def subscribe(self, t=None):
		"""subscribe to events"""
		if t is None:
			cherrypy.response.headers['Content-Type'] = 'application/javascript'
			i = len(deltas)
			cur = dict((key,util.state.history(key)[-1]) for key in util.state)
			j = len(deltas)
			prefix = []
			#hide race conditions
			for t, key, val in deltas[i:j]:
				if t > cur[key][0]:
					cur[key] = t, val
			for key in cur:
				t, val = cur[key]
				prefix.append((key, val, t))
			t = 0
			if j:
				t = deltas[j-1][0]
			return {'t':t, 'deltas':prefix}
		t = float(t)
		while True:#completely different logic
			if deltas and deltas[-1][0] > t:
				i = bisect.bisect_left(deltas,(numpy.nextafter(t,t+1),))
				j = len(deltas)
				return {'t':deltas[j-1][0], 'deltas':deltas[i:j]}
			try:
				deltas_change.acquire()
				deltas_change.wait(25)
			finally:
				deltas_change.release()
			return {'t':t, 'deltas':[]}

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
