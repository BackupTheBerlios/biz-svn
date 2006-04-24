# error.py

from string import Template

from biz.app import Application
from biz.content import HtmlContent


class Error(Application):
	Application.requires += ["biz.error.code", "biz.error.message"]
	##Application.accepts += ["biz.app.error.template"]

	def run(self):
		props = self.properties

		template = Template(self.options.get("error.template",
				'<p> ${code}: <span style="color: red">${message}</span></p>'))

		ec = props["biz.error.code"]

		page = template.substitute(code=ec,
				message=props["biz.error.message"])

		self.rcode = ec
		self.content = HtmlContent(page)


def load(root):
	return Error(root)

