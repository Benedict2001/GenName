import shlex
import getopt
import sys
from random import randint, normalvariate


# Define global variables
verbose = False		# Show progress and useful info
unique = False		# Enforce uniqueness in the output file
titalise = False	# Convert names to Title Format
opFormat = 'CSV'	# Alternative is JSON
opFile=""
numNames = -1		# Number of names to generate
middleProb = .5		# Prob of generating a middle name
mProb = 0.5			# Prob of generating a male name
fProb = 0.5			# Prob of generating a female name
dupRatio = 1.0		# Ratio of duplicates to total generated
dotTick	= 100		# Every dotTick names, you output a tick on screen
meanAge=-1			# Mean age
ageStdDev=-1		# Standard Deviation

def isNonNegativeFloat(s):	# Validate that something is a non negative float
	try:
		if float(s) >= 0.0:
			return True
	except ValueError:
		return False

def isPositiveInt(s):		#	Validate that something is a positive Integer
	try:
		if int(s) > 0:
			return True
	except ValueError:
		return False

def isNonNegativeInt(s):	#	Validate that something is an Integer >= 0
	try:
		if int(s) >= 0:
			return True
	except ValueError:
		return False

def validOPFormat(format):	# Validate the output format is a valid choice
	if (format not in ['c', 'j']):
		return False
	return True

def validCount(num):		# Validate that the count of names to generate is >= 0
	if isPositiveInt(num) == False:
		return -1
	return int(num)

def validMiddle(prob):		# Validate the probability of generating a middle name
	if isNonNegativeFloat(prob) == False:
		return -1
	p = float(prob)
	if (p > 1.0):
		return -1
	return p

# Ratio Parser
# Used to parse male:female ratio
# Used to parse mean:stdDev as well
def parseRatio(s):
	r_split = s.split(':')
	if (len(r_split) != 2):
		return -1, -1
	a = r_split[0]
	b = r_split[1]
	if (isNonNegativeInt(a) == False):
		print 'First argument not non-negative'
		return -1, -1
	if (isNonNegativeInt(b) == False):
		print 'Second argument not non-negative'
		return -1, -1
	return int(a), int(b)

def calculateMaleProb(males, females):	# Convert ratios of males to females to a probability of being a male
	return float(males) / (males + females)

def usage():
	print
	print sys.argv[0], '[-a m:s] [-f c|j] [-m <prob>] -n <number> [-o <file>] [-r m:f] [-t] [-u] [-v]'
	print '-a : Age range mean:stdDev - Guassian distribution'
	print '-f : Optional output format of the names (j=JSON, c=CSV) - defaults to CSV'
	print '-m : Optional propability of names having middle name'
	print '-n : Number of names to generate (must be > 0)'
	print '-o : Optional name of output file - if not specified, then default is standard out'
	print '-r : Optional rough ratio of males to females. If uspecified, defaults to 1:1'
	print '-t : Titalise names (e.g. "FRED" or "fred" = "Fred")'
	print '-u : Optionally enforce Uniqueness. This will take much longer to generator'
	print '-v : Optionally verbose'

try:
	opts, args = getopt.getopt(sys.argv[1:], "a:f:m:n:o:tr:uv")
except getopt.GetoptError:
	usage()
	sys.exit(2)

for opt, arg in opts:
	if opt == '-a':
		meanAge, ageStdDev = parseRatio(arg)
		if (meanAge < 0):
			print 'Illegal format for age range', arg
			usage()
			sys.exit(1)

	elif opt == '-f':
		if validOPFormat(arg) == False:
			print 'Illegal format ', format
			usage()
			sys.exit(1)
		if (arg == 'c'):
			opFormat = 'CSV'
		elif (arg == 'j'):
			opFormat = 'JSON'

	elif opt == '-m':
		middleProb = validMiddle(arg)

		if middleProb < 0:  # Probaility of generting a middle name
			print '-m probability must be a value between 0.0 and 1.0 inclusive'
			usage()
			sys.exit(1)

	elif opt == '-n':
		if isNonNegativeInt(arg):
			numNames = validCount(arg)
		else:
			print 'Number of names (-n) to generate must be > 0'
			usage()
			sys.exit(1)

	elif opt == '-o':
		opFile = arg

	elif opt == '-r':
		m, f = parseRatio(arg)
		if (m < 0):
			print 'Illegal format ', arg
			usage()
			sys.exit(1)
		mProb = calculateMaleProb(m, f)

	elif opt == '-t':
		titalise = True
	elif opt == '-u':
		unique = True
	elif opt == '-v':
		verbose = True
	else:
		print 'Illegal option ', opt
		usage()
		sys.exit(1)

# General Validation of Data

def strTitalise(s):		# Convert text to Title Format if needed
	if (titalise):
		str = s.title()
	return s

