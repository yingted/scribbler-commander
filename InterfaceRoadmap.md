# Introduction #

The interface should support:
  1. basic browsers
  1. desktop browsers (with AJAX)
  1. mobile/low-resolution browsers
  1. REST clients

# Details #

The plan is to use progressive enhancement, except allow ourselves to break clients older than ourselves.

Appearance:
  1. basic form
  1. style the page
  1. AJAX and animations

Internals:
  1. HTML form interface (through POST)
  1. provide second RESTful interface for use with AJAX
  1. possibly use `cherrypy-jsonrpcserver` and JSON-RPC if we're feeling ambitious