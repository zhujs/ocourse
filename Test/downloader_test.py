import unittest
import requests
import Queue 
import os

from ocourse import downloader
#import downloader
class TestDownloaderClass( unittest.TestCase ):
	
	def setUp( self ):
		self.downAddress = 'http://mov.bn.netease.com/mobilev/2013/4/7/F/S8SCNR77F.mp4'
		self.session = requests.Session()
		self.task_queue = Queue.Queue()
		self.prefix = u'TestDownload01'
		self.task_queue.put( (self.downAddress, os.getcwd(), self.prefix ) )

	def test_downloadThread( self ):
		dThread = downloader.DownloadThread( self.session, self.task_queue )
		dThread.start()

		dThread.join()
		self.assertTrue( dThread.download_completed()  )


	def test_wgetDownloader( self ):
		dler = downloader.WgetDownloader( self.session, 'wget' )
		done = dler.download( self.downAddress, os.getcwd(), self.prefix )	
		
		self.assertTrue( done )


