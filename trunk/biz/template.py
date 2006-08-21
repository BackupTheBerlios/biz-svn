# -*- coding: utf-8 -*-
# template.py -- Biz templating
# This templating system was initially based on Tomer Filiba's "templite",
# ... http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496702

# Biz web application framework
# Copyright (C) 2006  Yuce Tekol
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


import re
from collections import deque

from biz.errors import FileNotFoundError


class TemplateNotFoundError(FileNotFoundError):
	pass


class Parser:
	beginline = re.compile(r"^\s*\{%(.*)")
	endline = re.compile(r"^\s*%\}\s*$")
	onelinerline = re.compile(r"^\s*\{%(.*)%\}\s*$")
	chainedline = re.compile(r"^\s*%\}(.*)\{%\s*$")
	paragraph = re.compile(r"{\?(.*?)\?}", re.DOTALL)
	trans = re.compile(r"{([\w=.]*):(.*?):}", re.DOTALL)
	
	TEXT, HEADER, END, CHAIN, ONELINER, TRANS = \
		"text", "header", "end", "chain", "oneliner", "trans"
	
	def __init__(self):
		self.handlers = [("chain",self.chainedline),
						("oneliner",self.onelinerline),
						("header",self.beginline),
						("end",self.endline)]
						
		self.items = []

	def handle_header(self, groups):
		code, = groups
		self.items.append((self.HEADER,code.strip()))
		
	def handle_end(self, groups):
		self.items.append((self.END,None))
			
	def handle_chain(self, groups):
		code, = groups		
		self.items.append((self.CHAIN,code.strip()))
		
	def handle_oneliner(self, groups):
		code, = groups
		self.items.append((self.ONELINER,code.strip()))
		
	def handle_text(self, text):
		self.items.append((self.TEXT,"".join(text)))
	
	def parse(self, lines):
		text = []
		lines = unicode(lines, "utf-8")
		
		for i, text1 in enumerate(self.paragraph.split(lines)):
			# handle paragprah, {? ... ?}
			if i%2:
				ts = [x for x in text1.split("\n") if x.strip()]
				margin = len(ts[0]) - len(ts[0].lstrip())
				for l in ts:
					self.items.append((self.ONELINER,l[margin:]))
			else:
				for j, text2 in enumerate(self.trans.split(text1)):
					if j%3 == 1:
						n = text2
					elif j%3 == 2:
						self.items.append((self.TRANS,(n,text2)))
					else:
						auglines = text2.split("\n")
						auglines = ["%s\n" % x for x in auglines[:-1]] + [auglines[-1]]
						for line in auglines:
## 							if not line:
## 								continue
								
							for handler, parser in self.handlers:
								r = parser.search(line)
								if r:
									if text:
										self.handle_text(text)
										text = []
										
									getattr(self, "handle_%s" % handler)(r.groups())
									break
							else:
								text.append(line)
						
						if text:
							self.handle_text(text)
							text = []


