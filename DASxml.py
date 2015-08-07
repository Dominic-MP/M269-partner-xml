# -*- coding: utf-8 -*-
import csv, xml, re, time, os, datetime
import xml.etree.ElementTree as ET

x = 0
while x < 426:
	roll = 2 + x
	file = 'M269_' + str(roll).zfill(4)

## This part takes the partner XML and reformats it to more usable XML (i.e. going from attributes to elements - http://www.ibm.com/developerworks/library/x-eleatt/). The reformatted XML is saved as a new document with "_(reformatted)" appended to the name, so that the original file is not altered.

	with open('metadata/' + file + '_metadata.xml', 'r') as y :
		r = re.sub('<metadata name=\"(.*?)\" value=\"(.*?)\" />',r'<\1>\2</\1>', y.read())
		r = r.replace('Publication Number','Publication_Number')
		r = r.replace('Publication Title','Publication_Title')
		r = r.replace('Content Source','Content_Source')
		z = open(file + '_metadata_(reformatted).xml', 'w')
		z.write(r)
		z.close()
	
	tree = ET.parse(file + '_metadata_(reformatted).xml')
	root = tree.getroot()

	Publication_Number = root.find('Publication_Number').text
	Publication_Title = root.find('Publication_Title').text
	print str(datetime.datetime.now().time()) + ': ' + Publication_Number, Publication_Title, 'Roll ' + str(roll)

## This parses the XML for each page element. Default values for title components are "[BLANK]".
	try:
		for page in root.findall('page'):
			with open('objects/' + file + '.tsv', 'r') as log :
				readfile = csv.reader(log, delimiter= '\t')
		
				file_name = ''
				id = ''
				givenname = '[BLANK]'
				surname = '[BLANK]'
				age = '[BLANK]'
				year = '[BLANK]'
				military_unit = '[BLANK]'
				file_size = ''

				file_name = page.get('image-file-name')
				id = page.get('footnote-id')
				if page.find('givenname') is not None:
					givenname = page.find('givenname').text
				if page.find('surname') is not None:
					surname = page.find('surname').text
				if page.find('age') is not None:
					age = page.find('age').text
				if page.find('year') is not None:
					year = page.find('year').text
				if page.find('military-unit') is not None:
					military_unit = page.find('military-unit').text

	## Changes the given .jp2 file name to .jpg and adding the roll/publication information. Then, using the new file name extracted from partner data, look it up in the images CSV to extract file size, file path, and label flag fields.

				new_file_name = file + '_' + file_name[:-4] + '.jpg'
		
				for row in readfile:
					if new_file_name == row[0]:
						file_size = str(row[2])
						file_path = row[3]
						label_flag = row[5]

	## Generates the title based on the established formula.

				title = surname + ', ' + givenname + ' - Age ' + age + ', Year: ' + year + ' - ' + military_unit

	## Using all above parsed fields, generate the whole output XML document with 3 parts. XML_top (everything above the digital objects, since this will only appear once per title), digital_objects (so that it can repeat for each new page in the same title/file unit), and XML_bottom (completes each file unit).

				DASxml_top = """<fileUnit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">

<title>""" + title + """</title>

<parentSeries><naId>586957</naId></parentSeries>

<generalRecordsTypeArray><generalRecordsType><termName>Textual Records</termName></generalRecordsType></generalRecordsTypeArray>

<onlineResourceArray><onlineResource><termName>http://www.fold3.com/image/""" + id + """</termName><description>Fold3</description><note>This file was scanned as part of a collaboration effort between Fold3 and the National Archives.</note></onlineResource></onlineResourceArray>

<variantControlNumberArray><variantControlNumber><number>Fold3 2014</number><type><termName>Search Identifier</termName></type></variantControlNumber></variantControlNumberArray>

<microformPublicationArray><microformPublication><note>The start of this file can be found on Roll """ + str(roll) + """.</note><publication><termName>""" + Publication_Number + """ - """ + Publication_Title + """.</termName></publication></microformPublication></microformPublicationArray>

<dataControlGroup><groupCd>RDTP1</groupCd><groupId>ou=RDTP1,ou=groups</groupId></dataControlGroup>

<accessRestriction><status><termName>Unrestricted</termName></status></accessRestriction>

<useRestriction><status><termName>Unrestricted</termName></status></useRestriction>

<physicalOccurrenceArray><fileUnitPhysicalOccurrence>

<copyStatus><termName>Preservation-Reproduction-Reference</termName> </copyStatus><referenceUnitArray><referenceUnit><termName>National Archives at Washington, DC - Textual Reference</termName> </referenceUnit></referenceUnitArray>

<locationArray><location><facility><termName>National Archives Building - Archives I (Washington, DC)</termName> </facility></location></locationArray>

<mediaOccurrenceArray><mediaOccurrence><containerId></containerId><specificMediaType><termName>Paper</termName></specificMediaType>

<generalMediaTypeArray><generalMediaType><termName>Loose Sheets</termName></generalMediaType></generalMediaTypeArray>
</mediaOccurrence></mediaOccurrenceArray>

</fileUnitPhysicalOccurrence></physicalOccurrenceArray>

<digitalObjectArray>

"""

				digital_objects = """<digitalObject><objectType><termName>Image (JPG)</termName></objectType><labelFlag>""" + label_flag + """</labelFlag>
<objectDesignator>Fold3 File #""" + id + """</objectDesignator>
<objectDescription>Image provided by Fold3.</objectDescription>
<accessFilename>https://opaexport-conv.s3.amazonaws.com/""" + file_path + """</accessFilename><accessFileSize>""" + str(file_size) + """</accessFileSize>
<thumbnailFilename>http://media.nara.gov/dc-metro/jpg_t.jpg</thumbnailFilename><thumbnailFileSize></thumbnailFileSize></digitalObject>

"""
				DASxml_bottom = """</digitalObjectArray>
</fileUnit>

"""

