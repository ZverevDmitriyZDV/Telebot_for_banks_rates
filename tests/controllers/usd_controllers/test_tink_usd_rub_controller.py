import re
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.utils.bad_auth_exception import BadAuthException
from src.config.configurator import TinkBankConfiguration
from src.controllers.usd_contollers.tinkoff_usd_rub_controller import LastUSDToRUBRates


def test_bad_auth_get_usd_last_rate():
    bad_conf = TinkBankConfiguration(token='INCORRECT_TOKEN')
    usd_to_rub = LastUSDToRUBRates(bad_conf)
    usd_to_rub.client.get_usd_candles = MagicMock(side_effect=BadAuthException)
    assert usd_to_rub.get_usd_last_rate() is None


def test_get_usd_last_rate(tink_candles_history):
    conf = TinkBankConfiguration(
        token="TOKEN"
    )
    usd_to_rub = LastUSDToRUBRates(conf=conf)
    usd_to_rub.client.get_usd_candles = MagicMock(return_value=tink_candles_history)
    rate, message = usd_to_rub.get_usd_last_rate()
    reg = r'(Update : )(\S*\s*\S*)'
    time_search = re.search(reg, message).group(0)[-10:]
    time_search = datetime.strptime(time_search, '%d/%m/%Y')
    time_delta = datetime(day=4, month=3, year=2023) - time_search
    assert (rate, message) != (None, None)
    assert type(message) == str
    assert time_delta < timedelta(days=4)
