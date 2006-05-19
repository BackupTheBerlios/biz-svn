# server.py -- BizServer
# Based on P. J. Eby's simple_server.py

import time
import thread
from optparse import OptionParser
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import urllib, sys
from handlers import SimpleHandler

__version__ = "0.2"
__all__ = ['BizWSGIServer','BizWSGIRequestHandler']


server_version = "BizWSGIServer/" + __version__
sys_version = "Python/" + sys.version.split()[0]
software_version = server_version + ' ' + sys_version


class ServerHandler(SimpleHandler):
	server_software = software_version

	def close(self):
		try:
			self.request_handler.log_request(
				self.status.split(' ',1)[0], self.bytes_sent
			)
		finally:
			SimpleHandler.close(self)


class BizWSGIServer(SocketServer.ThreadingMixIn, HTTPServer):
	"""BaseHTTPServer that implements the Python WSGI protocol"""

	application = None

	def server_bind(self):
		"""Override server_bind to store the server name."""
		HTTPServer.server_bind(self)
		self.setup_environ()

	def setup_environ(self):
		# Set up base environment
		env = self.base_environ = {}
		env['SERVER_NAME'] = self.server_name
		env['GATEWAY_INTERFACE'] = 'CGI/1.1'
		env['SERVER_PORT'] = str(self.server_port)
		env['REMOTE_HOST']=''
		env['CONTENT_LENGTH']=''
		env['SCRIPT_NAME'] = ''

	def get_app(self):
		return self.application

	def set_app(self,application):
		self.application = application


class BizWSGIRequestHandler(BaseHTTPRequestHandler):
	server_version = "BizWSGIServer/" + __version__  ## ?

	def get_environ(self):
		env = self.server.base_environ.copy()
		env['SERVER_PROTOCOL'] = self.request_version
		env['REQUEST_METHOD'] = self.command
		if '?' in self.path:
			path,query = self.path.split('?',1)
		else:
			path,query = self.path,''

		env['PATH_INFO'] = urllib.unquote(path)
		env['QUERY_STRING'] = query

		host = self.address_string()
		if host != self.client_address[0]:
			env['REMOTE_HOST'] = host
		env['REMOTE_ADDR'] = self.client_address[0]

		if self.headers.typeheader is None:
			env['CONTENT_TYPE'] = self.headers.type
		else:
			env['CONTENT_TYPE'] = self.headers.typeheader

		length = self.headers.getheader('content-length')
		if length:
			env['CONTENT_LENGTH'] = length

		for h in self.headers.headers:
			k,v = h.split(':',1)
			k=k.replace('-','_').upper(); v=v.strip()
			if k in env:
				continue                    # skip content length, type,etc.
			if 'HTTP_'+k in env:
				env['HTTP_'+k] += ','+v     # comma-separate multiple headers
			else:
				env['HTTP_'+k] = v
		return env

	def get_stderr(self):
		return sys.stderr

	def handle(self):
		"""Handle a single HTTP request"""

		self.raw_requestline = self.rfile.readline()
		if not self.parse_request(): # An error code has been sent, just exit
			return

		handler = ServerHandler(
			self.rfile, self.wfile, self.get_stderr(), self.get_environ()
		)
		handler.request_handler = self      # backpointer for logging
		
		handler.run(self.server.get_app())


def run(root):
	op = OptionParser(usage="%prog [options]", version="%prog "+__version__)

	op.add_option("-a", "--address", dest="address", default="localhost",
			help="specify server address (default: localhost)")
	op.add_option("-p", "--port", dest="port", default="8000",
			help="specify server port (default: 8000)")
	op.add_option("-c", "--count", dest="count", default="0",
			help="specify number of requests to handle (default: run forever)")
	
	ops, args = op.parse_args()

	address = (ops.address, int(ops.port))
	count = int(ops.count)

	httpd = BizWSGIServer(address, BizWSGIRequestHandler)
	httpd.set_app(root)
	sa = httpd.socket.getsockname()
	
	print "Serving HTTP on", sa[0], "port", sa[1], "..."
	try:
		if count:
			for i in range(count):
				httpd.handle_request()  # serve one request, then exit

		else:
			httpd.serve_forever()
## 			while 1:
## 				try:
## 					thread.start_new_thread(httpd.handle_request,())
## 					time.sleep(0.5)
## 				except thread.error:
## 					pass
				

	except KeyboardInterrupt:
		pass

