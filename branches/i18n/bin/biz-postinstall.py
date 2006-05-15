
# Biz Postinstall script for Win32

import sys
import os.path

def main():
	if sys.argv[1] == "-install":
		scriptsdir = os.path.join(sys.prefix, "Scripts")
		bizadminloc = os.path.join(scriptsdir, "bizadmin")
		bizadminbatloc = bizadminloc + ".bat"
		pythonloc = os.path.join(sys.prefix, "python.exe")
		try:
			f = file(bizadminbatloc, "w")
			print>>f, '@echo off\n"%s" "%s" %%*' % (pythonloc,bizadminloc)
			f.close()
			file_created(bizadminbatloc)
		except IOError:
			print "bizadminloc.bat not saved"
			
if __name__ == "__main__":
	main()

	

