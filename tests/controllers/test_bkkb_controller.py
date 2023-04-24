import datetime
from unittest.mock import MagicMock

import pytest

from src.utils.bad_auth_exception import BadAuthException
from tests.fixtures_for_bkkb_client import make_responce_object
from tests.fixtures_for_bkkb_client import get_last_data_response, get_family_responce, get_lak_update_rates, \
    get_usd_update_rates
from src.config.configurator import BKKBConfiguration
from src.controllers.bkkb_controller import BKKBDataFrameFormat


@pytest.fixture
def bkkb_client_df():
    conf = BKKBConfiguration(token='TOKEN')
    return BKKBDataFrameFormat(conf=conf)


def test_incorrect_token():
    conf = BKKBConfiguration(token="Icorrect_token")
    bkkb_client = BKKBDataFrameFormat(conf)
    bkkb_client.client.get_data = MagicMock(side_effect=BadAuthException)
    with pytest.raises(BadAuthException) as e_info:
        bkkb_client.get_last_update()


def test_correct_token(get_last_data_response, bkkb_client_df):
    make_fake_update_responce(get_last_data_response, bkkb_client_df)
    response = bkkb_client_df.get_last_update()
    now = datetime.datetime.now().strftime('%d/%m/%Y')
    assert response.status_code == 200
    assert response.json()[0].get('Day')[2:] == now[2:]


def test_format_update_date(get_last_data_response, bkkb_client_df):
    make_fake_update_responce(get_last_data_response, bkkb_client_df)
    now_time = datetime.datetime(day=24, month=4, year=2023)
    result_data = bkkb_client_df.format_update_data()
    result_data_datetime = datetime.datetime(day=int(result_data['day']), month=int(result_data['month']),
                                             year=int(result_data['year']))
    delta_time = now_time - result_data_datetime
    assert delta_time < datetime.timedelta(days=10)


def test_format_get_family_by_currency(get_family_responce, bkkb_client_df):
    currency = 'Laos Kip'
    make_fake_families_responce(get_family_responce, bkkb_client_df)
    format_data = bkkb_client_df.format_get_family_by_currency(currency)
    assert format_data == 'LAK'


def test_format_get_family_by_incorrect_currency(get_family_responce, bkkb_client_df):
    make_fake_families_responce(get_family_responce, bkkb_client_df)
    currency = 'INCORRECT_CURRENCY'
    format_data = bkkb_client_df.format_get_family_by_currency(currency)
    assert format_data is None


def test_format_get_close_families_by_reg_name(get_family_responce, bkkb_client_df):
    make_fake_families_responce(get_family_responce, bkkb_client_df)
    reg_currency = 'Dollar'
    df = bkkb_client_df.format_get_close_families_by_reg_name(reg_currency=reg_currency)
    usd_50 = df[df['Description'] == 'us dollar 1-2']['Family'].iloc[0]
    assert len(df) > 3
    assert usd_50 == 'USD1'


def test_format_get_close_families_by_incorrec_reg_name(get_family_responce, bkkb_client_df):
    make_fake_families_responce(get_family_responce, bkkb_client_df)
    reg_currency = 'INCORRECT_REX'
    df = bkkb_client_df.format_get_close_families_by_reg_name(reg_currency=reg_currency)
    assert len(df) == 0
    assert df.empty is True


def test_format_get_x_rate(get_lak_update_rates, bkkb_client_df):
    family = 'LAK'
    make_fake_rate_request(get_lak_update_rates, bkkb_client_df)
    date_list = dict(day='02', month='04', year='2023')
    response_tuple = bkkb_client_df.format_get_x_rate(family=family, date_list=date_list)
    assert response_tuple != (None, None)
    assert type(response_tuple[0]) == float
    assert type(response_tuple[1]) == str


def test_formаt_get_x_rate_incorrect(get_lak_update_rates, bkkb_client_df):
    make_fake_rate_request(get_lak_update_rates, bkkb_client_df)
    date_dict = dict(day='02', month='04', year='2023')
    rate = 'INCORRECT_RATE'
    response_tuple = bkkb_client_df.format_get_x_rate(date_dict, rate)
    assert response_tuple == (None, None)


def test_formаt_get_x_rate_incorrect(get_lak_update_rates, bkkb_client_df):
    make_fake_rate_request(get_lak_update_rates, bkkb_client_df)
    date_dict = dict(day='02', month='04', year='2023')
    rate = None
    response_tuple = bkkb_client_df.format_get_x_rate(date_dict, rate)
    assert response_tuple == (None, None)


def make_fake_update_responce(get_last_data_response, bkkb_client_df):
    fake_reponse = make_responce_object(get_last_data_response, 200)
    bkkb_client_df.client.get_last_update = MagicMock(return_value=fake_reponse)


def make_fake_families_responce(get_family_responce, bkkb_client_df):
    fake_response = make_responce_object(get_family_responce, 200)
    bkkb_client_df.client.get_all_values_families = MagicMock(return_value=fake_response)


def make_fake_rate_request(get_lak_update_rates, bkkb_client_df):
    fake_responce = make_responce_object(get_lak_update_rates, 200)
    bkkb_client_df.client.get_last_all_rate_update_for_value = MagicMock(return_value=fake_responce)
