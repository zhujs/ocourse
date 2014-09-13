# -*- coding: utf-8 -*-
import unittest
import time

from ocourse import downloader 

class TestDownloaderClass( unittest.TestCase ):
    
    def setUp( self ):
        self.maxValue = 300
        self.bar = downloader.ProgressBar( self.maxValue, 'c' * 40 ) 
        self.bar1 = downloader.ProgressBar( self.maxValue, u'中文' ) 

    def _show_bar( self, bar ):
        for i in xrange( self.maxValue ):
            time.sleep( 0.05 )
            bar.show( i )
        
        bar.finish() 
        self.assertEqual( bar.currentValue, 0)


    def test_progressbar( self ):
        self._show_bar( self.bar )
        self._show_bar( self.bar1 )
        




