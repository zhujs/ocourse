import unittest
import requests
import Queue 
import os
import mock

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

    def test_nativeDownloader(self):
        # create a mock session object
        mock_session = mock.create_autospec( requests.sessions.Session )

        # mocks the download process
        mock_dler = downloader.NativeDownloader( mock_session, self.task_queue )
        mock_dler.download( self.downAddress, self.path, self.name)

        reply = mock_session.get.return_value
        reply.headers.get.assert_called_once_with('content-length')


        # bad address
        dler = downloader.NativeDownloader(self.session, self.task_queue)
        self.assertRaises( downloader.DownloadError,
                dler.download, self.badAddress, 
                self.path, self.name )


    @mock.patch('ocourse.downloader.subprocess')
    def test_wgetDownloader( self, mock_subprocess):
        dler = downloader.WgetDownloader(self.session, 'wget')
        done = dler.download( self.downAddress, self.path, self.name ) 

        # the method subprocess.call is called
        self.assertTrue( mock_subprocess.call.called )

        done = dler.download( self.downAddress, self.path, self.name ) 
        self.assertFalse(done)


