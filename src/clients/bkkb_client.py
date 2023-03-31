import datetime

import requests

from src.clients.base_api_class import BankAPI
from src.config.configurator import BKKBConfiguration


class BKKBClient(BankAPI):
    """
    Реализация класса запросов по API BangkokBank
    url запроса котировок определе для всех экземпляров класса
    """
    url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService'

    def __init__(self):
        """
        Инициализация подключения к API серверу
        :param token_name: токен подключения к API.
        Для его получения
        необходимо зарегистрироваться и запросить токен в клиенте личного профиля банка. Ссылка на получение и
        регистрацию: https://developer.bangkokbank.com/
        """
        self.headers = {'Ocp-Apim-Subscription-Key': self.get_token(), }

    def get_token(self):
        bkkb_configuration = BKKBConfiguration()
        return bkkb_configuration.token

    def get_data(self, url_keyword: str):
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
        return self.get_data('GetDateTimeLastUpdate')

    def get_all_values_families(self):
        """
        метод получения всех названий семейств для все имеющихся валют, по которым происходят операции обмена
        :return: HTTPResponse объект с данными о соотношении названия валюты с внутренним кодом, по которому
        производятся котировки.
        """
        return self.get_data('Getfxfamily')

    def get_last_all_rate_update_for_value(self, date_list: dict, family: str):
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
        return self.get_data(url_keyword)