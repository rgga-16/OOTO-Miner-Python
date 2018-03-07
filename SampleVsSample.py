'''
This file performs Z-Test of Independence of Pooled Proportions between two sample groups

'''
import sys
import csv
import math
from collections import defaultdict
from collections import Counter

'''
Returns the description of the given feature code and filename of the Variable Descriptor
'''
def getFeatureDescription(filename, feature, varMark):
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == varMark:
                if row[1] == feature:
                    return row[2]
'''               
Reads a column in a csv file given the name of the column header
'''
def readColumnCSV(filename, columnName):
    columns = defaultdict(list)
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            for(k,v) in row.items():
                columns[k].append(v)

    return columns[columnName]

'''
Writes a set of rows into a .csv file given the filename
'''
def writeOnCSV(rows, filename):
	with open(filename, 'wb') as f:
	    writer = csv.writer(f)
	    writer.writerows(rows)
'''
Generates the two groups that will be compared to each other for the Z Test
'''
def generateGroups(datasets, datasetPaths, selectedFeature, selectedFeatureValues, featureValues):
    for i in range(0, len(datasetPaths)):
        dataset = {'ColumnData':readColumnCSV(datasetPaths[i],selectedFeature)}
        temp = datasetPaths[i].split("\\")
        dataset['Name'] = temp[len(temp)-1]
        datasets.append(dataset)
        print dataset['Name']

    datasets = getTotalsAndProportions(datasets, featureValues, selectedFeatureValues)
    return datasets
    

'''
Calculates the total amount and proportion of each group.
Proportion is determined by which values of the feature are chosen
'''
def getTotalsAndProportions(datasets, featureValues, selectedFeatureValues):
    for dataset in datasets:
        countN = 0
        countP = 0
        c = Counter(dataset['ColumnData']) #Counts the number of occurrences of each feature value in the group
        featureValues.remove
        for x in c:
            if x in featureValues:
                countN = countN + int(c[x])
            if x in selectedFeatureValues:
                countP = countP + int(c[x])
        dataset['Total'] = countN #The total number of records that had a valid answer
        dataset['Proportion'] = countP #The number of records that answered any of the chosen feature values
        dataset['ProportionPercent'] = countP/float(countN)# Proportion / Total
    return datasets

'''
Z-Test of Independence of Pooled Proportions
Requires total amount and proportion of the two groups that will be compared with each other
'''
def ZTest(n1,p1,n2,p2):
    
    PPrime = getPPrime(n1,p1,n2,p2)
    
    standardError = getStandardError(PPrime, n1, n2)

    z = (p1 - p2) / float(standardError)

    return z,PPrime,standardError

'''
Returns P^ which is calculated by

P^ = ((n1 * p1) + (n2 * p2)) / (n1 + n2)

Where n and p represents respectively the total and proportion percent of each group

'''
def getPPrime(n1,p1,n2,p2):
    return float(n1*p1 + n2*p2) / float(n1 + n2)

'''
Returns the standard error between the two groups

Where n represents respectively the total of each group
and PPrime is P^

'''
def getStandardError(PPrime, n1, n2):
    temp = 1/float(n1) + 1/float(n2)
    return math.sqrt(PPrime * (1-PPrime) * temp)

def sampleVsSample(datasetPaths, selectedFeature, featureValues, selectedFeatureValues):
  for datasetPath in datasetPaths:
    print datasetPath
  '''
  datasetPaths.append(sys.argv[2]) #File path of Dataset 1
  datasetPaths.append(sys.argv[3]) #File path of Dataset 2

  initialVarDesc = sys.argv[4]#File path of Initial Variable Descriptor

  selectedFeature = sys.argv[5]#Feature that was selected for the test
  '''
  initialVarDesc = "InitialVarDesc.csv"

  selectedFeatureDesc = getFeatureDescription(initialVarDesc, selectedFeature, '^')#Get description of the selected Feature

  featureValues = featureValues.split(":") #All possible values of the feature
  selectedFeatureValues = selectedFeatureValues.split(":") #The selected values of the feature to be included in the proportion (P) 
  
  datasets = [] #The two groups that will be compared with each other

  datasets = generateGroups(datasets, datasetPaths,selectedFeature, selectedFeatureValues, featureValues) #Generate the two groups and their proportions


  n1 = datasets[0]['Total']
  p1 = datasets[0]['ProportionPercent']
  fp1 = datasets[0]['Proportion']
  n2 = datasets[1]['Total']
  p2 = datasets[1]['ProportionPercent']
  fp2 = datasets[1]['Proportion']

  z,PPrime,standardError = ZTest(n1,p1,n2,p2) #Perform Z-Test on the two groups and get the z-score


  zSquared = z**2#Get Z-Square

  z99 = 2.58 #Z-Square Critical Value at 99% Confidence
  z95 = 1.96 #Z-Square Critical Value at 95% Confidence

  greaterThanZ99 = '' #Determines if the Z-score surpasses the Z-Square Critical Value at 99% Confidence
  greaterThanZ95 = '' #Determines if the Z-score surpasses the Z-Square Critical Value at 95% Confidence

  if(math.fabs(z) > z95):
      greaterThanZ95 = 'Reject'
  else:
      greaterThanZ95 = 'Accept'

  if(math.fabs(z)> z99):
      greaterThanZ99 = 'Reject'
  else:
      greaterThanZ99 = 'Accept'


  #Summary of results
  print 'Z: ' + str(z)
  print 'Z^2: ' + str(zSquared)
  print '99% (Accept/Reject): ' + greaterThanZ99
  print '95% (Accept/Reject): ' + greaterThanZ95
  print 'P1: ' + str(p1)
  print 'P2: ' + str(p2)
  print 'P^: ' + str(PPrime)
  print 'Standard Error: ' + str(standardError)
  print 'N1: ' + str(n1)
  print 'N2: ' + str(n2)
  print 'N1+N2: ' + str(n1+n2)
  print 'freq(p1): ' + str(fp1)
  print 'freq(p2): ' + str(fp2)


  headers = ['','z', 'z^2', '99% (' + str(z99) + ')', '95% (' + str(z95) + ')', 'n1', 'n2', 'n1+n2','p1','1-p1', 'p2','1-p2', 'p^', 'SEp','freq(p1)', 'freq(p2)']
  results = ['v',round(z,2), round(zSquared,2), greaterThanZ99, greaterThanZ95, n1, n2, n1+n2, round(p1,2),round(1-p1,2),round(p2,2),round(1-p2,2),round(PPrime,2),round(standardError,2), fp1,fp2]
  datasetHeaders = []
  datasetHeaders.append('Dataset 1 : ' + datasets[0]['Name'])
  datasetHeaders.append('Dataset 2 : ' + datasets[1]['Name'])
  featureHeader = []
  featureHeader.append(selectedFeature + ': ' + selectedFeatureDesc)


  selectedFeatureValueHeader = ['Selected Values: ']

  for i in selectedFeatureValues:
      selectedFeatureValueHeader.append(i)



  summary = []

  summary.append(datasetHeaders)
  summary.append(featureHeader)
  summary.append(selectedFeatureValueHeader)
  summary.append(headers)
  summary.append(results)

  summaryName = 'Sample vs Sample_' + selectedFeature+ '_' + datasets[0]['Name'] + '_VS_' + datasets[1]['Name'] + '.csv'
  writeOnCSV(summary, summaryName)
  return summaryName





        
                
    

        




    
