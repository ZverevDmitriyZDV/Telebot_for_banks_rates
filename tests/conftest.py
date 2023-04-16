import os


def pytest_configure(config):
    os.environ['BKKB_LOGS_FILE'] = ''
    os.environ['TINK_LOGS_FILE'] = ''

