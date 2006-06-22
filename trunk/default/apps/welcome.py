
from biz import *
from biz.template import Template
from biz.handlers.filehandler import FileHandler


class DumbHandler(ArgHandler):
	def dynamic(self):
		q = self.q
		
		template = q.template.copy(True)
		template["pagemode"] = self.pagemode
		template["pagetitle"] = self.pagetitle
		
		self.r.content = HtmlContent(str(template))
		

class WelcomeApp(Application):
	def static(self):
		q = self.q
		
		q.template = Template.from_file("templates/welcome/page.tmpl")
		self._files_Handler = FileHandler
		q._files_Handler = dict(location="htdocs/welcome")
	
	class Handler(DumbHandler):
		def __init__(self, parent, name, **kwargs):
			ArgHandler.__init__(self, parent, name, **kwargs)
			self.pagemode = "home"
			self.pagetitle = "Welcome"
		
	class docsHandler(DumbHandler):
		def __init__(self, parent, name, **kwargs):
			ArgHandler.__init__(self, parent, name, **kwargs)
			self.pagemode = "docs"
			self.pagetitle = "Documentation"
			
	class tutorialHandler(DumbHandler):
		def __init__(self, parent, name, **kwargs):
			ArgHandler.__init__(self, parent, name, **kwargs)
			self.pagemode = "tutorial"
			self.pagetitle = "Tutorial"
		
def load(x):
	return WelcomeApp(x)
	

		