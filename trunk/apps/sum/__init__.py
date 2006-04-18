
def run(environ, start_response):
	start_response("200 OK", [("content-type","text/plain")])
	return str(sum([float(p) for p in environ["biz.path"][1:]]))
