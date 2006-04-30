# bizadmin.py

import sys
import os
import os.path
import shutil
from optparse import OptionParser

__version__ = "0.0.1"


def admin_create(options, args):
	if len(args) < 1:
		return False

	for arg in args:
		destination = os.path.join(os.getcwd(), arg)

		python_ver = sys.version_info
		python_ver = "python%d.%d" % (python_ver[0],python_ver[1])
		platform = sys.platform

		if options.prefix:
			prefix = options.prefix
		else:
			if platform.startswith("linux"):
				prefix = os.path.join(sys.prefix, "lib", python_ver, "site-packages", "biz")
			else:
				print "%s is not supported." % platform
				return True

		source = os.path.join(prefix, "default")
		shutil.copytree(source, destination)

		return True

def main():
	router = dict(create=admin_create)
	opt = OptionParser(usage="%prog [options] command [project_name]",
			version=__version__)
	opt.add_option("-p", "--prefix", dest="prefix", default=None,
			help="Change source prefix")

	options, args = opt.parse_args()

	try:
		result = router[args[0]](options, args[1:])
	except (KeyError, IndexError):
		opt.print_help()
	else:
		if not result:
			opt.print_help()

if __name__ == "__main__":
	main()

	
