import pytest
import datetime

from pandas import DataFrame

from src.clients.bkkb_client import BKKBClient


def test_correct_token():
    bkkb_client = BKKBClient()
    response = bkkb_client.get_data('ServiceVersion')
    assert response.status_code == 200
    assert type(response.json()) == str


def test_incorrect_token():
    bkkb_client = BKKBClient()
    bkkb_client.token = 'INCORRECT_TOKEN'
    response = bkkb_client.get_data('ServiceVersion')
    assert response.status_code == 401
    assert response.json().get('message') is not None


def test_last_update():
    bkkb_client = BKKBClient()
    response = bkkb_client.get_last_update()
    now = datetime.datetime.now().strftime('%d/%m/%Y')
    assert response.status_code == 200
    assert response.json()[0].get('Day')[2:] == now[2:]


def test_get_all_families():
    bkkb_client = BKKBClient()
    response = bkkb_client.get_all_values_families()
    assert response.status_code == 200
    assert len(response.json()) > 10

    data_frame = DataFrame(response.json())
    ticker_1 = 'Laos Kip'
    ticker_2 = 'INCORRECT_VALUE'

    def get_family(df, ticker):
        value_by_ticker = df[df['Description'] == ticker]
        return value_by_ticker['Family'].iloc[0]

    assert get_family(data_frame, ticker_1) == 'LAK'
    with pytest.raises(IndexError) as e_info:
        get_family(data_frame, ticker_2)


def test_last_rate_update():
    bkkb_client = BKKBClient()
    response = bkkb_client.get_last_all_rate_update_for_value(dict(day='02', month='04', year='2023'), 'LAK')
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0].get('Family') is not None


def test_last_rate_update_incorrect_value():
    bkkb_client = BKKBClient()
    ticker_incorrect = 'INCORRECT_VALUE'
    response = bkkb_client.get_last_all_rate_update_for_value(dict(day='02', month='04', year='2023'), ticker_incorrect)
    assert response.status_code == 200
    assert len(response.json()) == 0
