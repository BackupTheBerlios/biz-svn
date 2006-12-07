
import os.path
import mimetypes
from biz import Response
from biz.app import ArgHandler

class FileHandler(ArgHandler):
    def dynamic(self, req):
        env = req.environ
        myq = env["biz.q"][env["biz.handler_name"]]
        assert "location" in myq
        
        args = env["PATH_INFO"].lstrip("/") 
        filename = os.path.join(myq["location"], args)        
        if os.path.isdir(filename):
            abort(404)
            
        return Response(file(filename),
                content_type=mimetypes.guess_type(filename))
