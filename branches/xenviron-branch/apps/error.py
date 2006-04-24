# error.py

from string import Template

from biz.app import Application
from biz.content import HtmlContent


class Error(Application):
	def run(self):
		env = self.environ
		assert env.has_key("biz.error.code") and env.has_key("biz.error.message"), \
				"biz.error.code and biz.error.message should be in environ"

		template = Template(self.options.get("error.template",
				'<p> ${code}: <span style="color: red">${message}</span></p>'))

		page = template.substitute(code=env["biz.error.code"],
				message=env["biz.error.message"])

		self.rcode = int(env["biz.error.code"])
		self.content = HtmlContent(page)


def load(environ, start_response, options):
	return Error(environ, start_response, options)

