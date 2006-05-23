#errors.py

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

__all__ = ["BizError", "RootError", "FileNotFoundError", "ImproperFileError",
			"RootEnvironmentError", "NoApplicationExistsError",
			"ImproperConfigFileError", "ConfigFileNotFoundError",
			"ModuleNotFoundError", "WSGIKeyNotPresentError",
			"ApplicationNotFoundInModuleError", "ApplicationError",
			"ApplicationStaticError", "ApplicationDynamicError"]
			

def _(s):  # TODO: Replace this with a true i18n function
	return s
	

class BizError(Exception):
	def __init__(self, what, msg=None, **kwargs):
		"""
		* what : item caused the error.
		* msg : error message.
		* info : a dict.
		"""
		Exception.__init__(self)
		self.what = what
		self.msg = msg or _("Biz error: ``%(what)s``" % dict(what=what))
		self.info = kwargs
		self.args = (self.msg,)


class RootError(BizError):
	def __init__(self, what, msg=None, **kwargs):
		BizError.__init__(self, what,
				msg or _("Root error: ``%(what)s``" % dict(what=what)),
				**kwargs)
		


class FileNotFoundError(RootError):
	def __init__(self, what, msg=None, **kwargs):
		RootError.__init__(self, what,
				msg or _("``%(what)s`` not found" % dict(what=what)),
				**kwargs)


class ImproperFileError(RootError):
	def __init__(self, what, msg=None, **kwargs):
		RootError.__init__(self, what,
				msg or _("The file ``%(what)s`` is not proper for this context" % \
						dict(what=what)),
				**kwargs)


class RootEnvironmentError(RootError):
	def __init__(self, what, msg=None, **kwargs):
		RootError.__init__(self, what,
				msg or _("Environment error: ``%(what)s``" % dict(what=what)),
				**kwargs)


class NoApplicationExistsError(ImproperFileError):
	def __init__(self, what, msg=None, **kwargs):
		ImproperFileError.__init__(self, what,
			msg or _("The given path/module ``%(what)s`` does not contain an application [source: ``%(source)s``]" \
						% dict(what=what, source=kwargs.get("source", _("UNKNOWN")))),
				**kwargs)


class ImproperConfigFileError(ImproperFileError):
	def __init__(self, what, msg=None, **kwargs):
		ImproperFileError.__init__(self, what,
				msg or _("The given file ``%(what)s`` is not a valid configuration file [source: ``%(source)s``]" \
						% dict(what=what, source=kwargs.get("source", _("UNKNOWN")))),
				**kwargs)


class ConfigFileNotFoundError(FileNotFoundError):
	def __init__(self, what, msg=None, **kwargs):
		FileNotFoundError.__init__(self, what,
				msg or _("Configuration file ``%(what)s`` not found [source: ``%(source)s``]" % \
				dict(what=what, source=kwargs.get("source", _("UNKNOWN")))),
				**kwargs)


class ModuleNotFoundError(FileNotFoundError):
	def __init__(self, what, msg=None, **kwargs):
		FileNotFoundError.__init__(self, what,
				msg or _("Module ``%(what)s`` not found [source: ``%(source)s``]" % \
				dict(what=what, source=kwargs.get("source", _("UNKNOWN")))),
				**kwargs)


class WSGIKeyNotPresentError(RootEnvironmentError):
	def __init__(self, what, msg=None, **kwargs):
		RootEnvironmentError.__init__(self, what,
				msg or _("WSGI key ``%(what)s`` not present in environ" % \
						dict(what=what)),
				**kwargs)


#class ApplicationNotFoundError(RootError):
#    def __init__(self, what, msg=None):
#        RootError.__init__(self)
#        self.what = what
#        self.msg = msg or _("Application: ``%s`` not found" % what)


class ApplicationNotFoundInModuleError(ImproperFileError):
	def __init__(self, what, msg=None, **kwargs):
		ImproperFileError.__init__(self, what,
			msg or _("Application ``%(what)s`` not found in ``%(where)s`` [source: ``%(source)s``]" % \
				dict(what=what, where=kwargs.get("where", _("UNKNOWN")),
					source=kwargs.get("source", _("UNKNOWN")))),
				**kwargs)


class HTTPError(Exception):
	def __init__(self, code, msg):
		Exception.__init__(self)
		self.code = code
		self.msg = msg
		self.args = (self.msg,)


class ApplicationError(BizError):
	def __init__(self, what, msg=None, **kwargs):
		BizError.__init__(self, what,
				msg or _("Application error: ``%(what)s``" % dict(what=what)),
				**kwargs)


class ApplicationStaticError(ApplicationError):
	def __init__(self, what, msg=None, **kwargs):
		ApplicationError.__init__(self, what,
				msg or _("Application static() error: ``%(what)s``" % dict(what=what)),
				**kwargs)
				

class ApplicationDynamicError(ApplicationError):
	def __init__(self, what, where="", msg=None, **kwargs):
		ApplicationError.__init__(self, what,
				msg or _("Application dynamic() error: ``%(what)s`` in ``%(where)s`` [source: ``%(source)s``]" % \
				dict(what=what, where=where, source=kwargs.get("source", _("UNKNOWN")))),
				**kwargs)
		