import logging
from logging.handlers import RotatingFileHandler
class MyLog():
    """Initialises the logger in my way"""
    def __init__(self, filename):
        log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

        logFile = filename

        my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                        backupCount=2, encoding=None, delay=0)
        my_handler.setFormatter(log_formatter)
        my_handler.setLevel(logging.INFO)

        self.app_log = logging.getLogger('root')
        self.app_log.setLevel(logging.INFO)

        self.app_log.addHandler(my_handler)
    
    def info(self, info):
        self.app_log.info(info)
    
    def error(self, error):
        self.app_log.error(error)