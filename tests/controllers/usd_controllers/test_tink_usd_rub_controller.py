import re
from datetime import datetime, timedelta

from src.controllers.usd_contollers.tinkoff_usd_rub_controller import LastUSDToRUBRates


def test_get_usd_last_rate():
    usd_to_rub = LastUSDToRUBRates()
    rate, message = usd_to_rub.get_usd_last_rate()
    reg = r'(Update : )(\S*\s*\S*)'
    time_search = re.search(reg, message).group(0)[-10:]
    time_search = datetime.strptime(time_search, '%d/%m/%Y')
    time_delta = datetime.now() - time_search
    assert (rate, message) != (None, None)
    assert type(message) == str
    assert time_delta < timedelta(days=4)


def test_bad_auth_get_usd_last_rate():
    usd_to_rub = LastUSDToRUBRates()
    usd_to_rub.client.token_name = 'INCORRECT_TOKEN'
    assert usd_to_rub.get_usd_last_rate() is None
