import requests
import datetime
import os
from dotenv import load_dotenv
import logging

dotenv_path = os.path.abspath('.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get('TOKEN_BANGKOK')
# TOKEN = '1qwqe2e2wrqerwee22222'

HEADERS = {'Ocp-Apim-Subscription-Key': TOKEN, }
logging.basicConfig(level=logging.DEBUG, filename='logs/bangkok_bank.log', format='%(asctime)s %(levelname)s:%(message)s')


def get_last_update_rate():
    url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/GetDateTimeLastUpdate'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 401:
        logging.error('GETTING LAST RATES UPDATE FAILED : %s', response.reason)
        return None

    last_date_update = response.json()[0].get("Day").split('/')
    time_update = response.json()[0].get("Time")
    logging.debug('LAST BANGKOKBANK UPDATE RATE %s - %s', last_date_update, time_update)
    return dict(
        day=last_date_update[0],
        month=last_date_update[1],
        year=last_date_update[2],
        last_time_update=time_update
    )


def get_inner_family_value(value_rate='US Dollar 50-100', all=None):
    url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/Getfxfamily'
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 401:
        logging.error('GETTING INNER FAMILY VALUE DATA FAILED : %s', response.reason)
        return False

    if all is not None:
        logging.debug('ALL INNER FAMILIES VALUES HAVE BEEN RECEIVED %s', response.json())
        return response.json()
    for value in response.json():
        if value.get('Description') == value_rate:
            needed_value = value.get('Family')
            logging.debug('FAMILY FOR %s HAS BEEN RECEIVED: %s', value_rate
                          , needed_value)
            return needed_value
    return None


def get_x_rate_for_value(date_list, family, rate_info="TT"):
    now = datetime.datetime.now()
    tdd = now.day
    tmm = now.month
    tyyyy = now.year
    fdd = date_list.get('day')
    fmm = date_list.get('month')
    fyyyy = date_list.get('year')
    lang = 'en'
    url = f'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/GetChartfxrates/{fdd}/{fmm}/{fyyyy}/{tdd}/{tmm}/{tyyyy}/{family}/{lang}'
    response = requests.get(url, headers=HEADERS)
    data_needed = response.json()[-1]
    date = data_needed.get('Ddate').split('/')
    result_dict_x_rate = dict(
        tt_rate=data_needed.get(rate_info),
        date=f"{date[1]}/{date[0]}/{date[2]}",
        time=data_needed.get('DTime')
    )
    logging.debug('T-T RATE LAST UPDATE %s', result_dict_x_rate['tt_rate'])
    return result_dict_x_rate


def get_bangkok_usd_rate_inner():
    last_update = get_last_update_rate()

    if last_update is None:
        return None

    family = get_inner_family_value()
    if family is None:
        return get_inner_family_value(all=1)
    if not family:
        return None

    tt_rate = get_x_rate_for_value(last_update, family)
    if tt_rate is not None:
        return tt_rate


if __name__ == '__main__':
    last_update = get_last_update_rate()
    result = get_bangkok_usd_rate_inner()
