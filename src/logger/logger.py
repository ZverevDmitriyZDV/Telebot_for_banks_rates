import logging


class Zlogger(logging.Logger):

    def __init__(self, conf):
        super(Zlogger, self).__init__(conf.name, conf.log_level)
        self.log_file = conf.log_file
        self._setup_logger()
        self.config = conf

    def _setup_logger(self):
        """To setup as many loggers as you want"""
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
        logger = logging.getLogger(self.name)
        if self.log_file:
            logger.addHandler(logging.FileHandler(filename=f'logs/{self.log_file}.log'))
        return logger
