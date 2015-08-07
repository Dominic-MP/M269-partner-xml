import csv

with open('06 - M269-objects-001-for-jim.tsv', 'r') as log :
	readfile = csv.reader(log, delimiter= '\t')
	
	for row in readfile:
		directory = row[4]
		with open('objects/' + directory + '.tsv', 'a') as write:
			writelog = csv.writer(write, delimiter= '\t', quoting=csv.QUOTE_ALL)
			writelog.writerow( (row) )