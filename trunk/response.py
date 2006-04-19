# response.py

import os
from cStringIO import StringIO


RESPONSES = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No response', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this server.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
              'this proxy before proceeding.'),
        408: ('Request Time-out', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service temporarily overloaded',
              'The server cannot process the request due to a high load'),
        504: ('Gateway timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version not supported', 'Cannot fulfill request.'),
        }

class Content(object):
	__slots__ = "ctype","_clen","_descriptor"
	
	def __init__(self, ctype):
		self.ctype = ctype
		self._clen = 0
		
	def get_filedescriptor(self):
		"""return a file descriptor of the content.
		
		Override this.
		"""
		return None


class TextContent(Content):
	__slots__ = "content"
	
	def __init__(self, content=u""):
		Content.__init__(self, "text/plain")
		self.content = str(content)
		self._clen = len(self.content)
		self._descriptor = None		
		
	def get_filedescriptor(self):
		if not self._descriptor:
			self._descriptor = StringIO(self.content)
			
		return self._descriptor


class EmptyContent(TextContent):
	def __init__(self):
		TextContent.__init__(self, u"")


class HtmlContent(TextContent):
	def __init__(self, content=u""):
		TextContent.__init__(self, content)
		self.ctype = "text/html"
		
		
class FileContent(Content):
	def __init__(self, filename, ctype):
		Content.__init__(self, ctype)
		self._descriptor = file(filename, "rb")
		self._clen = os.stat(filename).st_size
		
	def get_filedescriptor(self):
		return self._descriptor	


class Response:
	def __init__(self, start_response, code=200, content=EmptyContent()):
		self.rcode = code
		self.content = content
		self.heads = {}
		self.start_response = start_response
		
	def __iter__(self):
		self.heads["content-type"] = self.content.ctype
		self.heads["content-length"] = str(self.content._clen)

		self._other_headers()

		self.start_response("%d %s" % (self.rcode,RESPONSES.get(self.rcode, ["Unknown"])[0]),
				[x for x in self.heads.iteritems()])		
		return self.content.get_filedescriptor()
		
	def _other_headers(self):  # TODO: Change name of this
		"""send other headers.
		
		Override this to add custom headers.
		"""
		pass
