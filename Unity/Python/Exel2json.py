import xlrd
import json
import codecs
import os

fileList = ['ssWeaponAndProjectile.xlsx']

class SheetData :
	def __init__(self, sheetName):
		self.sheetName = sheetName
		self.dataNames = []
		self.data = []
		self.columnCount = 0
		self.dataCount = 0
		
	def addDataNames(self, *values) :
		for v in values :
			self.dataNames.append(v)
			self.columnCount += 1
			
	def addDataNamesWithList(self, lst) :
		if type(lst) is list :
			self.columnCount = len(lst)
			self.dataNames.extend(lst)
		else :
			print "SheetData::addDataNamesWithList() => wrong parameter."
		
	def addData(self, *values) :
		tempData = []
		cnt = 0
		
		for v in values :
			teampData.append(v)
			cnt += 1
			if cnt > self.columnCount :
				break
			
		self.appendListData(tempData)
		self.dataCount += 1
		
	def addDataWithList(self, lst) :
		if type(lst) is list : 
			lstLength = len(lst)
			if lstLength > self.columnCount :
				for idx in range(self.columnCount, lstLength) :
					lst.remove(lst[idx])
			self.appendListData(lst)
			self.dataCount += 1
		else : 
			print "SheetData::addDataWithList() => wrong parameter."
			
	def appendListData(self, lst) :
		dic = dict()
		try :
			for idx in range(self.columnCount) :
				dic[self.dataNames[idx]] = lst[idx]
		except :
			print "SheetData::appendListData() => wrong data."
			return
		self.data.append(dic)
		

class JsonData :
	def __init__(self, filename) :
		self.filename = filename
		self.data = []
		self.count = 0
		
	def addSheetData(self, data) :
		if isinstance(data, SheetData) :
			self.data.append(data)
			self.count += 1
		else :
			print "JsonData::addSheetData() => wrong parameter."
			
	def getData(self) : 
		dic = {}
		for sheet in self.data :
			dic[sheet.sheetName] = sheet.data
		return dic
			
		
		
def uniqueArray(data) :
	tempList = list()
	cnt = 0
	for s in data : 
		if s in tempList :
			print "duplicated : ", s, "(", xlrd.cellname(0,cnt), ")"
			return False
		else :
			tempList.append(s)
		cnt += 1
	return True
		
		
for fileNum in range(len(fileList)) : 
	workbook = xlrd.open_workbook(fileList[fileNum])
	sheetNameList = workbook.sheet_names()
	jsonFilename = os.path.splitext(fileList[fileNum])[0] + '.json'
	jsonData = JsonData(jsonFilename)

	for sheetName in sheetNameList :
		print "Read sheet : ", sheetName
		workSheet = workbook.sheet_by_name(sheetName)
		try :
			rowVal = workSheet.row_values(0)
		except :
			print "Can't read a sheet : ", sheetName
			continue
			
		if len(rowVal) == 0 :
			print "nodata"
			continue
		
		if uniqueArray(rowVal) == False :
			print "Data column name error."
			break
			
		isNotData = False
		removeList = list()
		for rval in rowVal :
			if isNotData == False :
				if rval == '' :
					isNotData = True
					removeList.append(rval)
			else :
				removeList.append(rval)
				
		for removeVal in removeList :
			rowVal.remove(removeVal)

		colCnt = len(rowVal)
		rowCnt = workSheet.nrows
		
		sheetData = SheetData(sheetName)
		sheetData.addDataNamesWithList(rowVal)
		
		if rowCnt > 1 :
			for rowIndex in range(1, rowCnt) :
				singleData = workSheet.row_values(rowIndex)
				sheetData.addDataWithList(singleData)
			
		jsonData.addSheetData(sheetData)
		print "Done."
		
	js = json.dumps(jsonData.getData(), sort_keys = True, indent = 4, ensure_ascii=False)
	print js

	outfile = codecs.open(jsonData.filename, 'w', 'utf-8')
	outfile.write(js)


	
	