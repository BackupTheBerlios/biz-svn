
def run(environ, start_response):
	start_response("200 OK", [("content-type","text/plain")])
	return "\n".join(environ["biz.path"])
