import csv

class ColConverter(object):

	def __init__(self,header):
		self.head = header


	def convert(self,num):
		return self.head[num]

	def cleanRows(self,rows):

		newrows = []
		newrows.append(rows[0])
		for i in range(1, len(rows)):
			print "duh " + str(rows[i][1])
			if(rows[i][1] == '2'):
				newrows[i].append(rows[i])

		return newrows			


def writeOnCSV(rows, filename):
	with open(filename, 'wb') as f:
	    writer = csv.writer(f)
	    writer.writerows(rows)


def readCSV(filename):
	num=0
	rows = []

	with open(filename) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    
	    for row in readCSV:
	    	if(num==0):
	    		header = row
	        else:
	        	rows.append(row)
	        num= num +1
	return header, rows


def readNoHead(filename):
	num=0
	rows = []

	with open(filename) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    
	    for row in readCSV:

	        	rows.append(row)
	return rows



# csvfile = 'AgeGroupZ2576.csv'

# header, rows = readCSV('mine.csv')

# for i in range(0,len(header)):
# 	if(header[i]=='k3'):
# 		print i


# body = readNoHead(csvfile)


# for i in range(0,len(body)):
# 	body[i][0] = header[int(body[i][0])]

# writeOnCSV(body,csvfile)
