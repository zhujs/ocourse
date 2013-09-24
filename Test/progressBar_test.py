
import unittest
import time

from ocourse import downloader 

class TestDownloaderClass( unittest.TestCase ):
	
	def setUp( self ):
		self.maxValue = 300
		self.bar = downloader.ProgressBar( self.maxValue, 'c' * 40 ) 

	def test_progressbar( self ):
		
		for i in xrange( self.maxValue ):
			time.sleep( 0.05 )
			self.bar.show( i )
		
		self.bar.finish() 
		self.assertEqual( self.bar.currentValue, 0)




