#! python
# fuzz from fuzzdb (or other file) to the 

import xlsxwriter
import random
import uuid
import datetime
import json
import argparse


class XlsxFuzzer(object):

	def __init__(self, numCols=0, fuzzFile=None, outFile='./test.xlsx', mappingFile=None):
		self.numCols = numCols
		self.fuzzFile = fuzzFile
		self.outFile = outFile
		# the mapping is a nested dictionary for specifying column formats
		# it has the following format:
		# { [coNum] : { 'type' : [type], 'format': [format], 'val': [value]}}
		if mappingFile:
			self.mapping = self.readMappingFile(mappingFile)
		else:
			# self.mapping = self.createDefaultMap()
			# default to empty
			self.mapping = {}

	def readFuzzFile(self):
		#read the fuzz file into an array
		lines = {'1', "a'--", '<img src=x onerror=alert(4321)>'} # return something basic if no file specified.
		if self.fuzzFile:
			lines = [line.strip('\n') for line in open(self.fuzzFile)] # strip newlines
		return lines
	
	def readMappingFile(self, mapFile):
		f=open(mapFile,'r')
		map = json.loads(f.read())
		f.close()
		return map
	
	def createDefaultMap(self):
		map = {}
		item = { 'type' : 'int', 'format' : 'sequential' }
		map['0'] = item
		item = { 'type' : 'int', 'format' : 'rand', 'val' : 100 }
		map['1'] = item
		item = { 'type' : 'int', 'format' : 'unique', 'val' : 100 }
		map['2'] = item
		item = { 'type' : 'date', 'format' : '%b %d %Y %H:%M:%S' }
		map['3'] = item
		item = { 'type' : 'date', 'format' : '%b %d %Y %H:%M:%S', 'val' : 'Feb 18 2009 00:03:38' }
		map['4'] = item
		item = { 'type' : 'string', 'format' : 'unique' }
		map['5'] = item
		item = { 'type' : 'string', 'format' : 'unique', 'val' : 'This is a test string' }
		map['6'] = item
		item = { 'type' : 'string', 'format' : 'append', 'val' : '@optiv.com' }
		map['7'] = item
		return map
	
	def writeMap(self, map, outFile):
		f=open(outFile,'w')
		newData = json.dumps(map, sort_keys=True, indent=4)
		f.write(newData)
		f.close()
		

	def fuzzLine(self, lineNum, fuzzText, worksheet):
		#worksheet.write(lineNum, 0, str(lineNum+1))
		for x in range(0, self.numCols):
			worksheet.write(lineNum, x, self.getMappedVal(lineNum, x, fuzzText)) #default to fuzzText but override with mapping
	
	def getMappedVal(self,lineNum, colNum, default):
		retval = default
		map = self.mapping.get(str(colNum), None)
		if map:
			type = map.get('type', None)
			if type == 'int':
				#valid are 'rand', 'unique' or use the default assignment. If 'rand', multiply by 'val'
				format = map.get('format', None)
				if format == 'rand':
					mult = map.get('val', 100)
					retval = int(random.random() * mult)
				elif format == 'unique':
					retval = uuid.uuid4().int
				elif format == 'sequential':
					# use the provided line number
					retval = int(lineNum)
			elif type == 'date':
				#if type is date, format is the format string for current date/time. If val exists, it will override and be used.
				format = map.get('format', None)
				val = map.get('val', None)
				
				if format:
					retval = datetime.datetime.now().strftime(format)
				elif val:
					retval = val
			elif type == 'string':
				format = map.get('format', None)
				val = map.get('val', None)
				if 'unique' in format:
					retval = str(uuid.uuid4())
				if 'append' in format:
					retval = retval + val
				elif val:
					retval=val
		return retval
		
	def buildFuzzedSpreadsheet(self):
		fuzzList = self.readFuzzFile()

		wb = xlsxwriter.Workbook(self.outFile)
		ws = wb.add_worksheet()
		x = 0
		for fuzz in fuzzList:
			self.fuzzLine(x, fuzz, ws)
			x = x+1
		
		wb.close()

if __name__ == "__main__":
    import sys
    # command line parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--columns", type=int, help="number of columns to create")
    parser.add_argument("-f", "--fuzz_file", help="file with fuzzing data")
    parser.add_argument("-o", "--out_file", help="output file")
    parser.add_argument("-m", "--map_file", help="file containing column mapping data")
    parser.add_argument("-d", "--default", action="store_true", help="creat a default map file")
    args = parser.parse_args()
    
    cols = args.columns if args.columns else 10 #default to 10 columns
    fuzz = args.fuzz_file if args.fuzz_file else None
    out = args.out_file if args.out_file else './outfile.xlsx'
    map = args.map_file if args.map_file else None
    default = True if args.default else False
    
    fuzz = XlsxFuzzer(cols, fuzz, out, map)
    
    if default:
    	print('writing default map file')
    	fuzz.writeMap(fuzz.createDefaultMap(), './sample_map.txt')
    else:
    	print('building spreadsheet')
    	fuzz.buildFuzzedSpreadsheet()
