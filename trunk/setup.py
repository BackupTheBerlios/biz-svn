
# Biz setup script

import sys
import os
import os.path
from distutils.core import setup

import biz.default

# TODO: poor man's i18n :)
def _(s):
	return s

scripts = ["bin/bizadmin"]

def pack():
	def callback(origpath, newpath):
		print _("Packing: %(origpath)s -> %(newpath)s" % \
				dict(origpath=origpath, newpath=newpath))

	biz.default._pack("default", callback)

if "--install-script" in sys.argv:
	scripts.append("bin/biz-postinstall.py")

if not (("build" in sys.argv) or ("install" in sys.argv)):
	pack()

setup(name="Biz",
		version="0.0.3",
		url="http://biz.berlios.de",
		download_url="http://developer.berlios.de/project/showfiles.php?group_id=6616",
		author="Yuce Tekol, Gulhan Yener",
		author_email="yucetekol@gmail.com",
		description="A web application framework that focuses on reusable applications",
		license="GPL",
		packages=["biz", "biz.apps", "biz.apps.vfolder", "biz.coms", "biz.default"],
		scripts=scripts,
		)
