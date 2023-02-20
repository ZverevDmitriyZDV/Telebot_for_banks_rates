import logging


class Zlogger:
    def __init__(self, filename):
        self.filename = filename

    def logger_config(self):
        logging.basicConfig(level=logging.DEBUG, filename=f'logs/{self.filename}.log')

    def logger_format(self):
        logging.basicConfig(format='%(asctime)s %(clientip)-15s:%(message)s')
