# -*- coding: utf-8 -*-

import biz
from biz.template import Template
from biz.catalog import LanguageCatalog
from biz.userman import UserManager


class Login(biz.Application):
	@staticmethod
	def set_language(r, lcon):
		lang = r.env.get("HTTP_ACCEPT_LANGUAGE", ",").split(",", 1)[0][:2]
		lcon.set_language(lang)
		
	def static(self):
		q = self.q
		q.template = Template.open(q.options["template"])
		q.users_db_filename = q.options["users_db"]
		q.login_ok = Template.open(q.options["login_ok"])
		q.login_deny = Template.open(q.options["login_deny"])
		
		langs = [x.strip() for x in q.options["languages"].split(",")]
		locale_dir = q.options["locale_dir"]
		default_lang = q.options["default_language"]
		q.lc = LanguageCatalog.open(locale_dir, langs, lang=default_lang)
		q.set_language = self.set_language
		
	class Handler(biz.ArgHandler):
		def dynamic(self):
			q = self.q; r = self.r
			lcon = q.lc.get_context()
			q.set_language(r, lcon)
			
			template = q.template.copy()
			template["scriptname"] = q.scriptname
			template["appname"] = q.appname
			template["N_"] = lcon.get_noop_translator()
			
			r.content = biz.HtmlContent(template.render())
			
	class checkHandler(biz.ArgHandler):
		def dynamic(self):
			q = self.q; r = self.r
			lcon = q.lc.get_context()
			q.set_language(r, lcon)
			
			try:
				userman = UserManager(q.users_db_filename)
				username = r.fields.get("username")
				password = r.fields.get("password", "")
				login_ok = userman.check(username, password)
				if login_ok:
					template = q.login_ok.copy()
					r.session.username = username
					r.session.groups = userman.groups(username)
				else:
					template = q.login_deny.copy()
					
			except (KeyError,TypeError):
				template = q.login_deny.copy()
				
			template["N_"] = lcon.get_noop_translator()
			userman.close()			
			r.content = biz.HtmlContent(template.render())
				

def load(x):
	return Login(x)
