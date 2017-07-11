#!/usr/bin/python
# Title  : auto-compress-video.py
# Author : Alexander Jones
# Date   : 24-June-2017
# Usage  : auto-compress-video.py <root directory> <handbrake settings export (json)>
# Depen. : Python 2.7.10, ffprobe 3.1

import argparse
import os
import sys
import re
import math
import subprocess
import time

scriptVersion = "0.1a"

argumentParser = argparse.ArgumentParser(description='auto-compress-video.py version ' + scriptVersion)
argumentParser.add_argument('-rd',
							'-root-dir', 
							type=str,
							help='The root directory to search for media. Default is script root', 
							required=False, 
							default='.')
argumentParser.add_argument('-ib',
							'-ideal-bitrate', 
							type=float,
							help='The ideal bitrate that files should comply with (kbps). Default is 1000kbps',
							required=False,
							default=1000)
argumentParser.add_argument('-v',
							'-verbose',
							action='store_true',
							help='Verbose output of script',
							required=False)
argumentParser.add_argument('-l',
							'-log',
							type=str,
							nargs='?',
							help='Create a log file of output data. Add directory to argument to specify file location',
							required=False,
							default='NoLogging')
inputArguments = vars(argumentParser.parse_args())

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
	if ratio < 1:
		return '[' + '-' * int(round(ratio * 10)) + '|' + '-' * int(10 + (10 - round(ratio * 10))) + ']'
	elif ratio == 1:
		return '[' + '-' * 10 + '|' + '-' * 10 + ']'
	elif ratio > 1 and ratio < 2:
		return '[' + '-' * int(10 + round((ratio-1) * 10)) + '|' + '-' * int(10 - round((ratio-1) * 10)) + ']'
	elif ratio >= 2:
		return '[' + '-' * 20 + '|' + '-' * 0 + ']' 

print('-----------------------------------------------------------------')
print('-- auto-compress-video.py version ' + str(scriptVersion))
print('-----------------------------------------------------------------')

directoryRoot = inputArguments['rd']
verbose = inputArguments['v']

if inputArguments['l'] == 'NoLogging':
	logging = False
else:
	logging = True
	logFileName = 'acv-log_' + time.strftime('%Y%m%d_%H%M%S') + '.csv'
	if inputArguments['l'] == None: logFile = os.path.join('.', logFileName)
	else: logFile = os.path.join(inputArguments['l'], logFileName)

idealBitrate = inputArguments['ib']
idealHourlySize = sizeOf_readable(idealBitrate*1000/8*60*60)

print('-- Root Directory:  ' + os.path.abspath(directoryRoot))
if logging:
	logFileHandle = open(os.path.abspath(logFile), 'w')
	logFileHandle.write('Filename,Size,Duration,Bitrate,Ratio\r\n')
	print('-- Output log file: ' + os.path.abspath(logFile))
print('-- Ideal bitrate:   ' + str(idealBitrate) + 'kb/s (avg.) (' + str(idealHourlySize) + '/hr)')
numberOfBranches = 0
for root, subDirs, files in os.walk(directoryRoot):
	for fileN in files:
		numberOfBranches += 1
print('-- Total branches:  ' + str(numberOfBranches))
print('-- File list: ----------------------------------------------------')

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
			if verbose: print('\r\n' + fileName)
			fileSize = os.path.getsize(os.path.join(root, fileName))
			videoData = getVideoData_ffprobe(os.path.join(root,fileName))
			videoDataMatch = videoDataPattern.match(videoData)
			if videoDataMatch:
				videoFilesScanned += 1
				videoRatio = float(videoDataMatch.group(2))/idealBitrate
				if videoRatio > 1: videoFilesExceeding_1_0 += 1
				if videoRatio > 1.5: videoFilesExceeding_1_5 += 1
				if videoRatio > 2.0: videoFilesExceeding_2_0 += 1
				if logging: logFileHandle.write('"' + fileName + '",' + str(sizeOf_readable(fileSize)) + ',' + videoDataMatch.group(1) + ',' + videoDataMatch.group(2) + ',' + str(videoRatio) + '\r\n')
				if verbose: print('[' + str(sizeOf_readable(fileSize)) + '] [' + videoDataMatch.group(1) + '] [' + videoDataMatch.group(2) + 'kb/s]')
				if verbose: print('[' + str(videoRatio) + '] ' + txtRepresentRatio(videoRatio))
			else:
				ffprobeErrors += 1
				if logging: logFileHandle.write('"' + fileName + '",' + str(sizeOf_readable(fileSize)) + ', Error: ffprobe unable to find video data\r\n')
				if verbose: print('Error: ffprobe unable to find video data')
		print('\r-- Complete: ' + str(completionPerc) + '%'),

print('\r\n-- Branches scanned: ' + str(branchN))
print('-- Video files found: ' + str(videoFilesScanned))
print('-- ffprobe errors: ' + str(ffprobeErrors))
print('-- Files exceeding ratio 1.0: ' + str(videoFilesExceeding_1_0))
print('-- Files exceeding ratio 1.5: ' + str(videoFilesExceeding_1_5))
print('-- Files exceeding ratio 2.0: ' + str(videoFilesExceeding_2_0))
print('-----------------------------------------------------------------')

if logging: logFileHandle.close()
