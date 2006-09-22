# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser


class BizIniManager:
	def __init__(self, filename="biz.ini"):
		cfg = SafeConfigParser()
		cfg.read(filename)
		
		apps = {}
		for app, cfgfilename in cfg.items("applications"):
			appd = dict(cfgfilename=cfgfilename)
			c = SafeConfigParser()
			c.read(cfgfilename)
			for k, v in c.items("main"):
				appd[k] = v
			
			apps[app] = appd			
		self.apps = apps
		
		self.root = dict(cfg.items("root"))
		
	def update(self):
		pass

		
	
