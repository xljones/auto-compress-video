#!/usr/bin/python
import os
import sys
import re
import math
import subprocess
import time

conversionComplete = False
fileName = '/Users/Alex/Downloads/Transmission/MythBusters/Season 07 - 2009/MythBusters S07E18 Myth Evolution 2.avi'
#conversion = subprocess.Popen(['./HandBrakeCLI', '-z'], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
conversion = subprocess.Popen(['./HandBrakeCLI', '--preset-import-file', './plex-default.json', '-i', fileName, '-o', fileName + '-compressed.mkv'], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

print('SUBPROCESS STARTED-------')
#print ('\r' + str(loop) + ':' + str(len(conversion.communicate()[0])))
output = ''

# Poll process for new output until finished
for line in iter(conversion.stdout.readline, ""):
	print line,
	output += line

	conversion.wait()
	exitCode = conversion.returncode

	if (exitCode == 0):
		print output
	else:
		raise Exception(command, exitCode, output)

print('SUBPROCESS ENDED-------')
