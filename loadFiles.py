import csv, re, operator
from collections import OrderedDict, Counter, namedtuple

#Register a dialect for Concordance load file delimiters using their ASCII values

csv.register_dialect('concordance', delimiter=chr(20), quotechar=chr(254), quoting=csv.QUOTE_ALL)

Family = namedtuple('Family', ['parent', 'family'])

class Bates(object):

	def __init__( self, prefix = '', number = 0, digits = 0 ):
		
		self.prefix = prefix
		self.number = number
		self.digits = digits
		
	@classmethod
	def fromString( cls, bates ):

		match = re.match(r"([^0-9]+)([0-9]+)", bates, re.I)
		split = match.groups()
		
		prefix = split[0]
		number = int(split[1])
		digits = len(split[1])
		
		inst = cls(prefix, number, digits)
		
		return inst
	
	@classmethod
	def batesRange( cls, start = Bates(), end = Bates() ):
	
		for i in range(start.number, end.number+1):
			
			inst = cls(start.prefix, i, start.digits)
			yield inst		
			
	def __add__( self ):
	
		pass
	
	def __str__( self ): 
	
		return '{0}{1}'.format(self.prefix, str(self.number).zfill(self.digits))
		
	def __repr__( self ):
	
		return '{0}{1}'.format(self.prefix, str(self.number).zfill(self.digits))
		
class Loadfile(object):
	
	def __init__( self, records = {}, fields = [], key = '', nativeField = '', textField = '', familyField = ''):
	
		self.records = records
		self.fields = fields
		self.key = key
		self.nativeField = nativeField
		self.textField = textField
		self.familyField = familyField 
		self.familyType = 'splitrange'
		
	@classmethod
	def fromFile( cls, inputFile, key ):
	
		with open(inputFile,'r') as rawInput:
		
			parser = csv.DictReader(rawInput, dialect='concordance')
			fields = parser.fieldnames
			records = []
			
			for row in parser:
				
				rec = Record(key = row[key], metadata = row)
				records.append(rec)
			
			nativeField, textField, familyField = '', '', ''
			
			if 'NATIVEFILE' in fields:
				
				nativeField = 'NATIVEFILE'
			
			if 'OCRPATH' in fields:
			
				textField = 'OCRPATH'
				
			if 'ATTRANGE' in fields:
			
				familyField = 'ATTRANGE'
			
			inst = cls(records, fields, key, nativeField, textField, familyField)

			return inst
	
	@classmethod
	def fromFiles( cls, directory, key ):
	
		pass
	
	def toFile( self, outputFile, dialect='concordance' ):
	
		with open(outputFile, 'w', newline='') as output:
		
			parser = csv.DictWriter(output, fieldnames = self.fields, restval = '', dialect=dialect)
			
			parser.writeheader()
			
			parser.writerows([record.metadata for record in self.records])
			
			return True
	
	def recordKeys( self ):
		
		keys = []
		
		for record in self.records:
		
			keys.append(record.key)
			
		return keys
	
	def getFamilies( self ):

			families = []
			
			for record in self.records:
			
				if not record.metadata[self.familyField]:
					families.append(Family(record,[record]))
					continue	
				
				if self.familyType == 'range':
					famStart = Bates.fromString(record.metadata[self.familyField][:len(record.key)])
					famEnd = Bates.fromString(record.metadata[self.familyField][-len(record.key):])
				
				elif self.familyType == 'splitrange':
					famStart = Bates.fromString(record.metadata[self.familyField[0]][:len(record.key)])
					famEnd = Bates.fromString(record.metadata[self.familyField[1]][-len(record.key):])
				
				elif self.familyType == 'list':
					famStart = Bates.fromString(record.key)
					famEnd = Bates.fromString(record.metadata[self.familyField].split(';')[-1])
						
				if record.key != str(famStart):
					continue
				
				for page in Bates.batesRange(famStart, famEnd):
					
					members = [record]
					
					try:
						child = self.recordKeys().index(str(page))
						members.append(self.records[child])
						
					except ValueError: 
						continue
				
				families.append(Family(record,members))
			
			return families
	
	def sortRecords(  self, sortField ):
	
			self.results.sort(key = operator.attrgetter(sortField))
			return None
	
	def familySort ( self, sortField ):
	
			pass
	
class Record(object):
	
	def __init__( self, key = '', metadata = {} ):
		
		self.key = key
		self.metadata = metadata
		
	def __str__( self ):
	
		return 'Record {0}'.format(self.key)
		
	def __repr__( self ):
	
		return '<Record {0}>'.format(self.key)
	
class Field(object):

	pass
