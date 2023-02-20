import pandas as pd
import requests
import datetime
import os
from dotenv import load_dotenv
import logging
from pandas import DataFrame
from logger.logger import Zlogger
from abc import ABC, abstractmethod

bk_logger = Zlogger('bangkok_bank')
bk_logger.logger_config()
bk_logger.logger_format()


class BankAPI(ABC):
    url: str

    @abstractmethod
    def get_token(self):
        pass

    @abstractmethod
    def get(self):
        pass


def check_status(response, msg):
    if response.status_code == 401:
        logging.error(f'{msg} %s', response.reason)
        return None
    return response


class BangkokApi(BankAPI):
    url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService'

    def __init__(self, token_name):
        self.token_name = token_name
        self.headers = {'Ocp-Apim-Subscription-Key': self.get_token(), }

    def get_token(self):
        load_dotenv(os.path.abspath('.env'))
        return os.environ.get(self.token_name)

    def get(self, url_keyword):
        return requests.get(self.url + '/' + url_keyword, headers=self.headers)

    def get_last_update(self):
        return self.get('GetDateTimeLastUpdate')

    def get_all_values_families(self):
        return self.get('Getfxfamily')

    def get_last_all_rate_update_for_value(self, date_list, family):
        now = datetime.datetime.now()
        tdd = now.day
        tmm = now.month
        tyyyy = now.year
        fdd = date_list.get('day')
        fmm = date_list.get('month')
        fyyyy = date_list.get('year')
        lang = 'en'
        url_keyword = f'GetChartfxrates/{fdd}/{fmm}/{fyyyy}/{tdd}/{tmm}/{tyyyy}/{family}/{lang}'
        return self.get(url_keyword)


class BKKBClient:

    def __init__(self, token_name):
        self.client = BangkokApi(token_name)

    def format_update_data(self):
        response = check_status(self.client.get_last_update(), msg='GETTING LAST RATES UPDATE FAILED :')
        if response is None:
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

    def format_all_values_family(self):
        response = check_status(self.client.get_all_values_families(), msg='GETTING INNER FAMILY VALUE DATA FAILED :')
        if response is None:
            return None
        bangkok_bank_inner_families_values = DataFrame(response.json())
        pd.set_option('display.max_rows', None)
        logging.debug('ALL INNER FAMILIES VALUES HAVE BEEN RECEIVED \n%s', bangkok_bank_inner_families_values)
        return bangkok_bank_inner_families_values

    def format_get_family_by_currency(self, currency):
        data_frame = self.format_all_values_family()
        currency_frame = data_frame.loc[data_frame['Description'] == currency]

        if len(currency_frame['Family']) == 0:
            logging.error('FAMILY FOR %s VALUE HAS NOT BEEN FOUND:', currency)
            return None
        format_family_currency = currency_frame['Family'].loc[currency_frame.index[0]]

        logging.debug('FAMILY FOR %s VALUE HAS BEEN RECEIVED: %s', currency, format_family_currency)
        return format_family_currency

    def format_get_close_families_by_reg_name(self, reg_currency):
        data_frame = self.format_all_values_family()
        format_families_by_reg = data_frame[data_frame['Description'].str.match(f"((.*)({reg_currency}).*)") == True]
        logging.debug('ALL FAMILIES CLOSE TO CURRENSY \n%s', format_families_by_reg)
        return format_families_by_reg

    def format_get_x_rate(self, currency, rate_info="TT"):
        date_list = self.format_update_data()
        family = self.format_get_family_by_currency(currency)
        if date_list is None or family is None:
            return None
        response = self.client.get_last_all_rate_update_for_value(date_list, family)
        response = check_status(response, msg='GETTING RATE FOR CURENCY IS FAILED :')
        if response is None:
            return None
        data_needed = response.json()[-1]
        date = data_needed.get('Ddate').split('/')
        result_dict_x_rate = dict(
            tt_rate=data_needed.get(rate_info),
            date=f"{date[1]}/{date[0]}/{date[2]}",
            time=data_needed.get('DTime')
        )
        logging.debug('T-T RATE LAST UPDATE %s', result_dict_x_rate['tt_rate'])
        return result_dict_x_rate


if __name__ == '__main__':
    client = BKKBClient('TOKEN_BANGKOK')
    a1 = client.format_get_x_rate('US Dollar 50-100')
    print(a1)
    b2 = client.format_get_close_families_by_reg_name('Dollar')
    print(b2)

#
# def get_last_update_rate():
#     url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/GetDateTimeLastUpdate'
#     response = requests.get(url, headers=HEADERS)
#     if response.status_code == 401:
#         logging.error('GETTING LAST RATES UPDATE FAILED : %s', response.reason)
#         return None
#
#     last_date_update = response.json()[0].get("Day").split('/')
#     time_update = response.json()[0].get("Time")
#     logging.debug('LAST BANGKOKBANK UPDATE RATE %s - %s', last_date_update, time_update)
#     return dict(
#         day=last_date_update[0],
#         month=last_date_update[1],
#         year=last_date_update[2],
#         last_time_update=time_update
#     )
#
#
# def get_inner_family_value(value_rate='US Dollar 50-100', all=None):
#     url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/Getfxfamily'
#     response = requests.get(url, headers=HEADERS)
#
#     if response.status_code == 401:
#         logging.error('GETTING INNER FAMILY VALUE DATA FAILED : %s', response.reason)
#         return False
#
#     if all is not None:
#         bangkok_bank_inner_families_values = DataFrame(response.json())
#         pd.set_option('display.max_rows', None)
#         logging.debug('ALL INNER FAMILIES VALUES HAVE BEEN RECEIVED \n%s', bangkok_bank_inner_families_values)
#         return bangkok_bank_inner_families_values
#     for value in response.json():
#         if value.get('Description') == value_rate:
#             needed_value = value.get('Family')
#             logging.debug('FAMILY FOR %s HAS BEEN RECEIVED: %s', value_rate
#                           , needed_value)
#             return needed_value
#     return None
#
#
# def get_x_rate_for_value(date_list, family, rate_info="TT"):
#     now = datetime.datetime.now()
#     tdd = now.day
#     tmm = now.month
#     tyyyy = now.year
#     fdd = date_list.get('day')
#     fmm = date_list.get('month')
#     fyyyy = date_list.get('year')
#     lang = 'en'
#     url = f'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/GetChartfxrates/{fdd}/{fmm}/{fyyyy}/{tdd}/{tmm}/{tyyyy}/{family}/{lang}'
#     response = requests.get(url, headers=HEADERS)
#     data_needed = response.json()[-1]
#     date = data_needed.get('Ddate').split('/')
#     result_dict_x_rate = dict(
#         tt_rate=data_needed.get(rate_info),
#         date=f"{date[1]}/{date[0]}/{date[2]}",
#         time=data_needed.get('DTime')
#     )
#     logging.debug('T-T RATE LAST UPDATE %s', result_dict_x_rate['tt_rate'])
#     return result_dict_x_rate
#
#
# def get_bangkok_usd_rate_inner():
#     last_update = get_last_update_rate()
#
#     if last_update is None:
#         return None
#
#     family = get_inner_family_value()
#     if family is None:
#         return get_inner_family_value(all=1)
#     if not family:
#         return None
#
#     tt_rate = get_x_rate_for_value(last_update, family)
#     if tt_rate is not None:
#         return tt_rate
#
#
# if __name__ == '__main__':
#     get_last_update_rate()
#     # gf = get_inner_family_value(all =1)
#     # a1 = gf[gf['Description'].str.match("((US).*)")==True]
#     # print(a1)
