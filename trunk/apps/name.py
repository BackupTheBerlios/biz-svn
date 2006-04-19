
from biz.response import Response, TextContent, HtmlContent

def run(environ, start_response):
	params = environ["biz.params"]

	try:
		page = "Your name is: <b>%(name)s %(surname)s</b>. It's a nice name!" % params
		return Response(start_response, content=HtmlContent(page))

	except KeyError:
		return Response(start_response, content=TextContent("Invalid request"))

