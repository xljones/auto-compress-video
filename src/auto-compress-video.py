#!/usr/bin/python
# Title  : auto-compress-video.py
# Author : Alexander Jones
# Date   : 24-June-2017
# Usage  : auto-compress-video.py <root directory> <handbrake settings export (json)>
# Depen. : Python 2.7.10, ffprobe 3.1, HandbrakeCLI 1.0.7

import os
import sys
import re
import math
import subprocess
import time

scriptVersion = '1.0'			# script version
handbrakeBIn = 'HandbrakeCLI'	# handbrake command line tool binary

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

print('Auto-Compress Video V' + str(scriptVersion))

if (len(sys.argv[1:]) <= 0):
	print('Drop a folder onto this app to scan and compress')
else:
	directoryRoot = sys.argv[1]
	logging = True
	idealBitrate = 1000
	idealHourlySize = sizeOf_readable(idealBitrate*1000/8*60*60)
	logFileName = 'acv-log-' + time.strftime('%Y%m%d-%H%M%S') + '.csv'
	logFilePath = os.path.join('../../..', logFileName)

	logFileHandle = open(os.path.abspath(logFilePath), 'w')
	logFileHandle.write('Filename,Size,Duration,Bitrate,Ratio\r\n')
	print('Output log file: ' + os.path.abspath(logFilePath))
	print('Root Directory:  ' + os.path.abspath(directoryRoot))
	print('Ideal bitrate:   ' + str(idealBitrate) + 'kb/s (avg.) (' + str(idealHourlySize) + '/hr)')
	numberOfBranches = 0
	for root, subDirs, files in os.walk(directoryRoot):
		for fileN in files:
			numberOfBranches += 1
	print('Total branches:  ' + str(numberOfBranches))

	searchPattern = re.compile('.*(\.avi|\.mkv|\.mp4|\.m4v)$')
	videoDataPattern = re.compile('.*Duration: (.*), start:.*, bitrate: (\d*)')

	branchN = 0
	ffprobeErrors = 0
	videoFilesScanned = 0
	videoFilesExceeding_1_0 = 0
	videoFilesExceeding_1_5 = 0
	videoFilesExceeding_2_0 = 0

	for root, subDirs, files in os.walk(directoryRoot):
		for fileName in files:
			branchN += 1
			completionPerc = round(float(branchN) / float(numberOfBranches) * 100, 2)
			if searchPattern.match(fileName):
				print('Scanning: ' + fileName)
				fileSize = os.path.getsize(os.path.join(root, fileName))
				videoData = getVideoData_ffprobe(os.path.join(root,fileName))
				videoDataMatch = videoDataPattern.match(videoData)
				if videoDataMatch:
					videoFilesScanned += 1
					videoRatio = float(videoDataMatch.group(2))/idealBitrate
					if videoRatio > 1: videoFilesExceeding_1_0 += 1
					if videoRatio > 1.5: videoFilesExceeding_1_5 += 1
					if videoRatio > 2.0: videoFilesExceeding_2_0 += 1
					logFileHandle.write('"' + fileName + '",' + str(sizeOf_readable(fileSize)) + ',' + videoDataMatch.group(1) + ',' + videoDataMatch.group(2) + ',' + str(videoRatio) + '\r\n')
				else:
					ffprobeErrors += 1
					logFileHandle.write('"' + fileName + '",' + str(sizeOf_readable(fileSize)) + ', Error: ffprobe unable to find video data\r\n')
					print('Error: ffprobe unable to find video data')
			print('PROGRESS:' + str(completionPerc))

	print('Branches scanned: ' + str(branchN))
	print('Video files found: ' + str(videoFilesScanned) + ' (ffprobe errors: ' + str(ffprobeErrors) + ')')
	print('Files exceeding ratio 1.0: ' + str(videoFilesExceeding_1_0))
	print('Files exceeding ratio 1.5: ' + str(videoFilesExceeding_1_5))
	print('Files exceeding ratio 2.0: ' + str(videoFilesExceeding_2_0))

	logFileHandle.close()
