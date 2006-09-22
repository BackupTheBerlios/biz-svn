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


import sys
import re
from collections import deque

from biz.errors import FileNotFoundError

__VERSION__ = (0,0,89)


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
	
	def __init__(self, encoding=None):
		self.handlers = [("chain",self.chainedline),
						("oneliner",self.onelinerline),
						("header",self.beginline),
						("end",self.endline)]
						
		self.items = []
		self.encoding = encoding or "utf-8"

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
		self.items.append((self.TEXT,u"".join(text)))
	
	def parse(self, lines):
		text = []
		if isinstance(lines, str):
			lines = unicode(lines, self.encoding)
		
		for i, text1 in enumerate(self.paragraph.split(lines)):
			# handle paragprah, {? ... ?}
			if i%2:
				ts = [x for x in text1.split("\n") if x.strip()]
				margin = len(ts[0]) - len(ts[0].lstrip())
				for l in ts:
					self.items.append((self.ONELINER,l[margin:]))
			else:
				for j, text2 in enumerate(self.trans.split(text1)):
					# handle trans, {XXX: ... :}
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

	def __init__(self, tmpl, namespace=None, encoding=None, strict=True):
		"""{N_:
		* namespace : set default namespace (default: {})
		* encoding : set default encoding (default: utf-8)
		* (NOT-WORKS) strict : set strict substitution. If any variable is missing in the
		namespace, an exception is raised; or nonstrict substitution (if any
		variable is missing, it is substituted with empty string) (default: True)
		:}
		"""
		self.levels = deque()
		self.levels.append(0)
		
		self.encoding = encoding or "utf-8"

		self.namespace = namespace and dict(namespace) or {}
		self._outlist = []
		self.output = tmpl
		self.changed = True
		
		def emitter(*args):
##			self._outlist.extend([unicode(str(a), self.encoding) for a in args])
			for a in args:
				if isinstance(a, unicode):
					self._outlist.append(a)
				else:
					self._outlist.append(unicode(str(a), self.encoding))
##			self._outlist.extend([unicode("%s" % a, self.encoding) for a in args])
			
		def loadbody(filename):
			f = file(filename)  # XXX: try/except here
			text = self.body.search(f.read()).group(1) or ""
			f.close()
			return text
		
		def include(filename):
			f = file(filename)  # XXX: try/except here
			text = f.read()
			f.close()
			p = Parser(encoding=self.encoding)
			p.parse(text)
			code = "\n".join(self.walk(p.items))
			namespace = self.namespace
			exec code in namespace
		
		self.namespace["echo"] = emitter
		self.namespace["loadbody"] = loadbody
		self.namespace["include"] = include
		self.namespace["_"] = lambda s: s
		self.namespace["N_"] = lambda s: s
		
		parser = Parser(encoding)
		parser.parse(tmpl)
		self.parsed = parser.items
	
	def _prep_output(self, force=False):
		if force or self.changed:
			self._outlist = []
			code = u"\n".join(self.walk(self.parsed))
			namespace = self.namespace  #.copy() # XXX:
			
			exec code in namespace

			self.output = u"".join(self._outlist)
			self.changed = False
		
	def render(self, force=False):
		self._prep_output(force)			
		return unicode.encode(self.output, self.encoding)
		
	def render_unicode(self, force=False):
		self._prep_output(force)
		return self.output
		
	def __str__(self):
		self._prep_output()
		return unicode.encode(self.output, self.encoding)
		
	def __unicode__(self):
		self._prep_output()
		return self.output
		
	def __setitem__(self, name, value):
		self.namespace[name] = value
		self.changed = True
		
	def __getitem__(self, name):
		return self.namespace[name]
		
	def __delitem__(self, name):
		del self.namespace[name]
		
	@staticmethod
	def open(fileobj, namespace=None, encoding=None):
		"""
		loads a template from a file. ``fileobj`` can be either a string, specifying
		a filename, or a file-like object, supporting read() directly
		"""
		
		if isinstance(fileobj, basestring):
			fileobj = file(fileobj)
		
		try:
			return Template(fileobj.read(), namespace, encoding=encoding)
		except IOError, e:
			raise TemplateNotFoundError("filename", msg=e)
		
	@staticmethod
	def from_parsed(parsed, namespace=None, encoding=None):
		template = Template("", namespace, encoding=encoding)
		template.parsed = parsed  # XXX: parsed is copied shallowly
		return template
		
	def copy(self):
		return self.from_parsed(self.parsed, encoding=self.encoding)
		
	def copyall(self):
		return self.from_parsed(self.parsed, self.namespace, encoding=self.encoding)
			
	def update(self, dictionary):
		self.namespace.update(dictionary)
		
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
		tabs = "\t"*level
		output = n =="=" and (u"%secho(%s)" % (tabs,text)) or \
				u"%secho(%s('''%s'''))" % (tabs,n or "",text.replace("'", "\\'"))
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
	template["bold"] = lambda s: "<b>%s</b" % s
	template["upper"] = lambda s: s.upper()
	print template.render()
