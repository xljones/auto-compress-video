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

scriptVersion = 0.1

argumentParser = argparse.ArgumentParser(description='auto-compress-video.py version ' + str(scriptVersion))
argumentParser.add_argument('-r',
							 '-root-dir', 
							 type=str,
							 help='The root directory to search for media. Default is script root', 
							 required=False, 
							 default='.')
argumentParser.add_argument('-i',
							'-ideal-bitrate', 
							type=float,
							help='The ideal bitrate that files should comply with (kbps). Default is 1000kbps',
							required=False,
							default=1000)
argumentParser.add_argument('-v',
							'-verbose',
							nargs='?',
							type=bool,
							help='Verbose output of script',
							required=False,
							default=False)
argumentParser.add_argument('-l',
							'-log',
							type=str,
							help='Save results to log file at root of script (optionally include location in this argument)',
							required=False,
							default=False)
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

directoryRoot = inputArguments['r']
verbose = inputArguments['v']
print verbose
idealBitrate = inputArguments['i']
idealHourlySize = (((idealBitrate*1000*60*60)/8)/1024)/1024

numberOfBranches = 0
for root, subDirs, files in os.walk(directoryRoot):
	for fileN in files:
		numberOfBranches += 1

print('-- Root Directory:     ' + os.path.abspath(directoryRoot))
print('-- Ideal bitrate:      ' + str(idealBitrate) + 'kb/s (avg.) (' + str(idealHourlySize) + 'MB/hr)')
print('-- Total branches:     ' + str(numberOfBranches))
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
				if verbose: print('[' + str(sizeOf_readable(fileSize)) + '] [' + videoDataMatch.group(1) + '] [' + videoDataMatch.group(2) + 'kb/s]')
				if verbose: print('[' + str(videoRatio) + '] ' + txtRepresentRatio(videoRatio))
			else:
				ffprobeErrors += 1
				if verbose: print('Error: ffprobe unable to find video data')
		print('\rComplete: ' + str(completionPerc) + '%'),

print('\r\n-- Branches scanned: ' + str(branchN))
print('-- Video files found: ' + str(videoFilesScanned))
print('-- ffprobe errors: ' + str(ffprobeErrors))
print('-- Files exceeding ratio 1.0: ' + str(videoFilesExceeding_1_0))
print('-- Files exceeding ratio 1.5: ' + str(videoFilesExceeding_1_5))
print('-- Files exceeding ratio 2.0: ' + str(videoFilesExceeding_2_0))
print('-----------------------------------------------------------------')

