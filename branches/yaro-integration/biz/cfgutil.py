# -*- coding: utf-8 -*-

import os.path
from ConfigParser import SafeConfigParser


class BizIniManager:
    def __init__(self, filename="biz.ini"):
        path = os.path.dirname(filename)
        cfg = SafeConfigParser()
        cfg.read(filename)
        
        apps = {}
        for app, cfgfilename in cfg.items("applications"):
            cfgfilename = path and "/".join([path, cfgfilename]) or cfgfilename
            appd = dict(cfgfilename=cfgfilename)
            c = SafeConfigParser()
            c.read(cfgfilename)
            for k, v in c.items("main"):
                # This is a quick hack to make app point to the correct
                # ... module everyime.
                # TODO: make it prettier
                if k == "path":
                    v = path and "/".join([path, v]) or v
                appd[k] = v
            
            apps[app] = appd            
        self.apps = apps
        
        self.root = dict(cfg.items("root"))
        
    def update(self):
        pass

        
    
