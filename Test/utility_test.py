# -*- coding:utf-8 -*-
import unittest
import requests

from ocourse import utility

class TestUtilityFunction( unittest.TestCase ):
	
	def setUp( self ):
		self.url = 'http://v.163.com/special/opencourse/algorithms.html'
		self.noDownloadUrl = 'http://v.163.com/special/cuvocw/luojixue.html' 
		self.badurl = 'http://v.163.com/special/opencourse/oops.html'
		self.session = requests.Session()

	def test_get_url_page( self ):
		text = utility.get_url_page( self.session, self.badurl )
		self.assertIsNone( text )

		text = utility.get_url_page( self.session, self.url )
		self.assertIsNotNone( text )


	def test_parse_page( self ):
		page = utility.get_url_page( self.session, self.url )
		downloadList = utility.parse_page( page )
		self.assertEquals( len(downloadList), 24 )
		self.assertEqual( downloadList[0], ( u'001_课程简介及算法分析', 'http://mov.bn.netease.com/mobilev/2011/5/4/V/S72MEK54V.mp4' ) )
		
		page = utility.get_url_page( self.session, self.noDownloadUrl ) 
		downloadList = utility.parse_page( page )
		self.assertEqual( downloadList[0], ( u'001_逻辑学的对象与内容', '' ) )
