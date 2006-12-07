import os
import imp
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
import threading

from biz.errors import *
from biz.utility import Struct

applist_lock = threading.Lock()


class ApplicationInfo(object):
    __slots__ = ("name","mpath","cpath","body","module","class_","options")

    def __init__(self, name, options):
        self.name = name
        self.mpath = None
        self.module = None
        self.body = None
        self.class_ = None
        self.options = options

    def _reload_options(self):
        options = self.options
        
        self.module = options.get("module", None)
        self.mpath = options.get("path", "")
        self.class_ = options.get("class", "")
        self.cpath = options.get("cfgfilename", "")
        
        # module and path options are mutually exclusive
        if not(bool(self.module) ^ bool(self.mpath)):
            raise ImproperConfigFileError(what=self.cpath)                  

        return options

    def _reload(self, environ):
        environ["biz.options"] = self._reload_options()

        # app is standard
        if self.module:
            # class of the app is given
            if self.class_:
                try:
                    m = __import__(self.module, None, None, [self.class_])
                except ImportError, e:
                    raise ModuleNotFoundError(self.module, msg=e, source=self.cpath)
                    
                try:
                    # create the application
                    body = getattr(m, self.class_)
                except AttributeError, e:
                    raise ApplicationNotFoundInModuleError(self.class_, msg=e,
                            where=self.module, source=self.cpath)
                            
                self.body = body(environ)
            else:
                # a load function should be present in the module
                try:
                    m = __import__(self.module, None, None, ["load"])
                except ImportError, e:
                    raise ModuleNotFoundError(self.module, msg=e, source=self.cpath)
                    
                try:
                    load = m.load
                except AttributeError, e:
                    raise NoApplicationExistsError(self.module, msg=e, source=self.cpath)
                
                self.body = load(environ)

        else:
            # the location of the app is given by ``path`` option
            path, modname = os.path.split(self.mpath)
            modname = modname.split(".py")[0]
            m = imp.load_module(modname, \
                    *imp.find_module(modname, [path]))

            if self.class_:
                try:
                    self.body = m.__getattribute__(self.class_)(environ)
                except AttributeError, e:
                    # XXX: this is also raised on AttributeError in app's constructor
                    raise ApplicationNotFoundInModuleError(self.class_,
                        where=self.mpath, source="root", msg=e)
            else:
                try:
                    load = m.load
                except AttributeError, e:
                    # XXX: this is also raised on AttributeError in app's constructor
                    raise NoApplicationExistsError()  #path, source=self.cpath, msg=e)
                
                self.body = load(environ)

    # XXX: Not used right now
    def unload(self):
        self.body = None

    def __call__(self, environ):
        # if body is not loaded/not recent, load/reload it
        if not self.body:
            try:
                applist_lock.acquire()
                self._reload(environ)
            finally:
                applist_lock.release()

        return self.body
        
