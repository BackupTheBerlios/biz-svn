
# Biz post-install script for Win32

import sys
import os.path

def main():
	if sys.argv[1] == "-install":
		pythonloc = os.path.join(sys.prefix, "python.exe")
		scriptsdir = os.path.join(sys.prefix, "Scripts")
		scripts = ["bizadmin", "bizfiller"]
		for script in scripts:
			loc = os.path.join(scriptsdir, script)
			batloc = "%s.bat" % loc
			
			try:
				f = file(batloc, "w")
				print>>f, '@echo off\n"%s" "%s" %%*' % (pythonloc,loc)
				f.close()
				file_created(batloc)
			except IOError, e:
				print e
			
if __name__ == "__main__":
	main()

	

