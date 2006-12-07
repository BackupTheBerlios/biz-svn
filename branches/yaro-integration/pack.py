#! /usr/bin/env python
# Biz default project packer
import biz.default

def _(s): return s

def pack():
	def callback(origpath, newpath):
		print _("Packing: %(origpath)s -> %(newpath)s" % \
				dict(origpath=origpath, newpath=newpath))

	biz.default._pack("default", callback)

if __name__ == "__main__":
	pack()
