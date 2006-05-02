#! /usr/bin/env python
# runbiz.py

import biz.server
from biz.root import Root

root = Root.configure("biz.ini")
biz.server.run(root)

