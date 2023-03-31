import logging


class Zlogger:

    def __int__(self, name, log_file):
        self.name = name
        self.log_file = log_file

    @property
    def setup_logger(self, level=logging.DEBUG):
        """To setup as many loggers as you want"""

        handler = logging.FileHandler(filename=f'logs/{self.log_file}.log')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger = logging.getLogger(self.name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger



