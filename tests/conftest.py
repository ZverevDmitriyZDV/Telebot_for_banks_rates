import datetime
import os
import json

import pytest
from requests import Response
from tinkoff.invest import HistoricCandle, Quotation

from src.clients.bkkb_client import BKKBClient
from src.config.configurator import BKKBConfiguration


def pytest_configure(config):
    os.environ['BKKB_LOGS_FILE'] = ''
    os.environ['TINK_LOGS_FILE'] = ''


@pytest.fixture()
def get_last_data_response():
    return [{
        "Update": "2",
        "Time": "09:10     ",
        "Day": "24/04/2023"
    }]


@pytest.fixture()
def correct_client():
    conf = BKKBConfiguration(
        token="TOKEN",
        url="http://some_url",
    )
    return BKKBClient(conf=conf)


@pytest.fixture()
def incorrect_client():
    conf = BKKBConfiguration(
        token="INCORRECT_TOKEN",
        url="http://some_url",
    )
    return BKKBClient(conf=conf)


@pytest.fixture()
def get_family_response():
    return [{
        "Family": "USD1",
        "Description": "US Dollar 1-2"
    }, {
        "Family": "USD5",
        "Description": "US Dollar 5-20"
    }, {
        "Family": "USD50",
        "Description": "US Dollar 50-100"
    }, {
        "Family": "GBP",
        "Description": "Pound Sterling"
    }, {
        "Family": "EUR",
        "Description": "Euro"
    }, {
        "Family": "JPY",
        "Description": "Japanese Yen"
    }, {
        "Family": "HKD",
        "Description": "Hong Kong Dollar"
    }, {
        "Family": "MYR",
        "Description": "Malaysian Ringgit"
    }, {
        "Family": "SGD",
        "Description": "Singapore Dollar"
    }, {
        "Family": "BND",
        "Description": "Brunei Dollar"
    }, {
        "Family": "CNY",
        "Description": "Chinese Yuan"
    }, {
        "Family": "IDR",
        "Description": "Indonesian Rupiah"
    }, {
        "Family": "MMK",
        "Description": "Myanmar Kyat"
    }, {
        "Family": "INR",
        "Description": "Indian Rupee"
    }, {
        "Family": "KRW",
        "Description": "Korean Won"
    }, {
        "Family": "LAK",
        "Description": "Laos Kip"
    }, {
        "Family": "PHP",
        "Description": "Philippine Peso"
    }, {
        "Family": "TWD",
        "Description": "Taiwan Dollar"
    }, {
        "Family": "AUD",
        "Description": "Australian Dollar"
    }, {
        "Family": "NZD",
        "Description": "New Zealand Dollar"
    }, {
        "Family": "CHF",
        "Description": "Swiss Franc"
    }, {
        "Family": "DKK",
        "Description": "Danish Krone"
    }, {
        "Family": "NOK",
        "Description": "Norwegian Krone"
    }, {
        "Family": "SEK",
        "Description": "Swedish Krona"
    }, {
        "Family": "CAD",
        "Description": "Canadian Dollar"
    }, {
        "Family": "RUB",
        "Description": "Russia Ruble"
    }, {
        "Family": "VND",
        "Description": "Vietnam Dong"
    }, {
        "Family": "ZAR",
        "Description": "South Africa Rand"
    }, {
        "Family": "AED",
        "Description": "UAE Dirham"
    }, {
        "Family": "BHD",
        "Description": "Bahraini Dinar"
    }, {
        "Family": "OMR",
        "Description": "Rial Omani"
    }, {
        "Family": "QAR",
        "Description": "Qatari Riyal"
    }, {
        "Family": "SAR",
        "Description": "Saudi Riyal"
    }]


@pytest.fixture()
def get_lak_update_rates():
    return [{
        "Family": "LAK",
        "BuyingRates": "1.52      ",
        "SellingRates": "1.83      ",
        "SightBill": "-         ",
        "Bill_DD_TT": "-         ",
        "TT": "1.75        ",
        "Ddate": "04/03/2023",
        "DTime": ""
    }]


@pytest.fixture()
def get_usd_update_rates():
    return [{
        "Family": 'USD50',
        "BuyingRates": "81.52      ",
        "SellingRates": "82.83      ",
        "SightBill": "-         ",
        "Bill_DD_TT": "-         ",
        "TT": "81.75        ",
        "Ddate": "04/03/2023",
        "DTime": ""
    }]


@pytest.fixture()
def make_response_object():
    def wrap(data, status):
        the_response = Response()
        the_response._content = json.dumps(data).encode('utf8')
        the_response.status_code = status
        return the_response

    return wrap


@pytest.fixture
def tink_candles_history():
    return [
        HistoricCandle(open=Quotation(units=35548, nano=0), high=Quotation(units=35548, nano=0),
                       low=Quotation(units=35548, nano=0), close=Quotation(units=35548, nano=0), volume=1,
                       time=datetime.datetime(2023, 4, 3, 6, 0, tzinfo=datetime.timezone.utc), is_complete=True),
        HistoricCandle(open=Quotation(units=35547, nano=0), high=Quotation(units=35753, nano=0),
                       low=Quotation(units=35547, nano=0), close=Quotation(units=35682, nano=0), volume=18,
                       time=datetime.datetime(2023, 4, 3, 7, 0, tzinfo=datetime.timezone.utc), is_complete=True),
        HistoricCandle(open=Quotation(units=35693, nano=0), high=Quotation(units=35693, nano=0),
                       low=Quotation(units=35693, nano=0), close=Quotation(units=35693, nano=0), volume=1,
                       time=datetime.datetime(2023, 4, 3, 8, 0, tzinfo=datetime.timezone.utc), is_complete=True),
        HistoricCandle(open=Quotation(units=35690, nano=0), high=Quotation(units=35839, nano=0),
                       low=Quotation(units=35690, nano=0), close=Quotation(units=35839, nano=0), volume=8,
                       time=datetime.datetime(2023, 4, 3, 9, 0, tzinfo=datetime.timezone.utc), is_complete=True)]
