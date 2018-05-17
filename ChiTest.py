import csv
import math
import numpy as np
import sys
import string
from Table import Table
from clean import ColConverter



def writeOnCSV(rows, filename):
	with open(filename, 'wb') as f:
	    writer = csv.writer(f)
	    #writer.writerow(header)
	    writer.writerows(rows)
        


def readHeader(filename):
	num=0
	rows = []

	with open(filename) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')    
	    for row in readCSV:
	    	if(num==0):
	    		return row

def readCSVDict(filename):
        f = open(filename, 'rU')
        rows = csv.DictReader(f)
        return rows
                        

def readCSVtoDouble(filename):
	num=0
	rows = []

	with open(filename) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    
	    for row in readCSV:
	    	if(num==0):
	    		header = row
	        else:
	        	rows.append([float(i) for i in row])
	        num= num +1
	return header, rows


def readCSV(filename,isHead = True):
	rows = []
	count = 0
	with open(filename) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    for row in readCSV: #Iterate through each row in the dataset
	    	if(not (count==0 and isHead)): #If not the row is not the header
		    	for i in range(0,len(row)): #Iterate over the answers in each row
		    		if(RepresentsInt(row[i])):
		    			#print "REPRESENTS " + row[i]
		    			temp = int(row[i])
		    			row[i] = str(temp)

		    		elif(RepresentsFloat(row[i])):
		    			#print "REPRESENTS " + row[i]
		    			temp = float(row[i])
		    			temp = int(temp)
		    			row[i] = str(temp)

		        rows.append(row)
	        count =  count +1
	return rows


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def RepresentsFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False


def getPercentColumn(body, colIdx):
	total = 0
	percents = []
	boygirl = []
	for i in range(0, len(body)):
		total = total + int(body[i][colIdx])

	for i in range(0, len(body)):
		boygirl.append(body[i][colIdx])
		percents.append( float(float(body[i][colIdx])/total))

	return percents, boygirl



def getSumRows(rows):
	return np.sum(rows, axis=1).reshape(-1,1)


def getProportions(rows, totals):
	

	proportions = np.copy(rows)
	proportions = proportions / totals.reshape(-1,1)

	index=0
	getStandardError(proportions,totals)
	return proportions


def getStandardError(proportions,totals):
 	return np.sqrt(proportions*(1-proportions)/ totals.reshape(-1,1))


def getProportionPerColumn(numpiRows):
	colSum = np.sum(numpiRows, axis=0)
	return colSum



def sortTableColumns(header, rows):

	newheader = header[1:]
	newheader = [str(i) for i in newheader]

	pihead = np.asarray(newheader[0:])
	pirows = np.asarray(rows)
	labelCols = pirows[:,0]
	pirows = np.delete(pirows, 0, axis=1)
	i = np.argsort(pihead)
	pirows = pirows[:,i]
	pihead = pihead[i]
	pirows = np.hstack(( labelCols.reshape(-1,1),pirows))
	
	return [header[0]] + [str(i) for i in pihead.tolist()], pirows.tolist()



def doAccumulate(header, rows):
	

	newheader = [str(header[1])+"+"+ str(header[2])]
	newheader = [header[0]] + newheader


	#for i in range(3,len(header)-1):
	temp = ""
	for y  in range(3, len(header)-1):
		temp = temp + "+"+str(header[y])
	newheader.append(temp)

	print "new header"
	print newheader	
	newrow = []
	
	for row in rows:
		temprow = []
		temprow.append(row[1]+row[2])
		#print "len of row"+str(len(row)) 
		#for i in range(3,len(row)-1):
		temp = 0
		for y  in range(3, len(row)-1):
				#print row[y]
			temp = temp + row[y]	
		temprow.append(temp)
			#print "add"
		newrow.append([row[0]] +temprow)

	return newheader, newrow



def readTableToFloat(table):
	rows = []
	for x in range(1,len(table.rows)):
		rows.append([float(i) for i in table.rows[x]])
	return table.rows[0], rows


