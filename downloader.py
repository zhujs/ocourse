
import threading, subprocess, time
import signal, fcntl, termios, array
import log
import requests
import Queue
import os,sys
import utility

logger = log.getLogger( 'ocourse' )



class DownloadError( BaseException ):
	"""Class to be thrown if error occurs when downloading"""
	pass


class ProgressBar( object ):
	"""A progress bar to show the download progress"""

	_default_term_width = 80
	def __init__(self, maxValue , prefix='', promptedChar='*', fd=sys.stderr ):
		if maxValue < 0:
			raise ValueError('Max value out of range')
		self.maxValue= maxValue 
		self.currentValue = 0 
		self.prefix= prefix
		self.promptedChar = promptedChar 
		self.fd = fd
		self.barString = u'{prefix} {perc:>6.1%} |{chars}|' 
		self.finished = False

		self.signal_set = False
		try:
			self._handle_resize()
			signal.signal( signal.SIGWINCH, self._handle_resize )
			
			self.signal_set = True
		except (SystemExit, KeyboardInterrupt): raise
		except:
			self.term_width = self._default_term_width

		# how many time we need to update the progress bar
		self.count_intervals = max( 100, self.term_width )
		self.next_update = 0

		self.update_interval = self.maxValue / self.count_intervals


	def _handle_resize( self, signum=None, frame=None ):
		"""Handler to window size change"""
		h,w = array.array('h',fcntl.ioctl(self.fd,termios.TIOCGWINSZ, '\0' * 8))[:2]
		self.term_width = w
		self.fd.write( self.format_line() + '\r' )
	
	def _need_update( self ):
		"""Whether we need to update the progress bar"""
		if self.currentValue >= self.next_update or self.finished:
			return True

		return False 

	def show( self, currentValue ):
		"""Show the current status of progress bar"""

		if not 0 <= currentValue <= self.maxValue :
			raise ValueError( 'Value out of range' )
		
		self.currentValue = currentValue

		if self._need_update():
			self.fd.write( self.format_line() + '\r' )

		
	def finish( self ):
		self.finished = True
		self.show( self.maxValue )
		self.fd.write( '\n' )
		self.currentValue = 0 

		if self.signal_set:
			signal.signal( signal.SIGWINCH, signal.SIG_DFL )
	

	def format_line( self ):
		"""Formats the current status of progress bar to string"""

		percentage = self.currentValue * 1.0 / self.maxValue

		# the minimum bar is : prefix + percentage + |*****|
		minimum_bar = self.barString.format( prefix=self.prefix,
				perc=percentage, 
				chars=self.promptedChar * 5 )

		if utility.get_string_width( minimum_bar ) < self.term_width:
			temp = self.barString.format( prefix=self.prefix,
					perc=percentage, 
					chars='')

			# calculate the length of maximum prompted chars 
			width = self.term_width - utility.get_string_width( temp ) 
		else:
			width = self.term_width

		# how many prompted chars should be print  
		markers = int( width * percentage ) * self.promptedChar
		return self.barString.format( prefix=self.prefix,
				perc=percentage, 
				chars=markers.ljust(width,' '))




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
					if os.path.getsize( save_path ) == int( content_length ):
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





