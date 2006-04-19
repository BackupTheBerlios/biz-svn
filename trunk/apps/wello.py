
def run(environ, start_response):
	start_response("200 OK", [('Content-Type','text/plain')])
	return ["Wello, World!", " %s in_cache: %s again'n again 3..." % \
			(environ["biz.application.debug.usage"],environ["biz.application.debug.in_cache"])]

