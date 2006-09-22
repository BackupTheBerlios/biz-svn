import os.path
from biz.app import ArgHandler
from biz.content import HtmlContent
from biz.template import Template


class TemplateHandler(ArgHandler):
	"""
	* set self.template to a biz.Template before calling dynamic()
	"""
	def dynamic(self):
		q = self.q; r = self.r
##		assert "template" in q[self.name]
		
##		template = q[self.name]["template"].copy()
		template = self.template.copy()
		template["r"] = r
		template["scriptname"] = q.scriptname
		template["appname"] = q.appname
		template["selfname"] = self.name
		if q.scriptname:
			template["baseloc"] = "/%s/%s" % (q.scriptname,q.appname)
		else:
			template["baseloc"] = "/%s" % q.appname
		
		r.content = HtmlContent(template)
		
		
				
		