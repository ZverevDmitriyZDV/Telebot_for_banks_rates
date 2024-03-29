import pytest
from tinkoff.invest import AccountStatus
from tinkoff.invest.schemas import HistoricCandle

from pandas import DataFrame

from src.clients.tink_client import TinkoffBankClient
from src.utils.bad_auth_exception import BadAuthException
from src.config.configurator import TinkBankConfiguration


client_tink = TinkoffBankClient(conf=TinkBankConfiguration())


def test_incorrect_token():
    incorrect_config = TinkBankConfiguration(token='Incorrect_token')
    incorrect_client_tink = TinkoffBankClient(incorrect_config)
    assert incorrect_client_tink.token_name == 'Incorrect_token'
    with pytest.raises(BadAuthException) as e_info:
        incorrect_client_tink.get_data()


def test_check_correct_token():
    with client_tink.get_data() as cl:
        assert cl.users.get_accounts().accounts[0].status == AccountStatus.ACCOUNT_STATUS_OPEN


def test_get_all_figi_list():
    figi_list = client_tink.get_all_figi_list()
    assert len(figi_list) > 100

    data_frame = DataFrame(figi_list)
    ticker_1 = 'AVA'
    ticker_2 = 'CENT'

    def get_figi(df, ticker):
        value_by_ticker = df[df['ticker'] == ticker]
        return value_by_ticker['figi'].iloc[0]

    assert get_figi(data_frame, ticker_1) == 'BBG000BCNF74'
    assert get_figi(data_frame, ticker_2) == 'BBG000BFD605'


def test_get_candles_by_figi():
    figi_1 = 'BBG000BFD605'
    figi_2 = 'INCORRECT_FIGI_DATA'
    candles = client_tink.get_candles_by_figi(figi_1)
    assert candles is not None
    assert len(candles) > 2
    assert type(candles[0]) == HistoricCandle
    assert client_tink.get_candles_by_figi(figi_2) is None


def test_usd_candles():
    usd_candles = client_tink.get_usd_candles()
    assert usd_candles is not None
    assert len(usd_candles) > 2
    assert type(usd_candles[0]) == HistoricCandle