def GenName(maleProb, middleProb):
	middleLimit = float(middleProb) * 1000.0		# Multiply by 1000 - cater for 3 decimal places
	maleLimit = float(maleProb) * 1000.0
	middleOdds = randint(0, 1000)

	if (maleLimit >= randint(0,1000)):
		name = strTitalise(maleNames[randint(0, mCount-1)])				# First name
		if middleOdds < middleLimit:
			name += " " + strTitalise(maleNames[randint(0, mCount-1)])	# Possible middle name
		gender = "M"
	else:
		name = strTitalise(femaleNames[randint(0, fCount-1)])			# First name
		if middleOdds < middleLimit:
			name += " " + strTitalise(femaleNames[randint(0, fCount-1)])	# Possible middle name
		gender = "F"

	surname = strTitalise(surnames[randint(0, sCount-1)])
	age = normalvariate(meanAge, ageStdDev)
	s = name + ", " + surname + ", " + gender

	return name, surname, gender, age, s

def isDuplicate(s):
	nLen = len(nameArray)
	for i in range(nLen):
		check = createStr(i)
		if s == check:
			return True
	return False

def createStr(n):			# Create a string from a JSON entry
	record = nameArray[n]
	name = record['name']
	surname = record['surname']
	gender = record['gender']
	return name + ", " + surname + ", " + gender

def writeFile(fname):

	if (fname != ""):
		f = open(fname, "w")
		print "Writing data to file: ", fname

	nLen = len(nameArray)
	for n in range(nLen):
		record = nameArray[n]
		id = str(record['id'])
		name = record['name']
		surname = record['surname']
		gender = record['gender']
		age = record['age']

		s=""
		if opFormat == 'CSV':
			if (meanAge > 0):
				s = id + ", " + name + ", " + surname + ", " + gender + ", " + str(int(age))
			else:
				s = id + ", " + name + ", " + surname + ", " + gender
		elif opFormat == 'JSON':
			if (meanAge > 0):
				s = '{ "id" : ' + id + ', "name" : ' + name + '", "surname" : "' + surname + '", "gender" : "' + gender + '", "age" : "' + str(int(age)) + '" }'
			else:
				s = '{ "id" : ' + id + ', "name" : ' + name + '", "surname" : "' + surname + '", "gender" : "' + gender + '" }'
			if (n < (nLen-1)):
				s += ","
		if (fname != ""):
			f.write(s + "\n")
		else:
			print (s)

	if (fname != ""):
		f.close()

#
# Format of Data File is NAME <space> Frequency <space> Cumulative Frequency <space> Order by Frequency
#
def parseLine(line):
	vals = shlex.split(line)
	return vals[0]

def loadNames(fname):		# Load each line into an array to be returned
	arr=[]
	with open(fname, 'r') as f:
		for line in f:
			arr.append(parseLine(line))
	f.close()
	return len(arr), arr

mCount, maleNames = loadNames('male.txt')
print 'Loaded ', mCount, 'male names'
fCount, femaleNames = loadNames('female.txt')
print 'Loaded ', fCount, 'female names'
sCount, surnames= loadNames('surnames.txt')
print 'Loaded ', sCount, 'surnames'

print 'Output format = ', opFormat
print 'Prob of middle Name = ', middleProb
print 'Enforcing Uniqueness = ', unique
print 'Probability of being a male = ', mProb
print 'Mean Age = ', meanAge

numMales=0
numFemales=0
nameArray=[]
id = 1
dupCount = 0
dupLimit = dupRatio * numNames
for i in range(numNames):
	name, surname, gender, age, s = GenName(mProb, middleProb)
	record = {'id' : id, 'name' : name, 'surname' : surname, 'gender' : gender, 'age' : age}

	if (verbose):
		print 'Generated name is ', record
	dup = False
	if (unique and i > 0):		# Restricting uniques? More than one record
		dup = isDuplicate(s)
		if (verbose and dup):
			print 'Duplicate found - Regenerating until a unique value found'
		dupCount = 0
		while (dup and (dupCount < dupLimit)):
			dupCount += 1
			# print s, ' is a duplicate, trying again: ', dupCount
			name, surname, gender, age, s = GenName(mProb, middleProb)
			record = {'id': id, 'name': name, 'surname': surname, 'gender': gender}
			if (verbose):
				print 'Regenerated name (', dupCount, ') is ', record
			dup = isDuplicate(s)
	if (dupCount == dupLimit):
		print "It may not be possible to generate your data without duplicates."
		print "Try increasing the duplicate ratio, the source data, or reduce the names to generate"
		print "Writing the data I have generated so far"
		writeFile(opFile)
		sys.exit(1)

	if (verbose):
		print 'Adding ', record, ' to the list'
	nameArray.append(record)
	if gender == "M":
		numMales += 1
	else:
		numFemales += 1
	id += 1
	if ((i % dotTick) == 0):
		sys.stdout.write('.')
		sys.stdout.flush()

print
writeFile(opFile)

print 'Num Males = ', numMales
print 'Num Females = ', numFemales