def doFile(table,fileNum,results,converter,z, H):
	header, rows = readTableToFloat(table)
	header , rows = sortTableColumns(header,rows)

	print "Header after i killed it "+ str(header)
	print "diz are da header"
	print header	
	print "diz are the rows"
	print rows
	numpiRows = np.asarray(rows)
	labelCols = numpiRows[:,0]
	numpiRows=np.delete(numpiRows, 0, axis=1)

        if(len(numpiRows[0]) > 2 and numpiRows[0][0] == 0):
                numpiRows = np.delete(numpiRows,0,axis=1)

	totals =  getSumRows(numpiRows)
	#print "total: "+str(totals)

	proportions = getProportions(numpiRows, totals)
	
	print "proportions "+ str(proportions)

        proportions_list = proportions.tolist()

        for group in proportions_list: #for every group
                if(len(group) >= 2):
                        '''
                        This specific if statement deletes any 0 values in the proportions list in case
                        there is one as the first element of the group array.
                        There should only be a proportion value for a and b. The proportion for everything
                        else is 1 - (a+b).
                        '''
                        if(len(group) > 2):
                                del group[0]
                        
                       
	

	errors = getStandardError(proportions,totals) #Retrieve standard error of proportion

	upperBounds = proportions + errors*z
	lowerBounds = proportions - errors*z

	colSum = getProportionPerColumn(numpiRows)	
	PopulationCount = np.sum(colSum)
	PopQuestionProp = colSum / PopulationCount #Actual Population Proportion

	expected = np.copy(numpiRows)
	grandTotal = np.sum(colSum) 
	
	
	print "totals"
	#print totals
	lenrow = len(totals)

	print "colsum"
	#print colSum
	lencol =  len(colSum)


	# print "expected"
	# print expected
	

	for i in range(0,len(expected)):
		for y in range(0,len(expected[i])):
			#print colSum[y]
			expected [i][y] = totals[i][0] * colSum[y] / grandTotal

	
	print "Expected "
	print expected
	
	#print "the data"
	#print numpiRows

	chi = ((numpiRows - expected) * (numpiRows - expected)) / expected
	#print "Expected"
	#print expected
	print "Observed "
	print numpiRows

	shapeexpected = np.reshape(expected,(-1,1))
	print "Shape expected "
	print shapeexpected

	chistat = np.sum(chi)

	#if(chistat > z): #If the chi score is greater than the chi-square critical value, add it to the results
        higherOrLower=""

        '''
        tolerableFive =  expected.size
        tolerableFive = int(tolerableFive*0.20)


        numFive = 0
        for el in range(0,shapeexpected.size):
                if shapeexpected[el][0] < 5:
                        numFive = numFive +1

        if numFive > tolerableFive:
                chistat = np.nan
        '''
        if(not np.isnan(chistat)):
                print "observed",
                print numpiRows[0][1]
                print "expected",
                print expected[0][1]
                if(expected[0][1] < numpiRows[0][1] ):
                        higherOrLower ="+"
                else: 
                        higherOrLower = "-" 


        # print chistat

        print "Chi-Square"
        print chi
        print "Chi -stat"
        print chistat
        """
        print "Population count "+ str(PopulationCount)
        print "Pop Count "+ str(colSum)
        print "Errors" + str(errors)
        print "Pop Proportions "+ str(PopQuestionProp) 
        print "Lower "+ str(lowerBounds)
        print "Upper "+str(upperBounds)
        """
        #if(chistat > z):
        thequestion = converter.convert(fileNum)
        print "The H " + str(H)
        print "The Question "+ thequestion
        '''
        if(np.isnan(chistat)):
                chistat = ""
        '''

        print colSum.size
        print totals.size		

        degreeFreedom = (colSum.size - 1) * (totals.size -1)

        
        totals_list = totals.tolist() #populations for all groups

        thequestion = string.capwords(thequestion)
                                
        results_temp = [thequestion,H,chistat,higherOrLower,degreeFreedom];
                
                
        #results_temp.extend(proportions_list[:,1])

        chiCritical = 0.0 
                
        #Determine the chi critical value to compare chi score with
        #based on the degree of freedom

        if(degreeFreedom == 1):
                chiCritical = '6.635'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 2):
                chiCritical = '9.21'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 3):
                chiCritical = '11.345'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 4):
                chiCritical = '13.277'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 5):
                chiCritical = '15.086'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 6):
                chiCritical = '16.812'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 7):
                chiCritical = '18.475'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 8):
                chiCritical = '20.09'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 9):
                chiCritical = '21.666'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 10):
                chiCritical = '23.209'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 11):
                chiCritical = '24.725'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 12):
                chiCritical = '26.217'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 13):
                chiCritical = '27.688'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 14):
                chiCritical = '29.141'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 15):
                chiCritical = '30.578'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 16):
                chiCritical = '32'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 17):
                chiCritical = '33.409'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 18):
                chiCritical = '34.805'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 19):
                chiCritical = '36.191'
                results_temp.append(str(chiCritical))
        elif(degreeFreedom == 20):
                chiCritical = '37.566'
                results_temp.append(str(chiCritical))
                
        else:
                chiCritical = '100'
                results_temp.append(str(chiCritical))
                                            

        #Determine if the chi score is > than the chi critical value
        if( not(type(chistat) is str) and (float(chistat) > float(chiCritical)) ):#If yes
                results_temp.append('1')#Chi score is significant
        else:#otherwise
                results_temp.append('0')#Chi score is insignificant
                

        results_temp.extend(totals_list) #append populations for all groups
                                

        for group in proportions_list: #for every group
                if(len(group) >= 2):
                        results_temp.append(str(round(float(group[0])*100,2))+'%') #append proportion of answer a for each group
                        results_temp.append(str(round(float(group[1])*100,2))+'%') #append proportion of answer b for each group
                        results_temp.append(str(round((1-(float(group[0])+float(group[1])))*100, 2))+'%') #apend proportion of other answers for each group
                        #results_temp.append(group[i]) #append each proportion of every answer for each group
                        #print group[i]
                                             
        results.append(results_temp)
	


