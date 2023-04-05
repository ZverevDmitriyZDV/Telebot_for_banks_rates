import datetime

import pytest

from src.controllers.bkkb_controller import BKKBDataFrameFormat
from src.utils.bad_auth_exception import BadAuthException


def test_correct_token():
    bkkb_client_df = BKKBDataFrameFormat()
    response = bkkb_client_df.get_last_update()
    now = datetime.datetime.now().strftime('%d/%m/%Y')
    assert response.status_code == 200
    assert response.json()[0].get('Day')[2:] == now[2:]


def test_incorrect_token():
    bkkb_client_df = BKKBDataFrameFormat()
    bkkb_client_df.client.token = 'INCORRECT_TOKEN'
    with pytest.raises(BadAuthException) as e_info:
        bkkb_client_df.get_last_update()


def test_format_update_date():
    bkkb_client_df = BKKBDataFrameFormat()
    now_month = datetime.datetime.now().strftime('%m')
    result_data = bkkb_client_df.format_update_data()
    assert result_data.get('month') == now_month


def test_format_get_family_by_currency():
    bkkb_client_df = BKKBDataFrameFormat()
    currency = 'Laos Kip'
    format_data = bkkb_client_df.format_get_family_by_currency(currency)
    assert format_data == 'LAK'


def test_format_get_family_by_incorrect_currency():
    bkkb_client_df = BKKBDataFrameFormat()
    currency = 'INCORRECT_CURRENCY'
    format_data = bkkb_client_df.format_get_family_by_currency(currency)
    assert format_data is None


def test_format_get_close_families_by_reg_name():
    bkkb_client_df = BKKBDataFrameFormat()
    reg_currency = 'Dollar'
    df = bkkb_client_df.format_get_close_families_by_reg_name(reg_currency=reg_currency)
    usd_50 = df[df['Description'] == 'us dollar 1-2']['Family'].iloc[0]
    assert len(df) > 3
    assert usd_50 == 'USD1'


def test_format_get_close_families_by_incorrec_reg_name():
    bkkb_client_df = BKKBDataFrameFormat()
    reg_currency = 'INCORRECT_REX'
    df = bkkb_client_df.format_get_close_families_by_reg_name(reg_currency=reg_currency)
    assert len(df) == 0
    assert df.empty is True


def test_format_get_x_rate():
    bkkb_client_df = BKKBDataFrameFormat()
    family = 'USD50'
    date_list = dict(day='02', month='04', year='2023')
    response_tuple = bkkb_client_df.format_get_x_rate(family=family, date_list=date_list)
    assert response_tuple != (None, None)
    assert type(response_tuple[0]) == float
    assert type(response_tuple[1]) == str


def test_formаt_get_x_rate_incorrect():
    bkkb_client_df = BKKBDataFrameFormat()
    date_dict = dict(day='02', month='04', year='2023')
    rate = 'INCORRECT_RATE'
    response_tuple = bkkb_client_df.format_get_x_rate(date_dict, rate)
    assert response_tuple == (None, None)


def test_formаt_get_x_rate_incorrect():
    bkkb_client_df = BKKBDataFrameFormat()
    date_dict = dict(day='02', month='04', year='2023')
    rate = None
    response_tuple = bkkb_client_df.format_get_x_rate(date_dict, rate)
    assert response_tuple == (None, None)