## The final code: (1) creates a file for the DAS XML output if one does not yet exist, (2) writes each unique title to a separate CSV, (3) checks the CSV and writes DAS_top and digital_objects if the title is unique (it's a new file unit) or just digital_objects if it is not (it's an additional page within the current file unit), and then (4) writes the end tags for each completed file unit. It also logs each file unit in a separate log.txt, which is easier to read for progress than the full XML document.

				with open('uniquetest.csv', 'r') as log :
					test = False
					readlog = csv.reader(log, delimiter= '\t', quoting=csv.QUOTE_ALL)
					for row in readlog:
						if title == row[0]:
							test = True
							f = open('output.xml', 'a')
							f.write(digital_objects) 
							f.close()
							f = open('log.txt', 'a')
							f.write( '	' + '	' + label_flag + str(id) + str(file_size) + file_path + """
""") 
							f.close()
				if test is False:
					with open('uniquetest.csv', 'a') as write:
						writelog = csv.writer(write, delimiter= '\t', quoting=csv.QUOTE_ALL)
						writelog.writerow( (title, ) )

					try:
						f = open('output.xml', 'r')
						f = open('output.xml', 'a')
						f.write(DASxml_bottom + DASxml_top + digital_objects) 
						f.close()
						f = open('log.txt', 'a')
						f.write(title + str(roll) + label_flag + str(id) + str(file_size) + file_path + """
""") 
						f.close()
					except IOError:
						f = open('output.xml', 'a')
						f.write(DASxml_top + digital_objects) 
						f.close()
						f = open('log.txt', 'a')
						f.write(title + str(roll) + label_flag + str(id) + str(file_size) + file_path + """
""") 
						f.close()
	except IOError:
		print '   Error: OBJECTS NOT FOUND'
		pass
	x = x + 1
	os.remove(file + '_metadata_(reformatted).xml')
f = open('output.xml', 'a')
f.write(DASxml_bottom) 
f.close()