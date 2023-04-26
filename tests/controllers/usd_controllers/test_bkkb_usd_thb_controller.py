import re
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.utils.bad_auth_exception import BadAuthException
from src.config.configurator import BKKBConfiguration
from src.controllers.usd_contollers.bangkok_usd_thb_controller import LastUSDToTHBRates


def test_get_usd_to_thb_rate(get_last_data_response, get_usd_update_rates, make_response_object):
    conf = BKKBConfiguration(token="TOKEN")
    usd_to_thb = LastUSDToTHBRates(conf=conf)
    fake_response_update = make_response_object(get_last_data_response, 200)
    fake_response_get_x = make_response_object(get_usd_update_rates, 200)
    usd_to_thb.client.format_update_data = MagicMock(return_value=fake_response_update)
    usd_to_thb.client.get_x_rate = MagicMock(return_value=fake_response_get_x)
    rate, message = usd_to_thb.get_usd_to_thb_rates()
    reg = r'(Update: )(\S*\s*\S*)'
    time_search = re.search(reg, message).group(0)[-10:]
    time_search = datetime.strptime(time_search, '%d/%m/%Y')
    time_delta = datetime(day=4, month=3, year=2023) - time_search
    assert (rate, message) != (None, None)
    assert type(message) == str
    assert time_delta < timedelta(days=4)


def test_bad_auth_exception():
    bad_conf = BKKBConfiguration(token='TOKEN')
    usd_to_thb_bad = LastUSDToTHBRates(conf=bad_conf)
    usd_to_thb_bad.client.format_update_data = MagicMock(side_effect=BadAuthException)
    assert usd_to_thb_bad.get_usd_to_thb_rates() is None
