
import logging

class Logger:
    
    def __init__(self, name):

        self._level = logging.WARNING 

        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._level)

        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        self.console_handler = logging.StreamHandler()
        
        if not self.logger.hasHandlers():
            self.console_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.console_handler)

        self.logger.propagate = False
        
        # self.file_handler = logging.FileHandler('emmPipe.log')
        # self.file_handler.setFormatter(self.formatter)
        
        # self.logger.addHandler(self.file_handler)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):

        if value == 'DEBUG':
            value = logging.DEBUG
        elif value == 'INFO':
            value = logging.INFO
        elif value == 'WARNING':
            value = logging.WARNING
        elif value == 'ERROR':
            value = logging.ERROR
        elif value == 'CRITICAL':
            value = logging.CRITICAL
        else:
            raise ValueError('Invalid log level.')

        self._level = value
        self.logger.setLevel(value)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def exception(self, message):
        self.logger.exception(message)

    def set_level(self, level):
        self.logger.setLevel(level)

    def remove_console_handler(self):
        self.logger.removeHandler(self.console_handler)

    def remove_file_handler(self):
        self.logger.removeHandler(self.file_handler)