import logging


class Zlogger:
    def __init__(self, filename):
        self.filename = filename

        logging.basicConfig(level=logging.DEBUG, filename=f'logs/{self.filename}.log')

        logging.basicConfig(format='%(asctime)s %(clientip)-15s:%(message)s')
