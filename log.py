
import logging, sys 
import logging.config

# The configuration dict for the downloading script

_CONFIG = {
	'version' : 1,	
	'disable_existing_loggers' : True,

	'formatters' : {
		'standard' : {
			'format' : '[ %(levelname)s ] : %(message)s',
		},	
	},

	'handlers' : {
		'console' : {
			'level' : 'INFO',		
			'class' : 'logging.StreamHandler',
			'formatter' : 'standard',
			'stream' : sys.stdout,
		},
	
	},
		

	'loggers' : {
		'ocourse' : {
			'level' : 'INFO',
			'handlers': ['console'],
			'propagate' : True,
		},

	},
}


logging.config.dictConfig( _CONFIG )

# logging.getLogger( 'ocourse' ).addHandler( logging.NullHandler() ) 

# function to get the loggers
def getLogger( name ):
	return logging.getLogger( name )


if __name__  == '__main__':
	logger = getLogger( 'ocourse' )

	logger.info( 'Ifno message' )
	logger.error( 'Error message' )
