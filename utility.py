
import requests
import log
import re, os

from bs4 import BeautifulSoup as BeautifulSoup_

try:
	import html5lib
except ImportError:
	BeautifulSoup = lambda page: BeautifulSoup_( page, 'html.parser' )
else:
	BeautifulSoup = lambda page: BeautifulSoup_( page, 'htmllib' )


logger = log.getLogger('ocourse')

def _get_saved_directory( url ):
	"""Get the saved directory from the url"""

	result = urlparse.urlparse( url )
	basename = os.path.basename( result.path )

	return os.path.splitext( basename )[0]

def _get_saved_path( arg ):
	"""Get the saved path for the resource"""

	# get the valid saved path
	if arg.saved_path is None:
		arg.saved_path = os.path.join( os.getcwd(),
				_get_saved_directory( arg.url ) )

	if not os.path.exists( arg.saved_path ):
		os.mkdir( arg.saved_path )
		
	assert os.path.isdir( arg.saved_path )
	return arg.saved_path

def get_url_page( session, url):
	"""Make a HTTP get request for the specific url, return the html text as string"""

	try:
		reply = session.get(url)

		reply.raise_for_status()
	except ( requests.exceptions.InvalidSchema, 
			requests.exceptions.InvalidURL ) as e:
		logger.error( "Invalid URL for download: %s", url )

	except requests.exceptions.HTTPError as e:
		logger.error( "Error occurs when getting the page ==> %s, %s", url, e )
	else:
		return reply.text


def _format_filename( prefix, name ):
	assert isinstance( prefix , unicode )
	matchObj = re.search( r'\d+', prefix )	
	
	if matchObj is None:
		logger.info( "Cannot format the file name %s",
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
		return [] 

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
		logger.error("Cannot find any resource to download for the given url")
		return []
	else:
		return downloadList 




	

