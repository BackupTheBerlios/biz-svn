
def run(environ, start_response):
	start_response("200 OK", [("content-type","text/python")])
	return file("file.py")
