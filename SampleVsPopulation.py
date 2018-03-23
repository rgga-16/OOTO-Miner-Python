# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 11:03:29 2018

@author: Rgee Gallega


This is a program that allows you to compare a population dataset to several subgroups/samples of it, and tell whether the sample
is significantly different from the population based on a given feature.

The samples are made by dividing the population dataset into them based on the values of a given feature (sample feature).
For example, if you choose 'Gender' as your sample feature, the samples will be the 'Male' and 'Female' samples.

Comparison is done by calculating the Z-Score and Standard Error of Sample Proportion (SEp) of each sample to the population.
NOTE: Only SEp is being used to determine whether the sample is significantly different from the population.
      Its Z-score is only being calculated but not used for comparison. Kept just in case.

To determine whether the sample is significantly different from the population,
you calculate the upper bound (UB) and lower bound (LB) of it based on its proportion (frequency/total number) using the ff:

UB = p + SEp * Z
LB = p - SEp * Z

Where Z is the Z Critical Value inputted by the user based on ά he/she desires.
For example, if the user wants ά = 1% interval, then Z Critical Value is 2.58

"""

import sys
import csv
import copy
from collections import Counter
import math



'''
Reads all of the rows in a csv file as a list of dictionaries
'''
def readCSVDict(filename):
    rows = csv.DictReader(open(filename))
    return rows

'''
Writes a set of rows into a .csv file given the filename
'''
def writeOnCSV(rows, filename):
	with open(filename, 'wb') as f:
	    writer = csv.writer(f)
	    writer.writerows(rows)
	print 'Saved file is: ' + filename

'''
Given the feature you want to make the samples by, divide the population into the samples.

Example: If the sample feature is 'age'


'''
def makeSamples(records, sampleFeature,sampleGroups):
    groupNames = []
    for record in records:
        if(record[sampleFeature] not in groupNames):
            groupNames.append(record[sampleFeature])

    for gn in groupNames:
        sample = {'Sample Name':gn, 'Total':0, 'Frequency':0}
        sampleGroups.append(sample)

        
'''
Get the total number (n) and frequency (f) of each sample.

n is the number of records in a sample who answered any valid value in the selected feature
f is the number of records in a sample who answered any of the chosen values in the selected feature

'''
def getSampleTotalsAndProportions(records, samples, sampleFeature, selectedFeature, allValues, selectedValues):
    for record in records:
        for sample in samples:
            if(record[sampleFeature] == sample['Sample Name']):
                try:
                    if(record[selectedFeature] in allValues):
                        sample['Total'] += 1
                    if(record[selectedFeature] in selectedValues):
                        sample['Frequency'] += 1
                    break
                except KeyError:
                    sample['Total'] += 0
                    sample['Frequency'] += 0
                    sample['KeyError'] = "Selected feature not found for sample"
    for sample in samples:
        if(float(sample['Total']) == 0):
            sample['Proportion'] = 0
            sample['TotalError'] = "Sample total is 0"
        else:
            sample['Proportion'] = float(sample['Frequency']) / float(sample['Total'])

        
'''
Get the total number (N) and frequency (F) of the population

N is the number of records in the population who answered any valid value in the selected feature
F is the number of records in the population who answered any of the chosen values in the selected feature
'''
def getPopTotalsAndProportions(records,selectedFeature,allValues,selectedValues):
    population = {'Total':0, 'Frequency':0}
    for record in records:
        try:
            if(record[selectedFeature] in allValues):
                population['Total'] += 1
            if(record[selectedFeature] in selectedValues):
                population['Frequency'] += 1
        except KeyError:
            population['Total'] += 0
            population['Frequency'] += 0
            population['KeyError'] = "Selected feature not found for population"
    if(float(population['Total']) == 0):
        population['Proportion'] = 0
        population['TotalError'] = "Population total is 0"
    else:
        population['Proportion'] = float(population['Frequency']) / float(population['Total'])
    return population


'''
Calculate the standard error.
'''
def getStandardError(p,n):
    if(float(n) == 0):
        return 0
    else:
        return math.sqrt( (p * (1-p)) / float(n))

'''
Calculate the z-score between a sample and the population
'''
def getZScore(sample, population):
    se = getStandardError(population['Proportion'], sample['Total'])
    if se == 0:
        z = 0
        return z, se
    z = (sample['Proportion'] - population['Proportion']) / se

    return z,se
'''
Write the results of samples vs population in a file
'''
def makeResults(header, samples, population, zCriticalValue, fileName):
    rows = []
    rows.append(header)
    for sample in samples:
        tempRow = []
        tempRow.append(population['Total'])
        tempRow.append(population['Frequency'])
        tempRow.append(population['Proportion'])
        tempRow.append(sample['Sample Name'])
        tempRow.append(sample['Total'])
        tempRow.append(sample['Frequency'])
        tempRow.append(sample['Proportion'])
        tempRow.append(sample['Standard Error'])
        tempRow.append(zCriticalValue)
        tempRow.append(sample['Lower Bound'])
        tempRow.append(sample['Upper Bound'])
        tempRow.append(sample['Accept or Reject'])
        rows.append(tempRow)
    
    writeOnCSV(rows, fileName)


'''
This method is similar but returns a result from a sample which shows
the Z-Score for a particular variable. 
'''
def sampleVsPopulationSpecific(popDataset, sampleFeature, sampleValue, selectedFeature, allValues, selectedValues, zCriticalValue, strDelim):
    population_dataset = popDataset#Get population dataset

    sample = {'Sample Name':sampleValue, 'Total':0, 'Frequency':0} #Create sample
    
    allValues = allValues.split(strDelim)
    selectedValues = selectedValues.split(strDelim)

    samples = []
    samples.append(sample)

    getSampleTotalsAndProportions(population_dataset, samples, sampleFeature, selectedFeature, allValues, selectedValues)

    population = getPopTotalsAndProportions(population_dataset, selectedFeature, allValues, selectedValues)

    for sample in samples:
        #Perform Z-Test and Standard Error of Sample Proportion vs the population
        zScore, standardError = getZScore(sample,population)#Retrieve the z-score of the sample and the standard error to the population
        sample['Z'] = zScore
        sample['Standard Error'] = standardError
        sample['Upper Bound'] = sample['Proportion'] + (zCriticalValue * sample['Standard Error'])
        sample['Lower Bound'] = sample['Proportion'] - (zCriticalValue * sample['Standard Error'])
        if(population['Proportion'] >= sample['Lower Bound'] and population['Proportion'] <= sample['Upper Bound']):
            sample['Accept or Reject'] = 'Accept'
        else:
            sample['Accept or Reject'] = 'Reject'
    
    tempRow = []
    tempRow.append(selectedFeature)
    tempRow.append(population['Total'])
    tempRow.append(population['Frequency'])
    tempRow.append(population['Proportion'])
    tempRow.append(sample['Sample Name'])
    tempRow.append(sample['Total'])
    tempRow.append(sample['Frequency'])
    tempRow.append(sample['Proportion'])
    tempRow.append(sample['Standard Error'])
    tempRow.append(sample['Z'])
    tempRow.append(zCriticalValue)
    tempRow.append(sample['Lower Bound'])
    tempRow.append(sample['Upper Bound'])
    tempRow.append(sample['Accept or Reject'])

    sampleKeyList = sample.keys()
    popKeyList = population.keys()

    if 'KeyError' in sampleKeyList:
        tempRow.append(sample['KeyError'])
    if 'TotalError' in sampleKeyList:
        tempRow.append(sample['TotalError'])
    if 'KeyError' in popKeyList:
        tempRow.append(population['KeyError'])
    if 'TotalError' in popKeyList:
        tempRow.append(population['TotalError'])

    return tempRow
    



'''
Call this method to initiate the Sample vs Population
'''
def sampleVsPopulation(popDatasetPath, sampleFeature, selectedFeature, allValues, selectedValues, zCriticalValue):
    delimiter = ':'
    
    records = readCSVDict(popDatasetPath) #Read records from the population dataset file

    samples = []

    makeSamples(records, sampleFeature,samples)#Make the samples from the population raw dataset

    records = readCSVDict(popDatasetPath) #Read the records again because for some reason they disappear after making the sample groups
    print "All values: " + allValues
    print "Selected values: " + selectedValues
    allValues = allValues.split(":")
    selectedValues = selectedValues.split(":")
    getSampleTotalsAndProportions(records, samples, sampleFeature, selectedFeature, allValues, selectedValues)#Calculate n, f, and p of the samples

    records = readCSVDict(popDatasetPath) #Read the records again because for some reason they disappear after making the sample groups

    population = getPopTotalsAndProportions(records,selectedFeature,allValues,selectedValues)#Make the population and calculate N, F, and P of the population

    for sample in samples:
        #Perform Z-Test and Standard Error of Sample Proportion vs the population
        zScore, standardError = getZScore(sample,population)#Retrieve the z-score of the sample and the standard error to the population
        sample['Z'] = zScore
        sample['Standard Error'] = standardError
        sample['Upper Bound'] = sample['Proportion'] + (zCriticalValue * sample['Standard Error'])
        sample['Lower Bound'] = sample['Proportion'] - (zCriticalValue * sample['Standard Error'])
        if(population['Proportion'] >= sample['Lower Bound'] and population['Proportion'] <= sample['Upper Bound']):
            sample['Accept or Reject'] = 'Accept'
        else:
            sample['Accept or Reject'] = 'Reject'

    

    header = ['N','F','P','Sample','n','f','p','SE','Z Score','Z Critical Value','LB','UB','Accept/Reject']
    saveFile = 'Sample vs Population_'+sampleFeature+'_'+selectedFeature+'.csv'
    makeResults(header, samples, population, zCriticalValue, saveFile)

    return saveFile






