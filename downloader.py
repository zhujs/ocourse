
import threading, subprocess
import log
import requests
import Queue
import os,sys

logger = log.getLogger( 'ocourse' )

class DownloadError( BaseException ):
	"""Class to be thrown if error occurs when downloading"""
	pass


class ProgressBar( object ):
	"""A progress bar to show the download progress"""

	_characterNum_default = 40

	def __init__(self, maxValue , prefix='', promptedChar='*', fd=sys.stderr ):
		self.maxValue= maxValue 
		self.currentValue = 0 
		self.characterNum = self._characterNum_default 
		self.prefix= prefix
		self.promptedChar = promptedChar 
		self.fd = fd


	def show( self, currentValue ):
		"""Show the current status of progress bar"""
		self.currentValue = currentValue
		self.fd.write( self.format_line() + '\r' )

		
	def finish( self ):
		self.show( self.maxValue )
		self.fd.write( '\n' )
		self.currentValue = 0 
	

	def format_line( self ):
		"""Formats the current status of progress bar to string"""
		bar = u'{0} {1}% |{2}{3}|' 

		percentage = round( self.currentValue / float( self.maxValue ) , 2 )

		nCompletedChar = int( percentage * self.characterNum )
		return bar.format( self.prefix, 
				percentage*100,
				self.promptedChar * nCompletedChar,
				' ' * ( self.characterNum - nCompletedChar ) )


	

'''
class DownloadThread( threading.Thread ):
	"""Thread used for downloading the video"""
	def __init__(self,session,  task_queue ):
		#super( DownloadThread, self ).__init__( self )
		threading.Thread.__init__( self )
		self.session = session
		self.task_queue = task_queue
		self.completed = False

	def download_completed( self ):
		return self.completed


	def run( self ):
		url, path, name = self.task_queue.get()
		
		if url is not None and url != '':
			# get the url resource
			reply = self.session.get( url, stream= True )

			try:
				reply.raise_for_status()
			except requests.exceptions.HTTPError as e:
				raise DownloadError( e )
			else:
				# get the content length
				content_length = reply.headers.get( 'content-length' )
				chunk_size = 2**20
				save_path = os.path.join( path, name)	

				assert isinstance( name, unicode )
				bar = ProgressBar( int(content_length), name  )

				with open( save_path, 'wb' ) as fileObj:
					data = reply.raw.read( chunk_size )
					received_length = len(data)

					while data != '':
						fileObj.write( data )
						received_length += len( data )
						bar.show( received_length )
						data = reply.raw.read( chunk_size )

				bar.finish()
				reply.close()
				self.completed = True
'''
				
class NativeDownloader( object ):
	def __init__( self , session , task_queue ):
		self.session = session
		self.task_queue = task_queue
	
	def download( self, url, path, name ):
		if url is not None and url != '':
			# get the url resource
			reply = self.session.get( url, stream= True )

			try:
				reply.raise_for_status()
			except requests.exceptions.HTTPError as e:
				raise DownloadError( e )
			else:
				# get the content length
				content_length = reply.headers.get( 'content-length' )
				chunk_size = 2**20

				save_path = os.path.join( path, name)
				if os.path.exists( save_path ):
					# if the size of the existing file is identical 
					if os.path.getsize( save_path ) == content_length:
						logger.info("Skipping %s: file exists" % name )
						return True
				

				assert isinstance( name, unicode )
				bar = ProgressBar( int(content_length), name  )

				# read the data and write to the file
				with open( save_path, 'wb' ) as fileObj:
					received_length = 0

					for data in reply.iter_content( chunk_size ):
						if data == '':
							break
						received_length += len(data)
						bar.show( received_length )
						fileObj.write( data )

				bar.finish()
				reply.close()
				return True



		
class ExternalDownloader( object ):
	def __init__( self , session, tools_name ):
		self.session = session
		self.tools = tools_name

	def _create_command( self, url, filename ):
		"""Create external command to download the material"""
		raise NotImplementedError("Subclasses should implement this class")

	def download( self, url, path, name ):
		filename = os.path.join( path, name )
		command = self._create_command( url , filename )

		try:
			exitcode = subprocess.call( command )
		except OSError as e:
			raise DownloadError(e)
		else:
			if exitcode:
				raise DownloadError('Error occurs:'
						'exit code: %d' % exitcode)
			else:
				return True 


class WgetDownloader( ExternalDownloader ):
	def __init__(self, session, tools ):
		super( WgetDownloader, self ).__init__( session, tools )
	
	def _create_command( self, url, filename ):
		"""Create the wget command to download the material"""
		return [ self.tools, url, '-O', filename ]



def get_downloader( arg, session ):
	task_queue = Queue.Queue()

	if arg.wget:
		return WgetDownloader( session, 'wget' )	
	else:
		return NativeDownloader( session, task_queue )





