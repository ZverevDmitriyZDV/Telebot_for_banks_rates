import re
from datetime import datetime, timedelta

from src.config.configurator import BKKBConfiguration
from src.controllers.usd_contollers.bangkok_usd_thb_controller import LastUSDToTHBRates


def test_get_usd_to_thb_rate():
    conf = BKKBConfiguration()
    usd_to_thb = LastUSDToTHBRates(conf=conf)
    rate, message = usd_to_thb.get_usd_to_thb_rates()
    reg = r'(Update: )(\S*\s*\S*)'
    time_search = re.search(reg, message).group(0)[-10:]
    time_search = datetime.strptime(time_search, '%d/%m/%Y')
    time_delta = datetime.now() - time_search
    assert (rate, message) != (None, None)
    assert type(message) == str
    assert time_delta < timedelta(days=4)


def test_bad_auth_exception():
    bad_conf = BKKBConfiguration()
    bad_conf.token = 'INCORRECT_TOKEN'
    usd_to_thb_bad = LastUSDToTHBRates(conf=bad_conf)
    assert usd_to_thb_bad.get_usd_to_thb_rates() is None
