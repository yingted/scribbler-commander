#!/usr/bin/python
import cherrypy
import os

class HelloWorld(object):
	pass

cherrypy.quickstart(HelloWorld(),config={
	'/' : {
		'tools.staticfile.root' : os.path.dirname(os.path.abspath(__file__)),
		'tools.staticfile.on' : True,
		'tools.staticfile.filename' : 'index.html',
	}
})
