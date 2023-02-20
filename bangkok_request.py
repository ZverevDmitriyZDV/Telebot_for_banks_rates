from http.client import HTTPResponse

import pandas as pd
import requests
import datetime
import os
from dotenv import load_dotenv
import logging
from pandas import DataFrame
from logger.logger import Zlogger
from abc import ABC, abstractmethod

# быстрая настройка записи логов
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


def check_status(response: HTTPResponse, msg: str) -> HTTPResponse:
    """
    функция проверки статуса запроса
    :param response:
    :param msg:
    :return:
    """
    if response.status_code == 401:
        logging.error(f'{msg} %s', response.reason)
        return None
    return response


class BangkokApi(BankAPI):
    """
    Реализация класса запросов по API BangkokBank
    url запроса котировок определе для всех экземпляров класса
    """
    url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService'

    def __init__(self, token_name):
        """
        Инициализация подключения к API серверу
        :param token_name: токен подключения к API.
        Для его получения
        необходимо зарегистрироваться и запросить токен в клиенте личного профиля банка. Ссылка на получение и
        регистрацию: https://developer.bangkokbank.com/
        """
        self.token_name = token_name
        self.headers = {'Ocp-Apim-Subscription-Key': self.get_token(), }

    def get_token(self):
        """
        получение сохраненного токена из файл .env или окружениея HEROKU / GIT в зависимости от ресурса на котором
        будет произведено развертывание проекта.
        :return: токен доступа для осуществеления запросов по API
        """
        load_dotenv(os.path.abspath('.env'))
        return os.environ.get(self.token_name)

    def get(self, url_keyword):
        """
        метод осуществляющий запрос GET по ключевому слову в соовтетсвии с API документацией
        https://developer.bangkokbank.com/docs/services/exchangerateservice/operations/exchangewebapi_fxcal
        :param url_keyword: слово определяющее вызываемый метод API банка
        :return: HTTPResponse - результат запроса
        """
        return requests.get(self.url + '/' + url_keyword, headers=self.headers)

    def get_last_update(self):
        """
        метод получения последней даты обновления котировок
        :return: HTTPResponse объект с данными о последних обновлениях котировок
        """
        return self.get('GetDateTimeLastUpdate')

    def get_all_values_families(self):
        """
        метод получения всех названий семейств для все имеющихся валют, по которым происходят операции обмена
        :return: HTTPResponse объект с данными о соотношении названия валюты с внутренним кодом, по которому
        производятся котировки.
        """
        return self.get('Getfxfamily')

    def get_last_all_rate_update_for_value(self, date_list, family):
        """
        Метод определения котировок валют с настоящего времени по заданную дату
        :param date_list:  -> dict: словарь с данными до какой даты необходимо искать данные по обновлению котировок
        :param family:     -> str : значение семейства валюты, дял которой определяются котировки
        :return: HTTPResponse объект с данными котировок валюты в заданный период времени
        """
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
    """
    Реализация класса работы с данными по завершению API запросов
    """

    def __init__(self, token_name):
        """
        Инициализация клиента для работы с API банком
        :param token_name: название переменной для передачи значения токена из env файла
        """
        self.client = BangkokApi(token_name)

    def format_update_data(self):
        """
        Метод форматирования данных запроса и формирования даты последнего обновления котировок валют банка по заданному
        образцу dd/mm/yyyy/time
        :return: ->dict: словарь с данными последней даты обновления котировок
        """
        # проверка статуса запроса и запись логов при ошибке
        response = check_status(self.client.get_last_update(), msg='GETTING LAST RATES UPDATE FAILED :')
        if response is None:
            return None
        # выбираем интересующие нас данные из json объекта
        last_date_update = response.json()[0].get("Day").split('/')
        time_update = response.json()[0].get("Time")
        # запись логов удачного результат
        logging.debug('LAST BANGKOKBANK UPDATE RATE %s - %s', last_date_update, time_update)
        return dict(
            day=last_date_update[0],
            month=last_date_update[1],
            year=last_date_update[2],
            last_time_update=time_update
        )

    def format_all_values_family(self):
        """
        Метод форматирования данных запроса всех семейств валют.
        :return: -> DataFrame объект с данными всех семейств валют
        """
        # проверка статуса запроса и запись логов при ошибке
        response = check_status(self.client.get_all_values_families(), msg='GETTING INNER FAMILY VALUE DATA FAILED :')
        if response is None:
            return None
        # формирование DataFrame объекта средствами pandas, настройка с отображением всех данных в логах
        bangkok_bank_inner_families_values = DataFrame(response.json())
        # max.rows рекомендуется указать не более 30. Без натройки None отображение будет в свернутом виде
        pd.set_option('display.max_rows', None)
        # запись логов удачного результат
        logging.debug('ALL INNER FAMILIES VALUES HAVE BEEN RECEIVED \n%s', bangkok_bank_inner_families_values)
        return bangkok_bank_inner_families_values

    def format_get_family_by_currency(self, currency):
        """
        метод поиска навзания семейства для определенной валюты по ее точному названию, определенному банком
        :param currency: -> str название валюты
        :return: -> str название семейства для валюты
        """

        data_frame = self.format_all_values_family()
        # производим поиск по полю Description
        currency_frame = data_frame.loc[data_frame['Description'] == currency]
        # проверяем результат поиска на наличие результата
        if len(currency_frame['Family']) == 0:
            logging.error('FAMILY FOR %s VALUE HAS NOT BEEN FOUND:', currency)
            return None
        # определяем требуемое значение из DataFrame объекта
        format_family_currency = currency_frame['Family'].loc[currency_frame.index[0]]
        # запись логов удачного результат
        logging.debug('FAMILY FOR %s VALUE HAS BEEN RECEIVED: %s', currency, format_family_currency)
        return format_family_currency

    def format_get_close_families_by_reg_name(self, reg_currency):
        """
        Метод поиска возможных совпадений семейства и валют по ключевому слову.
        поиск происходит по регулярному выражению
        :param reg_currency: -> str название валюты
        :return: -> DateFrame Объект возможных совпадений
        """
        # поиск всех семейств валют
        data_frame = self.format_all_values_family()
        # форматирование значение по нижнему регистру для предотвращения опечаток
        data_frame['Description'] = data_frame['Description'].str.lower()
        # фильтрация данных по требуемому ключевому значению
        format_families_by_reg = data_frame[data_frame['Description'].str.match(f"((.*)({reg_currency.lower()}).*)") == True]
        # запись логов удачного результат
        logging.debug('ALL FAMILIES CLOSE TO CURRENSY \n%s', format_families_by_reg)
        return format_families_by_reg

    def format_get_x_rate(self, date_list, family, rate_info="TT"):
        """
        Метод определения котировок обмена валют. по умолчанию значение ТТ определяем котировки для клиентов банка,
        имеющих два счета банка с внутренней валютой и иностранной
        :param date_list:   -> dict словарь времени с которого необходимо отслеживать изменения курса
        :param family:      -> str семейство валюты
        :param rate_info:   -> str код курса обмена валют в зависимости от статус клиента банка
        :return:            -> dict значение котировок с данными последнего обновления
        """
        # проверка данных на ввод исключяем получения None
        if date_list is None or family is None:
            return None
        response = self.client.get_last_all_rate_update_for_value(date_list, family)
        # проверка статуса результа запроса
        response = check_status(response, msg='GETTING RATE FOR CURENCY IS FAILED :')
        if response is None:
            return None
        # выбираем необходимые данные их полученного HTTPResponse объекта
        data_needed = response.json()[-1]
        date = data_needed.get('Ddate').split('/')
        result_dict_x_rate = dict(
            tt_rate=data_needed.get(rate_info),
            date=f"{date[1]}/{date[0]}/{date[2]}",
            time=data_needed.get('DTime')
        )
        # запись логов удачного результат
        logging.debug('T-T RATE LAST UPDATE %s', result_dict_x_rate['tt_rate'])
        return result_dict_x_rate


if __name__ == '__main__':
    # объявление киента
    client = BKKBClient('TOKEN_BANGKOK')
    # поиск возможных совпадений
    usd_family = client.format_get_close_families_by_reg_name('Dollar')
    # поиск семейства для USD
    family = client.format_get_family_by_currency('US Dollar 50-100')
    # определяем дату последнего обновления котировок
    time_update_date = client.format_update_data()
    # определяем курс обмена валюты USD в THB для внутреннго клиента банка
    usd_thb = client.format_get_x_rate(time_update_date,family)

# референс старая версия
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
