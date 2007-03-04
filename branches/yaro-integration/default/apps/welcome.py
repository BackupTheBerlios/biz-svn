
import os.path
from biz import *
from biz.template import Template
from biz.handlers.filehandler import FileHandler


class DumbHandler(ArgHandler):
    def dynamic(self, req):
        env = req.environ
        q = env["biz.q"]        
        template = q.template.copy()
        template["basepath"] = env["biz.basepath"]                
        template["pagemode"] = self.pagemode
        template["pagetitle"] = self.pagetitle
        return Response(template.render(), content_type="text/html")
        

class WelcomeApp(Application):
    def static(self):
        env = self.environ
        q = env["biz.q"]
        q.template = Template.open(pathFor("templates/welcome/page.bit"))
        self._files_Handler = FileHandler
        q._files_Handler = dict(location=pathFor("htdocs/welcome"))
    
    class Handler(DumbHandler):
        def __init__(self, **kwargs):
            ArgHandler.__init__(self, **kwargs)
            self.pagemode = "home"
            self.pagetitle = "Welcome"
        
    class docsHandler(DumbHandler):
        def __init__(self, **kwargs):
            ArgHandler.__init__(self, **kwargs)
            self.pagemode = "docs"
            self.pagetitle = "Documentation"
            
    class tutorialHandler(DumbHandler):
        def __init__(self, **kwargs):
            ArgHandler.__init__(self, **kwargs)
            self.pagemode = "tutorial"
            self.pagetitle = "Tutorial"
        
def load(x):
    return WelcomeApp(x)
