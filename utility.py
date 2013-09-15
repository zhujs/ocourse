
import requests
import logging
import re

from bs4 import BeautifulSoup as BeautifulSoup_

try:
	import html5lib
except ImportError:
	BeautifulSoup = lambda page: BeautifulSoup_( page, 'html.parser' )
else:
	BeautifulSoup = lambda page: BeautifulSoup_( page, 'htmllib' )



def get_url_page( session, url):
	"""Make a HTTP get request for the specific url, return the html text as string"""

	try:
		reply = session.get(url)

		reply.raise_for_status()
	except ( requests.exceptions.InvalidSchema, 
			requests.exceptions.InvalidURL ) as e:
		logging.error( "Invalid URL for download: %s", url )
		return

	except requests.exceptions.HTTPError as e:
		logging.error( "Error occurs when getting the page %s: %s", url, e )
		return
	else:
		return reply.text


def _format_filename( prefix, name ):
	assert isinstance( prefix , unicode )
	matchObj = re.search( r'\d+', prefix )	
	
	if matchObj is None:
		logging.error( "Error occurs when formating the file name %s",
				prefix + name )
		return prefix + name

	episode = matchObj.group()
	assert isinstance( episode , unicode )

	return episode.zfill(3) + '_' + name



def parse_page( page ):
	"""Parse the resource page and get a download list""" 

	parser = BeautifulSoup( page )

	# find all table tags in the html page (according to the structure of html page) 
	tables = parser.find_all( 'table', id=re.compile('^list') )

	if tables is None:
		return

	downloadList = []
	try:
		# get the table containing all the resources ( table with the id 'list2' )
		allRows = tables[ len(tables)-1 ].find_all('tr')
		allRows = allRows[1:]
			
		for tr in allRows:
			td = tr.find_all( 'td' )
			name = _format_filename( td[0].contents[0].strip() , td[0].a.string.strip()  )
			if td[1].find( 'a' ):
				href = td[1].a.get( 'href' )
			else:
				href = ''

			downloadList.append( (name, href) )
	except Exception as e:
		logging.error('Error occurs when parsing: %s', e )
	else:
		return downloadList if len( downloadList ) else [] 




	

