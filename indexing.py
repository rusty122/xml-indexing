# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
# Designed for computers running Ubuntu, I guess, but probably pretty portable #
#                                                                              #
################################################################################


# Add your local path to the indexing folder (git foldser) and update currentUser
# In addition, create a folder called `files` in this folder (which is left 
# untracked in the .gitignore file) where outputted xml files will be saved
paths = { 
            'Nolan'  : '/home/nolan/Documents/work/indexing/',
            'Russell' : '/home/russell/Desktop/indexing/'
        }

currentUser = 'Nolan'
wordpressExportPath = paths[currentUser] + 'jomi.wordpress.2015-06-11.xml'
jinjaTemplatePath   = paths[currentUser] + 'JOMI-8.xml'

# Define a dictionary of the namespaces used in the xml file generated by 
#    WordPress to make ET.find(), ET.findall(), or ET.iterfind() more simple
namespace = {'wp':'http://wordpress.org/export/1.2/',
            'content':'http://purl.org/rss/1.0/modules/content/'}

import sys
import jinja2
import codecs
from datetime import datetime
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


# getMetaData(): loop through every element in the article with the tag 
#                wp:postmeta parse the production id and the hospital name, and
#                finally save this data to the dictionary
def getMetaData(data, article):
    for metaObject in article.findall('wp:postmeta', namespace):
        # If the text in the meta_key tag is "production_id" 
        # save the meta_value tag text in our dictionary as "production_id"
        if metaObject.find('wp:meta_key', namespace).text == "production_id":
            data['production_id'] = metaObject.find('wp:meta_value', namespace).text
        # Otherwise, if the text in the meta_key tag is "hospital_name"
        # save the text of meta_value tag in our dictionary as "affiliation"
        elif metaObject.find('wp:meta_key', namespace).text == "hospital_name":
            data['affiliation'] = metaObject.find('wp:meta_value', namespace).text


# Pubdate(): Find and parse publication date information from the article into
#             day, month, and year dictionary items, and save this in the data object
def pubdate(data, elem):
    try:
        publicationDate = datetime.strptime(elem.find('pubDate').text[:-6], '%a, %d %b %Y %H:%M:%S')
    except:
        print 'Failed to parse publication date for ' + data['title']
        publicationDate = datetime.now()

    data['pub_year']  = publicationDate.strftime('%Y')
    data['pub_month'] = publicationDate.strftime('%m')
    data['pub_day']   = publicationDate.strftime('%d')


# parseLastName(): If the author's name is saved with `MD` or `PHD` in WP, drop
#                    this to store in the dictionary
def parseLastName(name):
    commas = name.split(',')[0]
    names = commas.split(' ')
    name = ''
    suffix = ''
    for i in range(len(names)):
        if names[i].upper() != 'MD' and names[i].upper() != 'PHD':
            if i > 0:
                name += ' '
            name += names[i]
        else:
            suffix += ' '.join(names[i:])
            break
    if len(commas) > 1:
        suffix += ' ' + ','.join(commas[1:])
    return name, suffix.strip()


# getAuthors(): Parse the firstname, lastname, and initials of the authors of
#                the article and save this to the dictionary as a single tuple
def getAuthors(data, elem):   
    # get the authors' JoMI username
    author_usernames = elem.findall('category[@domain="author"]')
    # loop through author listings at beginning of xml doc
    data['authors'] = []
    for usernameElem in author_usernames :
        username = usernameElem.text
        for i in tree.iterfind('channel/wp:author', namespace):
            if i.find('wp:author_login', namespace).text == username:
                first_name = i.find('wp:author_first_name', namespace).text
                last_name, suffix  = parseLastName(i.find('wp:author_last_name', namespace).text)
            
                data['authors'].append({
                    'first_name': first_name,
                    'last_name' : last_name,
                    'initials'  : first_name[0] + last_name[0],
                    'suffix'    : suffix
                })
                break


def addReasonableNewlines(s, tabCount):
    s = s.strip()
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
    newString = newString.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return newString


def getOLBullet(olType, num):
    olType = olType%2
    b = ' '*4*olType
    if(olType == 0):
        b += str(num)
    elif(olType == 1):
        num = num % 52
        if(num < 26):
            b += chr(num + ord('a') - 1)  
        else:
            b += chr(num + ord('A') - 27)
    return b + '. '


