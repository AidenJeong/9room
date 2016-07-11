import xlrd
import json
import codecs
import os

# 읽어들일 엑셀 파일 리스트
# 'ssWeaponAndProjectile.xlsx', 'ssCharacter.xlsx', 'ssEnemy.xlsx', 
fileList = ['ssDataStage.xlsx']

class SheetData :
	def __init__(self, sheetName):
		self.sheetName = sheetName
		
		# 데이터 키셋
		# 엑셀 시트에 첫번째 행의 내용들이 각각 데이터의 키로 저장됨.
		self.dataNames = []
		
		# 실제 데이터들
		self.data = {}
		
		self.columnCount = 0
		self.dataCount = 0
		
	def addDataNames(self, *values) :
		lst = []
		for v in values :
			lst.append(v)
		self.addDataNamesWithList(lst)
			
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
			if lst[0] == '' :
				print "It's not data row."
				return
			lstLength = len(lst)
			if lstLength > self.columnCount :
				tmp = []
				for idx in range(0, self.columnCount) :
					tmp.append(lst[idx])
				lst = tmp
			self.appendListData(lst)
			self.dataCount += 1
		else : 
			print "SheetData::addDataWithList() => wrong parameter."
			
	def appendListData(self, lst) :
		# Json 데이터로 파싱하기 편리하도록
		# 데이터를 추가할때 데이터키와 함께 딕셔너리로 저장시킨다.
		# 데이터에 오류가 있으면 예외발생
		dic = dict()
		try :
			for idx in range(self.columnCount) :
				dic[self.dataNames[idx]] = lst[idx]
		except :
			print "SheetData::appendListData() => wrong data."
			print "Sheet name : ", self.sheetName
			return
			
		# 엑셀 시트의 첫번째 열에 해당하는 데이터를 키값으로 갖는 딕셔너리 생성
		self.data[dic[self.dataNames[0]]] = dic
		

		
class ExcelData :
	def __init__(self, filename) :
		self.jsonFileName = filename
		self.data = []
		self.count = 0
		
	def addSheetData(self, data) :
		if isinstance(data, SheetData) :
			self.data.append(data)
			self.count += 1
		else :
			print "JsonData::addSheetData() => wrong parameter."
			
	def getDataWithDict(self) : 
		dic = {}
		for sheet in self.data :
			dic[sheet.sheetName] = sheet.data
		return dic
			
		
		
def uniqueArray(data) :
	# 데이터 키들의 중복여부를 채크하고
	# 중복이 있을경우 중복이 되는 키 이름과 그 키가 들어있는 엑셀 셀의 위치를 출력.
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
		
	
def main() :	
	for fileNum in range(len(fileList)) : 
		workbook = xlrd.open_workbook(fileList[fileNum])
		sheetNameList = workbook.sheet_names()
		jsonFilename = os.path.splitext(fileList[fileNum])[0] + '.json'
		excelData = ExcelData(jsonFilename)

		for sheetName in sheetNameList :
			print "Read sheet : ", sheetName
			workSheet = workbook.sheet_by_name(sheetName)
			try :
				# 시트의 내용이 전혀 없으면 예외발생
				rowVal = workSheet.row_values(0)
			except :
				print "Can't read a sheet : ", sheetName
				continue
				
			# 엑셀 시트의 A1 셀이 비어있으면 데이터 시트로 간주하지 않는다.
			if len(rowVal) == 0 :
				print "nodata"
				continue
	
			# 데이터 셀 중간에 비어있는 셀이 있으면
			# 그 셀부터 뒷쪽셀은 데이터로 간주하지 않고 스킵한다.
			# 데이터에 대한 설명등을 엑셀에 포함하는 경우 빈 셀을 만들어 경계를 설정할 수 있도록 함.
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
				
			# Json 데이터 키가 중복되지 않도록 확인
			if uniqueArray(rowVal) == False :
				print "Data column name error."
				break

			rowCnt = workSheet.nrows
			
			sheetData = SheetData(sheetName)
			sheetData.addDataNamesWithList(rowVal)
			
			if rowCnt > 1 :
				for rowIndex in range(1, rowCnt) :
					singleData = workSheet.row_values(rowIndex)
					sheetData.addDataWithList(singleData)
				
			excelData.addSheetData(sheetData)
			print "Done."
			
		js = json.dumps(excelData.getDataWithDict(), sort_keys = True, indent = 4, ensure_ascii=False)
		outfile = codecs.open(excelData.jsonFileName, 'w', 'utf-8')
		outfile.write(js)
		outfile.close()
		#print js

if __name__ == "__main__" :
	main()
	
	

	
	