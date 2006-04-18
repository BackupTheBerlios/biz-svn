
def run(environ, start_response):
	start_response("200 OK", [('Content-Type','text/plain')])
	return ["Wello, World!", " %s in_cache: %s" % \
			(environ["biz.application.debug.usage"],environ["biz.application.debug.in_cache"])]