def getULBullet(ulType):
    ulBullets = ['*','~', '-', '+']
    ulType = ulType%4
    return ' '*4*ulType + ulBullets[ulType] +' '


def parseOrderedList(ol, tabCount, olType = 0, numberingOffset = 0):
    i = numberingOffset + 1
    textContent = ''
    #print 'tag element:',ol, ol.attrib
    for listElem in ol:
        if(listElem.tag == 'li'):
            textContent += '\n' + (' '*(tabCount+1)*4) + getOLBullet(olType, i) + ''.join(listElem.itertext()).strip()
            i += 1
        elif(listElem.tag == 'ol'):

            #print 'child element:',listElem, listElem.attrib
            textContent += parseOrderedList(listElem, tabCount+1, olType+1)[0]
        elif(listElem.tag == 'ul'):
            textContent += parseUnorderedList(listElem, tabCount+1, 0)
            
    textContent += '\n' + (' '*(tabCount+1)*4) 
    textContent = textContent.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return (textContent, i-1)


def parseUnorderedList(ul, tabCount, ulType=0):
    textContent = ''
    for listElem in ul:
        if(listElem.tag == 'li'):
            textContent += '\n' + (' '*(tabCount+1)*4) + getULBullet(ulType) + ''.join(listElem.itertext()).strip()
        elif(listElem.tag == 'ol'):
            #print 'child element:',listElem, listElem.attrib
            textContent += parseUnorderedList(listElem, tabCount+1, 0)
        elif(listElem.tag == 'ul'):
            textContent += parseUnorderedList(listElem, tabCount+1, ulType+1)
            
    textContent += '\n' + (' '*(tabCount+1)*4) 
    textContent = textContent.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return textContent

# getOutline(): retrieve the Procedure Outline and return it as an elementTree
def getOutline(elem):
    for metaObject in elem.findall('wp:postmeta', namespace):
        if metaObject.find('wp:meta_key', namespace).text == "outline":
            content = metaObject.find('wp:meta_value', namespace).text.encode('utf-8').replace('<br>','<br/>')
            try:
                return ET.fromstring( '<?xml version="1.0" encoding="UTF-8" ?>\n' + '<body>\n' + content + '\n</body>' )
            except:
                return False
    return False