def group(index, rows,V, header):
	groups = {}
	#1 Because first index is question name
	if header not in V.keys():
		print "Warning "+ header +" "+"not in Variable description"
	else:
		for i in range(1,len(V[header])):
			entry =  V[header][i][0]
			groups[V[header][i][0]] = []


	for i in range(0, len(rows)):

		entry = rows[i][index]

		if(entry != '-1' and entry!='' and entry != '-1.0'):

			if entry in groups:
				groups[entry].append(i)
			else:
				print "Warning  "+ str(entry) +" is not declared in variable description for question "+ header
				groups[entry] = []
				groups[entry].append(i)

	return groups


def getTable(col,clusters,V, header):

	groups = []
	for c in clusters:
		groups.append(group(col,c,V,header))

	keys = []
	for g in groups:

		for key in g:

			if key not in keys:
				keys.append(key)
	
	return Table(groups,keys,header)


def getVariableList(filename, varMarker): #Reads the question
	variables = {}	

	with open(filename) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    for row in readCSV:
	    	if( row[0] == varMarker):
	    		variables[row[1]]= [row[2]]
	    		lastVar = row[1]    	
	    	else:
	    		variables[lastVar].append((row[0], row[1]))			        
	return variables

def chiTest(datasetPaths):
  #change to ur own.
  vList = getVariableList('Updated-Variables.csv', '^') #Get Variable Description
  header = readHeader(datasetPaths[0]) #Read the header from one of the datasets which include the question codes


  results = []
  converter = ColConverter(header)


  #print header
  clusternames = datasetPaths #Read the filepaths of the datasets

  #print clusternames
  clusters = [] #clusters contains all of the respondents and their answer in per dataset

  #For each data set
  for clustername in clusternames:
    clusterRow = readCSV(clustername) #Get all of the respondent's IDs and answers in the dataset
    #print clusterRow
    clusters.append(clusterRow) #Add to the clusters


  tableList = [] #list of contingency tables

  #z=[6.64]
  z=[0.0]
  zstr = ['1960']
  for y in range(0,len(z)):
    results = [] #The resulting content that will be written in save.csv
    dataset_headers = []
    dataset_names = []

    for x in range(0, len(clusternames)):
        clustername_arr = clusternames[x].split('\\')
        dataset_names.append(clustername_arr[len(clustername_arr)-1])#Getting the dataset name from its file path
        dataset_headers.append("Dataset " + str(x+1))

    results.append(dataset_headers)
    results.append(dataset_names) #Append dataset names

          
    population_and_proportionHeaders = [] #Headers Ni and Pi for each cluster i

    for x in range(0, len(clusternames)):
        population_and_proportionHeaders.append("N"+str(x+1)) #Add Header "Nx" for each cluster x. Total of x

    for x in range(0, len(clusternames)):
      population_and_proportionHeaders.append("P"+str(x+1)+"(a)") #Add Header "Px" for each cluster x. Proportion of x
      population_and_proportionHeaders.append("P"+str(x+1)+"(b)")
      population_and_proportionHeaders.append("P"+str(x+1)+"(etc)")
                  
    #results_headers = ["Question","Feature","Chi","Higher Or Lower", "Degrees of Freedom"] #Results headers                     
    results_headers = ["Feature","Question","Chi","Higher Or Lower", "Degrees of Freedom", "Cut-off", "Is significant"] #Results headers
    results_headers.extend(population_and_proportionHeaders) #Append the population and proportion headers for each cluster to results headers
    results.append(results_headers) #Append these as header names to the results
    print results

    for i in range(0,len(header)): #Iterate over each question
      if header[i] not in vList.keys(): #If the question code is not found in Variable Description
        print "Warning "+ header[i] +" "+" question name not in Variable description will be assigned to null"
        H = "null"
      else:
        H = vList[header[i]][0] #H is the question itself
      print "col "+str(i)+" "+ header[i]	
      theTable = getTable(i,clusters,vList,header[i]) #Generates a table matrix for all datasets to do the chi-test for the question

      doFile(theTable,i,results,converter,z[y], H) #Chi test on the question and then writing it in the file
      

      #Remove the column with -1 in the table.
      if('-1' in theTable.rows[0]):
        position = theTable.rows[0].index('-1')#Get index of the -1 column.
        for row in theTable.rows:#Delete the entire -1 column.
                del row[position]

      print "Table",
      print theTable.rows

      theTable.getPrintable(tableList)


    #print results
    fileName = 'Chi-Test_' #Get filename of save file
    for name in dataset_names:
        fileName = fileName + name + '_'

    fileName = fileName + '.csv'    

    writeOnCSV(results,fileName)
    #print tableList
    writeOnCSV(tableList,"Tables "+fileName)
    return fileName

  #results = converter.cleanRows(results)
  #writeOnCSV(results,filename)

  # print "results"
  # print results



