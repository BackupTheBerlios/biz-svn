
import biz
from biz.template import Template


class TemplateRunApp(biz.Application):
	def static(self):
		q = self.q
		assert q.options.has_key("template")
		q.template = Template.open(q.options["template"])
		
	class Handler(biz.ArgHandler):
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
				
			self.r.content = biz.HtmlContent(template.render())
			
			
def load(x):
	return TemplateRunApp(x)

			