# renderAndSave(): create xml text with the jinja2 template engine and save it
#                  in the folder `files` with a title of its production_id
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
    # Skip article if it has not been published
    if not elem.find('wp:status', namespace).text == 'publish':
        continue
    # Initialize an empty dictionary that will hold all of the parsed data
    data = {}
    # Save the title, link, and pubdate of the article as dictionary entries
    data['title'] = elem.find('title').text
    data['link'] = elem.find('link').text
    
    getMetaData(data, elem)
    pubdate(data, elem)
    getAuthors(data, elem)

    # Skip article if the main text portion is empty
    if( elem.find('content:encoded', namespace).text == None):
        continue
    # Otherwise, create an elementTree from the main text
    content = elem.find('content:encoded', namespace).text.encode('utf-8').replace('<br>','<br/>')
    try:
        content = ET.fromstring( '<?xml version="1.0" encoding="UTF-8" ?>\n' + '<body>\n' + content + '</body>' )    
    except:
        print  '<?xml version="1.0" encoding="UTF-8" ?>\n' + '<body>\n' + content + '</body>'
        continue
    
    # Start parsing and formatting the main text of the article
    textContent = ""
    discussion = False
    abstract   = False
    reading    = False
    inSection  = False
    data['sections'] = []
    data['abstract'] = ''
    
    tabCount = 5
    for tag in content:
        if tag.tag == 'h4':
            if reading:
                if abstract:
                    data['abstract'] = textContent
                    abstract = False
                    #print textContent
                else:
                    textContent += '\n' + (' '*(tabCount )*4) + '</text>'
                    if inSection:
                        textContent += '\n' + (' '*(tabCount )*4) + '</section>'
                        
                    data['sections'].append({'title':sectionTitle, 'text': textContent})
                    if discussion:
                        break
            textContent = ""
            inSection = False
            if tag.text == "Abstract":
                abstract = True
                textContent = '\n'
            elif tag.text == "Discussion":
                discussion = True
                sectionTitle = tag.text
            else:
                sectionTitle = tag.text
            reading = True
            if len(tag.tail) > 0 :
                textContent += (' '*tabCount*4) + addReasonableNewlines(tag.tail, tabCount)
        elif tag.tag == 'ol':
            textContent += parseOrderedList(tag, tabCount+1)[0]
        elif tag.tag == 'ul':
            textContent += parseUnorderedList(tag, tabCount+1)
        else:
            newText = ''.join(tag.itertext())
            if len(newText) > 0:
                if tag.tag == 'h5':
                    if inSection:
                        textContent += '\n' + (' '*(tabCount + 1)*4) + '</text>'
                        textContent += '\n' + (' '*(tabCount )*4) + '</section>'
                    else:
                        textContent += '\n' + (' '*(tabCount )*4) + '</text>'
                        inSection = True
                    textContent += '\n' + (' '*(tabCount )*4) + '<section>'
                    textContent += '\n' + (' '*(tabCount + 1)*4) + '<title>'
                    textContent += newText.upper() + '</title>'
                    textContent += '\n' + (' '*(tabCount + 1)*4) + '<text>'
                    if len(tag.tail) > 0 :
                        textContent += (' '*tabCount*4) + addReasonableNewlines(tag.tail, tabCount)
                elif tag.tag == 'sup':
                    if len(tag.tail) > 0 :
                        textContent += (' '*tabCount*4) + addReasonableNewlines(tag.tail, tabCount)
                else:
                    textContent += (' '*tabCount*5) + addReasonableNewlines(newText, tabCount)
    
    # Parse and format the procedure outline of the article
    procedure = getOutline(elem)
    
    if(procedure):
        sectionTitle = 'Procedure'
        textContent = '\n'
        listCount = 0
        inSection = False
        for tag in procedure:
            if tag.tag == 'h4':
                if inSection:
                    textContent += '\n' + (' '*(tabCount + 1)*4) + '</text>'
                    textContent += '\n' + (' '*(tabCount )*4) + '</section>'
                else:
                    textContent += '\n' + (' '*(tabCount )*4) + '</text>'
                    inSection = True
                textContent += '\n' + (' '*(tabCount )*4) + '<section>'
                textContent += '\n' + (' '*(tabCount + 1)*4) + '<title>'
                textContent += newText.upper() + '</title>'
                textContent += '\n' + (' '*(tabCount + 1)*4) + '<text>'
                if len(tag.tail) > 0 :
                    textContent += (' '*tabCount*4) + addReasonableNewlines(tag.tail, tabCount)
                if len(tag.tail) > 0 :
                    textContent += (' '*tabCount*4) + addReasonableNewlines(tag.tail, tabCount)
            elif tag.tag == 'ol':
                newTextContent, listCount = parseOrderedList(tag, tabCount+1, 0, listCount)
                textContent += newTextContent
            elif tag.tag == 'ul':
                textContent += parseUnorderedList(tag, tabCount+1)
            else:
                newText = ''.join(tag.itertext())
                if len(newText) > 0:
                    if tag.tag == 'sup':
                        if len(tag.tail) > 0 :
                            textContent += (' '*tabCount*4) + addReasonableNewlines(tag.tail, tabCount)
                    else:
                        textContent += (' '*tabCount*4) + addReasonableNewlines(newText, tabCount)
        
        
        textContent += '\n' + (' '*(tabCount )*4) + '</text>'
        if inSection:
            textContent += '\n' + (' '*(tabCount )*4) + '</section>'
    
    data['sections'].append({'title':sectionTitle, 'text': textContent})
    
    renderAndSave( data )


# Provided notes: 
# The text for both the Main Text and the Procedure Outline would be appropriate.
# Do not include the citations, comments, disclosures, or statement of consent.
# Each document will need a unique identifier.  In the example, I used
# “JOMI-“ along with your identifier.  Adding “JOMI-“ before your
#  article ID will ensure there is no conflict with any other content we index.
# The section headings are not required, but many times they are themselves informative.
# You should provide a URL for linking