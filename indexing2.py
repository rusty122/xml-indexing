# -*- coding: utf-8 -*-

################################################################################
#																			   #
# Designed for computers running Ubuntu, I guess, but probably pretty portable #
#																			   #
################################################################################


#add the path on your computer to the indexing folder ad set currentUser to you

paths = { 
			'Nolan'  : '/home/nolan/Documents/work/indexing/',
			'Russel' : '/home/russel/Desktop/indexing/'
		}

currentUser = 'Nolan'

wordpressExportPath = paths[currentUser] + 'jomi.wordpress.2015-06-11.xml'
jinjaTemplatePath   = paths[currentUser] + 'JOMI-8.xml'



import sys
import jinja2
import codecs
from datetime import datetime
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# Define namespaces dictionary to make ET.find() or ET.findall() more simple
namespace = {'wp':'http://wordpress.org/export/1.2/',
			 'content':'http://purl.org/rss/1.0/modules/content/'}


# loop through every element in the article with the tag wp:postmeta
# and save necessary data to the dictionary
def getMetaData(dict, article):
	for metaObject in article.findall('wp:postmeta', namespace):
		# If the text in the meta_key tag is "production_id" 
		# save the meta_value tag text in our dictionary as "production_id"
		if metaObject.find('wp:meta_key', namespace).text == "production_id":
			data['production_id'] = metaObject.find('wp:meta_value', namespace).text
		# Otherwise, if the text in the meta_key tag is "hospital_name"
		# save the text of meta_value tag in our dictionary as "affiliation"
		elif metaObject.find('wp:meta_key', namespace).text == "hospital_name":
			dict['affiliation'] = metaObject.find('wp:meta_value', namespace).text


def pubdate(data, elem):
	try:
		publicationDate = datetime.strptime(elem.find('pubDate').text[:-6], '%a, %d %b %Y %H:%M:%S')
	except:
		print 'Failed to parse publication date for ' + data['title']
		publicationDate = datetime.now()
   
	data['pub_year']  = publicationDate.strftime('%Y')
	data['pub_month'] = publicationDate.strftime('%m')
	data['pub_day']   = publicationDate.strftime('%d')
   
# The last name occasionally has MDs and PHDs in it
def parseLastName(name):
	name = name.split(',')[0]
	names = name.split(' ')
	name = ''
	for i in range(len(names)):
		if names[i].upper() != 'MD' and names[i].upper() != 'PHD':
			if i > 0:
				name += ' '
			name += names[i]
		else:
			break
	return name


def getAuthors(data, elem):   
	# get the author's JoMI username (use findall() if multiple authors exist?)
	author_usernames = elem.findall('category[@domain="author"]')
	# loop through author listings at beginning of xml doc
	data['authors'] = []
	for usernameElem in author_usernames :
		username = usernameElem.text
		for i in tree.iterfind('channel/wp:author', namespace):
			if i.find('wp:author_login', namespace).text == username:
				first_name = i.find('wp:author_first_name', namespace).text
				last_name  = parseLastName(i.find('wp:author_last_name', namespace).text)
               
				data['authors'].append({
					'first_name': first_name,
					'last_name' : last_name,
					'initials'  : first_name[0] + last_name[0]
				})
				break

def addReasonableNewlines(s, tabCount):
	length = len(s)
	newString = ''
	pos = 0
	while(length > pos + 80):
		newLength = 70
		while(length > pos + newLength and s[pos + newLength]!=' '):
			newLength += 1
		newString += s[pos:pos+newLength] + '\n' + (' '*tabCount*4)
		pos += newLength +1
	newString += s[pos:] + '\n'
	return newString



# save xml file with specified title that contains `text`
def renderAndSave( data ):
	templateLoader = jinja2.FileSystemLoader( searchpath="/" )
	templateEnv = jinja2.Environment( loader=templateLoader )
	TEMPLATE_FILE = jinjaTemplatePath
	template = templateEnv.get_template( TEMPLATE_FILE )
	file = codecs.open('files/' + data['production_id'] + '.xml', 'w', encoding='utf8')
	file.write( template.render(data) )
	file.close()



# Create ElementTree object from xml file
tree = ET.ElementTree(file=wordpressExportPath)

# For each article in the ElementTree object
for elem in tree.iterfind('channel/item'):
	# skip article if it is still in preprint
	if not elem.find('wp:status', namespace).text == 'publish':
		continue
	# Initialize an empty dictionary that will hold all of the parsed data
	data = {}
	# Save the title, link, and pubdate of the article as dictionary entries
	data['title'] = elem.find('title').text
	data['link'] = elem.find('link').text
	
	debug = False
	if data['title'] == 'Cervical Laminaplasty':
		debug = True
     
	getMetaData(data, elem)
	pubdate(data, elem)
	getAuthors(data, elem)
	if( elem.find('content:encoded', namespace).text == None):
		#print data['title']
		continue
	
	content = elem.find('content:encoded', namespace).text.encode('utf-8').replace('<br>','<br/>')
	try:
		content = ET.fromstring( '<?xml version="1.0" encoding="UTF-8" ?>\n' + '<body>\n' + content + '</body>' )	
	except:
		print  '<?xml version="1.0" encoding="UTF-8" ?>\n' + '<body>\n' + content + '</body>'
		continue
	
	textContent = ""
	discussion = False
	abstract   = False
	reading    = False
	data['sections'] = []
	data['abstract'] = ''
	
	tabCount = 5
	for tag in content:
		if tag.tag == 'h4':
			if reading:
				textContent = addReasonableNewlines(textContent, tabCount)
				if abstract:
					data['abstract'] = textContent
					abstract = False
					#print textContent
				else:
					data['sections'].append({'title':sectionTitle, 'text': textContent})
					if discussion:
						break
			if tag.text == "Abstract":
				abstract = True
				#print "Abstract!!"
			elif tag.text == "Discussion":
				discussion = True
				sectionTitle = tag.text
			else:
				sectionTitle = tag.text
			textContent = ""
			reading = True
		elif tag.tag == 'ol':
			i = 0
			for listElem in tag.findall('*'):
				textContent += '\n' + (' '*(tabCount+1)*4) + str(i) +'. ' + listElem.text
				i += 1
		elif tag.text != None:
			if tag.tag == 'h5':
				textContent += '\n' + (' '*tabCount*4) + tag.text.strip().upper()+'.\n' + (' '*tabCount*4)
			else:
				textContent += tag.text
	
	#if(debug):
		#print data['abstract']
	if len(data['sections']) == 1 :
		print data['title']
	renderAndSave( data )


# parse the necessary data into a dictionary
	# tough part of this is the actual content
	# thinking about actually switching over to pulling data straight from MySQL
	# the xml file that WordPress generates contains an entire xml doc of formatted
		# text in the contents section
	# Would need to find a way to generate bullet points or numbered lists for 
		# <ul> and <ol> respectively
	# Here's a possible solution I see: filter through the content to get rid 
		# of unwanted sections
	# Feed this data into an xml to plain-text converter
	# Still need to make arrays of titles and corresponding text to feed into the template engine
# render an xml file with the dictionary as the argument
# save file with unique name in specific folder


# Notes: 
# The text for both the Main Text and the Procedure Outline would be appropriate.
# Do not include the citations, comments, disclosures, or statement of consent.
# Each document will need a unique identifier.  In the example, I used
# “JOMI-“ along with your identifier.  Adding “JOMI-“ before your
#  article ID will ensure there is no conflict with any other content we index.
# The section headings are not required, but many times they are themselves informative.
# You should provide a URL for linking.