class Template:
	variable = re.compile(r"\$[{]?([a-zA-Z][\w.]*(?:\[[\w.]\])*)[}]?")
	body = re.compile(r"<body>(.*)</body>", re.DOTALL | re.MULTILINE)

	def __init__(self, tmpl, variables=None):
		self.levels = deque()
		self.levels.append(0)

		self.variables = variables and dict(variables) or {}
		self._outlist = []
		self.output = tmpl
		self.changed = True
		
		def emitter(*args):
			self._outlist.extend([unicode(str(a), "utf-8") for a in args])
			
		def loadbody(filename):
			f = file(filename)  # XXX: try/except here
			text = self.body.search(f.read()).group(1) or ""
			f.close()
			return text
		
		def include(filename):
			f = file(filename)  # XXX: try/except here
			text = f.read()
			f.close()
			p = Parser()
			p.parse(text)
			code = "\n".join(self.walk(p.items))
			namespace = self.variables
			exec code in namespace
			
		self.variables["echo"] = emitter
		self.variables["loadbody"] = loadbody
		self.variables["include"] = include
		self.variables["_"] = lambda s: s
		self.variables["N_"] = lambda s: s
		
		parser = Parser()
		parser.parse(tmpl)
		self.parsed = parser.items
		
	def render(self, force=False):
		if force or self.changed:
			self._outlist = []
			code = u"\n".join(self.walk(self.parsed))
			namespace = self.variables  #.copy() # XXX:
			
			exec code in namespace
			self.output = u"".join(self._outlist)
			
			self.changed = False
			
		return unicode.encode(self.output, "utf-8")
		
	__str__ = render
		
	def __setitem__(self, attr, value):
		self.variables[attr] = value
		self.changed = True
		
	@staticmethod
	def open(fileobj, variables=None):
		"""
		loads a template from a file. ``fileobj`` can be either a string, specifying
		a filename, or a file-like object, supporting read() directly
		"""
		
		if isinstance(fileobj, basestring):
			fileobj = file(fileobj)
		
		try:
			return Template(fileobj.read(), variables)	
		except IOError, e:
			raise TemplateNotFoundError("filename", msg=e)
		
	@staticmethod
	def from_parsed(parsed, variables=None):
		template = Template("", variables)
		template.parsed = parsed  # XXX: parsed is copied shallowly
		return template
		
	def copy(self):
		return self.from_parsed(self.parsed)
		
	def copyall(self):
		template = self.from_parsed(self.parsed)
		template.variables = self.variables.copy()
		return template			
			
	def update(self, dictionary):
		self.variables.update(dictionary)
		
	def handle_header(self, value, level):
		output = "%s%s:" % ("\t"*level,value)
		self.levels.append(level)
		return (level + 1,output)
		
	def handle_end(self, value, level):
		return (self.levels.pop(),"")
		
	def handle_chain(self, value, level):
		newlevel = self.levels.pop()
		self.levels.append(newlevel)
		output = u"%s%s:" % ("\t"*newlevel,value)
		return (newlevel + 1,output)
		
	def handle_oneliner(self, value, level):
		if value.startswith("#"):
			return (level,"")
			
		return (level,u"%s%s" % ("\t"*level,value))
		
	def handle_text(self, value, level):
		def q(i, v):
			if i%2:
				return u"%s" % v
			else:
				return u"'''%s'''" % v.replace("'", "\\'")
				
		values = [q(*iv) for iv in enumerate(self.variable.split(value))]
		output = u"%secho(%s)" % ("\t"*level,", ".join(values))
		return (level,output)
		
	def handle_trans(self, value, level):
		n, text = value
		output = n =="=" and (u"%secho(%s)" % ("\t"*level,text)) or \
				u"echo(%s('''%s'''))" % (n or "",text.replace("'", "\\'"))
##		return (level,"echo(%s_('''%s'''))" % (n or "",text.replace("'", "\\'")))
		return (level,output)
		
	def walk(self, parsed):
		level = 0
		output = []
		for handler, value in parsed:
			level, out = getattr(self, "handle_%s" % handler)(value, level)
			if out:
				output.append(out)
				
		return output


if __name__ == "__main__":
	test = ur"""
<html>
	<body>
		<table>
		{% for name, age in people.iteritems()
			<tr>
				<td>$name</td><td>$age</td>
				{% if age > 60
					<td>old</td>
				%} elif age > 30 {%
					<td>not old</td>
				%} elif age > 20 {%
					<td>young</td>
				%} elif age > 15 {%
					<td>teen</td>
				%} elif age > 10 {%
					<td>very young</td>
				%} elif age > 5 {%
					<td>kiddo</td>
				%} else {%
					<td>baby</td>
				%}
			</tr>
		%}
		</table>
		{% a = 'oneliner\n' %}
		This is {_:Translated text:}.
		[$a] is an {? echo("important number!.") ?} Isn't it?
		{upper:Uppercase string.:}
		{=:" ".join(["Shortcut", "emit"]):}
		{bold:Bold text:}
		{=:"%s!" % ", ".join(["Hello", "World"]):}
		{% echo("%}") %}
	</body>
	{?
	if 10 > 5:
		value = 5
	else:
		value = 10
	?}
	$value
</html>
"""
	template = Template(test)
	template["people"] = {"gugu":24, "ali yankı":13}
	template["_"] = lambda s: s
	template["N_"] = lambda s: s.upper()
	template["bold"] = lambda s: "<b>%s</b" % s
	template["upper"] = lambda s: s.upper()
	print template.render()
