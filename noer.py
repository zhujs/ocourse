#! /usr/bin/evn python


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
import logging

import utility
import downloader

def parse_argument( args=None ):
	"""Parse the arguments of the script"""
	parser = argparse.ArgumentParser( description='Script for downloading learning material at open.163.com.')

	parser.add_argument('-w', '--wget',
			action='store_true',
			default=False,
			dest='wget',
			help='Use the wget tools to download.')

	parser.add_argument('url',
			action='store',
			help='The url of the learning material at open.163.com' )
			

	return parser.parse_args( args ) 


def main():
	arg = parse_argument()

	session = requests.Session()
	# get the html page of the desired url
	page = utility.get_url_page( session, arg.url )

	if page is None:
		logging.info("Cannot get the url page.")
	else:
		# parse the page to obtain a download list
		downloadList = utility.parse_page( page )

		dler = downloader.get_downloader( arg, session )

		assert dler is not None, 'No downloader!'

		for name, href in downloadList:
			try:
				dler.download( href, os.getcwd(), name )
			except downloader.DownloadError:
				logging.info("Cannot download %s --> %s", name, href )

		logging.info( "Download complete.")




if __name__ == '__main__':
	main()



