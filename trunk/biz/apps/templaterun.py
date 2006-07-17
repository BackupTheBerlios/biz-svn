
from biz import *
from biz.template import Template


class TemplateRunApp(Application):
	def static(self):
		q = self.q
		options = q.options.main
		assert options.has_key("template")
		q.template = Template.open(options["template"])
		
	class Handler(ArgHandler):
		def dynamic(self):
			q = self.q
			template = q.template.copy()
			template["r"] = self.r
			template["options"] = q.options
			template["scriptname"] = q.scriptname
			template["appname"] = q.appname
			template["selfname"] = self.name
			if q.scriptname:
				template["baseloc"] = "/%s/%s" % (q.scriptname,q.appname)
			else:
				template["baseloc"] = "/%s" % q.appname
				
			self.r.content = HtmlContent(template)
			
			
def load(x):
	return TemplateRunApp(x)

			