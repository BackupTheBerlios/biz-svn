
import sys
import os
import os.path
from zipfile import ZipFile, ZIP_DEFLATED
from cStringIO import StringIO
import re
from base64 import b64encode, b64decode

excluded_files = re.compile(r".*(.swp|.bak|~)$")

# XXX
remove_firstdir = re.compile(r"^[^/\\]+[/|\\](.*)")

def _pack(dirname, callback=None):
	"""pack the files under ``dirname`` and write as base64ed string
	to ``packed.py``

	* callback is a function of prototype function(origpath, newpath).
	It is called before attempting to compress the file.
	"""

	# get the files under dirname
	filelist = []
	for root, dirs, files in os.walk(dirname):
		filelist.extend([os.path.join(root, f) for f in files
				if f and not excluded_files.match(f)])

		if ".svn" in dirs:
			dirs.remove(".svn")

	fakefile = StringIO()
	zipf = ZipFile(fakefile, "w", ZIP_DEFLATED)

	for f in filelist:
		origpath = f
		newpath = remove_firstdir.search(f).group(1)

		if callback:
			callback(origpath, newpath)

		zipf.write(origpath, newpath)

	zipf.close()

	out = file(os.path.join(os.path.dirname(__file__), "packed.py"), "w")
	print>>out, "packed_default ='%s'" % b64encode(fakefile.getvalue())
	fakefile.close()
	out.close()

def unpack(dirname, callback=None):
	"""unpack the files in ``packed.py`` and decompress under ``dirname``

	* callback is a function of prototype function(path).
	It is called before attempting to compress the file.
	"""
	from biz.default.packed import packed_default

	fakefile = StringIO(b64decode(packed_default))
	zipf = ZipFile(fakefile, "r")

	for name in zipf.namelist():
		try:
			os.makedirs(os.path.join(dirname, os.path.dirname(name)), 0700)
		except OSError:
			pass

		data = zipf.read(name)
		filename = os.path.join(dirname, name)

		if callback:
			callback(filename)

		f = file(filename, "wb")
		f.write(data)
		f.close()

	zipf.close()
	fakefile.close()

