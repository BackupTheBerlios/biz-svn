
from biz import *
from biz.template import Template


class TemplateRunApp(Application):
	def static(self):
		q = self.q
		options = q.options.main
		assert options.has_key("template")
		q.template = Template.from_file(options["template"])
		
	class Handler(ArgHandler):
		def dynamic(self):
			q = self.q
			template = q.template.copy(True)
			request = self.request
			template["env"] = request.env
			template["path"] = request.path
			template["fields"] = request.fields
			template["options"] = q.options
			template["scriptname"] = q.scriptname
			template["selfname"] = self.name
## 			template["request"] = self.request
			
			self.response.content = HtmlContent(str(template))
			
			
def load(x):
	return TemplateRunApp(x)

			