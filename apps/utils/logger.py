import logging
import os
import time
import sys
from logging import CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET

from colorama import Fore, Style

from MoonForum.settings import settings
from apps.utils.logger_utils import LoggerMode

default_mode = set()
default_mode.add(LoggerMode.console_mode)

class Logger(object):
	def __init__(self, logger, level, mode=default_mode):
		self.logger = logging.getLogger(name=logger)
		self.logger.setLevel(level)

		rq = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))
		log_path = os.path.join(settings['root'],settings['logger']['path'])
		log_name = os.path.join(log_path, rq + ".log")

		if not self.logger.handlers:


			for m in mode:
				if m == LoggerMode.console_mode:
					ch = logging.StreamHandler(sys.stdout)
					ch.setLevel(logging.DEBUG)
					formatter = logging.Formatter(
						"%(asctime)s - %(filename)s[line:%(lineno)d] - %(name)s - %(message)s")
					ch.setFormatter(formatter)
					self.logger.addHandler(ch)
				if m == LoggerMode.file_mode:
					fh = logging.FileHandler(log_name)
					fh.setLevel(logging.DEBUG)
					fh.setFormatter(formatter)
					self.logger.addHandler(fh)

	def debug(self, msg, *args, **kwargs):
		if self.logger.isEnabledFor(DEBUG):
			msg =Fore.CYAN + "DEBUG - " + str(msg) + Style.RESET_ALL
			self.logger._log(DEBUG, msg, args, **kwargs)

	def info(self, msg, *args, **kwargs):
		if self.logger.isEnabledFor(INFO):
			msg = Fore.GREEN + "INFO - " + str(msg) + Style.RESET_ALL
			self.logger._log(ERROR, msg, args, **kwargs)

	def warning(self, msg, *args, **kwargs):
		if self.logger.isEnabledFor(WARNING):
			msg = Fore.MAGENTA + "WARNING - " + str(msg) + Style.RESET_ALL
			self.logger._log(WARNING, msg, args, **kwargs)

	def error(self, msg, *args, **kwargs):
		if self.logger.isEnabledFor(ERROR):
			msg = Fore.RED + "ERROR - " + str(msg) + Style.RESET_ALL
			self.logger._log(ERROR, msg, args, **kwargs)

	def critical(self, msg,*args,**kwargs):
		if self.logger.isEnabledFor(CRITICAL):
			msg = Fore.LIGHTMAGENTA_EX + "CRITICAL - " + str(msg) + Style.RESET_ALL
			self.logger._log(CRITICAL, msg, args, **kwargs)


if __name__ == '__main__':
	log = Logger(logger="test", level=settings['logger']['level'])


	class t:
		def test_log(self):
			log.info('hi')


	tt = t()
	tt.test_log()
	log.debug("debug")
	log.info("info")
	log.error("error")
	log.warning("warning")
	log.critical("critical")
