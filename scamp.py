#!/usr/bin/env python

import sys
import subprocess

arguments = sys.argv[1:]

print arguments

for x in arguments:
	print x
	subprocess.call("python ./download.py "+x, shell=True)
