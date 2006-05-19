# cgirun -- Run Biz root in a CGI script
# Note that, this is extremely inefficient; (more than 10x slower)

import os
import sys
import biz
from biz.handlers import CGIHandler

def run(configfilename):
	root = biz.Root.configure(configfilename)
	root.meltscriptname = True
	CGIHandler().run(root)
