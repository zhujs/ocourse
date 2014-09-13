import unittest
import requests
import Queue 
import os

from ocourse import downloader
#import downloader
class TestDownloaderClass( unittest.TestCase ):
    
    def setUp( self ):
        self.downAddress = 'http://mov.bn.netease.com/mobilev/2013/4/7/F/S8SCNR77F.mp4'
        self.badAddress = 'http://mov.bn.netease.com/nonexist.mp4'
        self.session = requests.Session()
        self.task_queue = Queue.Queue()
        self.path = u'download'
        self.name = u'TestDownload01'

        try:
            os.mkdir(self.path);
        except:
            pass


    def test_nativeDownload( self ):
        dler= downloader.NativeDownloader( self.session, self.task_queue )
        done = dler.download( self.downAddress, self.path, self.name)
        self.assertTrue( done )

        self.assertRaises( downloader.DownloadError,
                dler.download, self.badAddress, 
                self.path, self.name )

        # what happen if the file exists
        done = dler.download( self.downAddress, self.path, self.name)
        self.assertTrue( done )

    def test_wgetDownloader( self ):
        dler = downloader.WgetDownloader( self.session, 'wget' )
        done = dler.download( self.downAddress, self.path, self.name )    
        
        self.assertTrue( done )
        self.assertRaises( downloader.DownloadError,
                dler.download, self.badAddress, 
                self.path, self.name )


