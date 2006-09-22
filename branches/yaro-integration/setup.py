
# Biz setup script

import sys
import os
import os.path
from distutils.core import setup

import biz.default

scripts = ["bin/bizadmin", "bin/bizfiller", "bin/bizcatalog"]

if "--install-script" in sys.argv:
	scripts.append("bin/biz-postinstall.py")

setup(name="biz",
		version="0.0.43",
		url="http://biz.berlios.de",
		download_url="http://developer.berlios.de/project/showfiles.php?group_id=6616",
		author="Yuce Tekol",
		author_email="yucetekol@gmail.com",
		description="A web application framework that focuses on reusable applications",
		license="GPL",
		packages=["biz", "biz.apps", "biz.apps.vfolder", "biz.coms", "biz.default", "biz.handlers"],
		scripts=scripts,
		)
