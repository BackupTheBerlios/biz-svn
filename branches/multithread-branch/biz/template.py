
# based on the recipe by by tomer filiba
# taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496702

import re


class Template(object):
	delimiter = re.compile(r"\{%(.*?)%\}", re.DOTALL)
	value = re.compile(r"\$\{(\w+)\}")
	TEXT = 0
	CODE = 1
	VARIABLE = 2

	def __init__(self, template):
		self.tokens = self.compile(template)

	@classmethod
	def from_file(cls, file):
		"""
		loads a template from a file. `file` can be either a string, specifying
		a filename, or a file-like object, supporting read() directly
		"""
		if isinstance(file, basestring):
			file = open(file)
		return cls(file.read())

	@classmethod
	def compile(cls, template):
		tokens = []
		for i, part in enumerate(cls.delimiter.split(template)):
			print "part =", part
			if i % 2 == 0:
				if part:
					for j, p in enumerate(cls.value.split(part)):
						if j % 2 == 0:
							tokens.append((cls.TEXT, p.replace("{\\%", "{%")))
						else:
							tokens.append((cls.VARIABLE, p))

			else:
				if not part.strip():
					continue
				lines = part.replace("%\\}", "%}").splitlines()
				margin = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
				realigned = "\n".join(l[margin:] for l in lines)
				code = compile(realigned, "<templite %r>" % (realigned[:20],), "exec")
				tokens.append((cls.CODE,code))
		return tokens

	def render(__self, __namespace = None, **kw):
		"""
		renders the template according to the given namespace. 
		__namespace - a dictionary serving as a namespace for evaluation
		**kw - keyword arguments which are added to the namespace
		"""
		namespace = {}
		if __namespace: namespace.update(__namespace)
		if kw: namespace.update(kw)

		def emitter(*args):
			for a in args: output.append(str(a))
		def fmt_emitter(fmt, *args):
			output.append(fmt % args)
		namespace["emit"] = emitter
		namespace["emitf"] = fmt_emitter

		output = []
		for type_, value in __self.tokens:
			if type_ == __self.CODE:
				eval(value, namespace)
			elif type_ == __self.VARIABLE:
				output.append(str(namespace[value]))
			else:
				output.append(value)

		return "".join(output)


	# shorthand
	__call__ = render
	
	
if __name__ == "__main__":
 	people = dict(yuce=27, gugu=24)
 
	page = r"""
 <html>
	 <body>
		 <table>
			 {%
				for name, age in people.iteritems():
					emit("<tr>\n")
					emit("\t<td>Name:", name, "</td>\n")
					emit("\t<td>Age:", age, "</td>\n")
					emit("</tr>\n")
			 %}
			 {%# comment %}
			 {\% this will be in the output %}
			 this is the value of variable: ${variable}
		 </table>
	 </body>
 </html>"""

	template = Template(page)
	print template(people=people, variable=4)

