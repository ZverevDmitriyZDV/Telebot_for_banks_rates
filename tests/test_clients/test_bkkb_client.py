import pytest
import datetime

from pandas import DataFrame


def test_token_bkkb(requests_mock, correct_client):
    bkkb_client = correct_client
    headers = bkkb_client.headers
    requests_mock.get('http://some_url/ServiceVersion', request_headers=headers, text='2.0.0.1', status_code=200)
    response = bkkb_client.get_data('ServiceVersion')
    assert response.text == '2.0.0.1'
    assert response.status_code == 200


def test_incorrect_token_bkkb(requests_mock, incorrect_client):
    bkkb_client_incorrect = incorrect_client
    headers = bkkb_client_incorrect.headers
    requests_mock.get('http://some_url/ServiceVersion', request_headers=headers, json={"message": None},
                      status_code=401)
    response = bkkb_client_incorrect.get_data('ServiceVersion')
    assert response.json().get('message') is None
    assert response.status_code == 401


def test_last_update(requests_mock, get_last_data_response, correct_client):
    bkkb_client = correct_client
    headers = bkkb_client.headers
    json_request = get_last_data_response
    requests_mock.get('http://some_url/GetDateTimeLastUpdate', request_headers=headers, json=json_request,
                      status_code=200)
    now = datetime.datetime.now().strftime('%d/%m/%Y')
    response = bkkb_client.get_last_update()
    assert response.json()[0].get('Day')[2:] == now[2:]
    assert response.status_code == 200


def test_get_all_families(correct_client, requests_mock, get_family_response):
    bkkb_client = correct_client
    headers = bkkb_client.headers
    json_response = get_family_response
    requests_mock.get('http://some_url/Getfxfamily', request_headers=headers, json=json_response, status_code=200)
    client_response = bkkb_client.get_all_values_families()
    assert client_response.status_code == 200
    assert len(client_response.json()) > 10

    data_frame = DataFrame(client_response.json())
    ticker_1 = 'Laos Kip'
    ticker_2 = 'INCORRECT_VALUE'

    def get_family(df, ticker):
        value_by_ticker = df[df['Description'] == ticker]
        return value_by_ticker['Family'].iloc[0]

    assert get_family(data_frame, ticker_1) == 'LAK'
    with pytest.raises(IndexError) as e_info:
        get_family(data_frame, ticker_2)


def test_last_rate_update(correct_client, requests_mock, get_lak_update_rates):
    bkkb_client = correct_client
    headers = bkkb_client.headers
    json_response = get_lak_update_rates
    now = datetime.datetime.now()
    tdd = now.day
    tmm = now.month
    tyyyy = now.year
    fdd = '02'
    fmm = '04'
    fyyyy = '2023'
    lang = 'en'
    family = 'LAK'
    requests_mock.get(f'http://some_url/GetChartfxrates/{fdd}/{fmm}/{fyyyy}/{tdd}/{tmm}/{tyyyy}/{family}/{lang}',
                      request_headers=headers, json=json_response, status_code=200)
    response = bkkb_client.get_last_all_rate_update_for_value(dict(day=fdd, month=fmm, year=fyyyy), family)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0].get('Family') is not None


def test_last_rate_update_incorrect_value(correct_client, requests_mock):
    bkkb_client = correct_client
    headers = bkkb_client.headers
    json_response = []
    now = datetime.datetime.now()
    tdd = now.day
    tmm = now.month
    tyyyy = now.year
    fdd = '02'
    fmm = '04'
    fyyyy = '2023'
    lang = 'en'
    family = 'INCORRECT_VALUE'
    requests_mock.get(f'http://some_url/GetChartfxrates/{fdd}/{fmm}/{fyyyy}/{tdd}/{tmm}/{tyyyy}/{family}/{lang}',
                      request_headers=headers, json=json_response, status_code=200)
    response = bkkb_client.get_last_all_rate_update_for_value(dict(day=fdd, month=fmm, year=fyyyy), family)
    assert response.status_code == 200
    assert len(response.json()) == 0
