
import sys

# check for required package for running the script
required_package = [ 'requests', 'bs4' ]  
missed_package = []

for package in required_package:
	try:
		__import__(package)
	except ImportError:
		missed_package.append( package )

# have some packages missing
if len(missed_package) != 0:
	msg = 'Module{0} required for running the script: [' #os.linesep 

	for package in missed_package:
		if package == 'bs4':
			package = 'beautifulsoup4'
		msg =  msg + ' ' + package
	msg += ' ]'

	sys.exit( msg.format( '' if len(missed_package) == 1 else 's' ) )


import argparse,os
import requests
import urlparse

import log
import utility
import downloader

# get the script logger
logger = log.getLogger( 'ocourse' )


def parse_argument( args=None ):
	"""Parse the arguments of the script"""
	parser = argparse.ArgumentParser( description='Script for downloading learning material at open.163.com.')

	parser.add_argument('-w', '--wget',
			action='store_true',
			default=False,
			dest='wget',
			help='Use the wget tools to download.')

	def is_valid_path( string ):
		# check for a valid directory
		if os.path.exists( string ) and not os.path.isdir( string ):
			raise argparse.ArgumentTypeError( 
					'The saved path should '
					'be a directory.')
		return string

	parser.add_argument('-p', '--path',
			action='store',
			default=None,
			type=is_valid_path,
			dest='saved_path',
			help='the saved path of the learning materials' )

	parser.add_argument('url',
			action='store',
			help='The required url of the learning material at open.163.com' )
			

	return parser.parse_args( args ) 




def main():
	arg = parse_argument()

	session = requests.Session()
	# get the html page of the desired url
	page = utility.get_url_page( session, arg.url )

	if page is None:
		return
	else:

		path = utility._get_saved_path( arg )

		# parse the page to obtain a download list
		downloadList = utility.parse_page( page )

		if len( downloadList ) == 0:
			sys.exit(1)

		dler = downloader.get_downloader( arg, session )

		assert dler is not None, 'No downloader!'

		# download all the resource in the parsed list

		logger.info( "Download start")
		for name, href in downloadList:
			try:
				if href == '':
					logger.info("Skipping %s: cannot find valid url", name)
				else:
					dler.download( href, path, name )

			except downloader.DownloadError as e:
				logger.error("Cannot download %s --> %s, %s", name, href, e )

		logger.info( "Download completed")




if __name__ == '__main__':
	main()



