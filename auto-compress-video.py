#!/usr/bin/python
# Title  : auto-compress-video.py
# Author : Alexander L. Jones
# Date   : 24-June-2017
# Usage  : auto-compress-video.py <root directory> <handbrake settings export (json)>
# Depen. : Python 2.7.10, ffprobe 3.1

import argparse
import os
import sys
import re
import math
import subprocess

def getVideoData_ffprobe(fileName):
	# Based on: https://stackoverflow.com/questions/3844430/
	result = subprocess.Popen(["./ffprobe", fileName], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	buildList = [x for x in result.stdout.readlines() if "Duration" in x]
	if len(buildList) > 0:
		return buildList[0]
	else:
		return ''
def sizeOf_readable(numBytes, suffix='B'):
	# Based on: https://stackoverflow.com/questions/1094841
	for unit in ['','K','M','G','T','P','E','Z']:
		if abs(numBytes) < 1024.0:
			return '%3.1f%s%s' % (numBytes, unit, suffix)
		numBytes /= 1024.0
	return '%.1f%s%s' % (numBytes, 'Y', suffix)
def txtRepresentRatio(ratio):
	if (ratio < 1):
		return '[' + '-' * int(round(ratio * 10)) + '|' + '-' * int(10 + (10 - round(ratio * 10))) + ']'
	elif ratio == 1:
		return '[' + '-' * 10 + '|' + '-' * 10 + ']'
	elif ratio > 1 and ratio < 2:
		return '[' + '-' * int(10 + round((ratio-1) * 10)) + '|' + '-' * int(10 - round((ratio-1) * 10)) + ']'
	elif ratio >= 2:
		return '[' + '-' * 20 + '|' + '-' * 0 + ']' 

scriptVersion = 0.1
print('-----------------------------------------------------------------')
print('-- auto-compress-video.py version ' + str(scriptVersion))
print('-----------------------------------------------------------------')
print('-- Generating number of branches to search...'),

if len(sys.argv) < 3:
	print('Error: missing arguments.')
	print('Usage: auto-compress-video.py <root directory> <handbrake settings export>')
else:
	directoryRoot = sys.argv[1]			# The root directory to browse through.
	handbrakeSettings = sys.argv[2]		# The handbrake settings export file, commonly in .json format.
	idealBitrate = 800					# Compression rate to baseline is 800kbps.
	idealHourlySize = (((idealBitrate*1000*60*60)/8)/1024)/1024
	numberOfBranches = 0

	for root, subDirs, files in os.walk(directoryRoot):
		for fileN in files:
			numberOfBranches += 1

	print('\r-- Root Directory:     ' + os.path.abspath(directoryRoot))
	print('-- Handbrake Settings: ' + os.path.abspath(handbrakeSettings))
	print('-- Ideal bitrate:      ' + str(idealBitrate) + 'kb/s (avg.) (' + str(idealHourlySize) + 'MB/hr)')
	print('-- File list: ----------------------------------------------------')
	print('-- Total files:        ' + str(numberOfBranches))

	searchPattern = re.compile('.*(\.avi|\.mkv|\.mp4|\.m4v)$')
	videoDataPattern = re.compile('.*Duration: (.*), start:.*, bitrate: (\d*)')
	branchN = 0
	for root, subDirs, files in os.walk(directoryRoot):
		for fileName in files:
			branchN += 1
			completionPerc = round(float(branchN) / float(numberOfBranches) * 100,2)
			if searchPattern.match(fileName):
				print('\r\n' + fileName)
				fileSize = os.path.getsize(os.path.join(root, fileName))
				videoData = getVideoData_ffprobe(os.path.join(root,fileName))
				videoDataMatch = videoDataPattern.match(videoData)
				if videoDataMatch:
					videoRatio = float(videoDataMatch.group(2))/idealBitrate
					print('[' + str(sizeOf_readable(fileSize)) + '] [' + videoDataMatch.group(1) + '] [' + videoDataMatch.group(2) + 'kb/s]')
					print('[' + str(videoRatio) + '] ' + txtRepresentRatio(videoRatio))
				else:
					print('Error: ffprobe unable to find video data')
			print('Complete: ' + str(completionPerc) + '%')

print('-----------------------------------------------------------------')

