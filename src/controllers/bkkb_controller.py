from typing import Optional

import pandas as pd
from pandas import DataFrame
from requests import Response

from src.clients.bkkb_client import BKKBClient
from src.config.configurator import BKKBConfiguration
from src.utils.http_bkkb_utils import check_status, logger_bkkbanks_logs


class BKKBDataFrameFormat:
    """
    Реализация класса работы с данными по завершению API запросов
    """

    def __init__(self, conf: BKKBConfiguration):
        """
        Инициализация клиента для работы с API банком
        :param token_name: название переменной для передачи значения токена из env файла
        """
        self.conf = conf
        self.client = BKKBClient(self.conf)

    @check_status(msg='GETTING INNER FAMILY VALUE DATA FAILED :')
    def get_all_values_family(self) -> Response:
        return self.client.get_all_values_families()

    @check_status(msg='GETTING RATE FOR CURRENCY IS FAILED :')
    def get_x_rate(self, date_list: dict, family: str) -> Response:
        return self.client.get_last_all_rate_update_for_value(date_list, family)

    @check_status(msg='GETTING LAST RATES UPDATE FAILED :')
    def get_last_update(self) -> Response:
        return self.client.get_last_update()

    def format_update_data(self) -> Optional[dict]:
        """
        Метод форматирования данных запроса и формирования даты последнего обновления котировок валют банка по заданному
        образцу dd/mm/yyyy/time
        :return: ->dict: словарь с данными последней даты обновления котировок
        """
        # проверка статуса запроса и запись логов при ошибке
        response = self.get_last_update()
        # выбираем интересующие нас данные из json объекта
        last_date_update = response.json()[0].get("Day").split('/')
        time_update = response.json()[0].get("Time")
        # запись логов удачного результат

        logger_bkkbanks_logs.debug('LAST BANGKOKBANK UPDATE RATE %s - %s', last_date_update, time_update)
        return dict(
            day=last_date_update[0],
            month=last_date_update[1],
            year=last_date_update[2],
            last_time_update=time_update
        )

    def format_all_values_family(self) -> Optional[DataFrame]:
        """
        Метод форматирования данных запроса всех семейств валют.
        :return: -> DataFrame объект с данными всех семейств валют
        """
        response = self.get_all_values_family()
        # формирование DataFrame объекта средствами pandas, настройка с отображением всех данных в логах
        bangkok_bank_inner_families_values = DataFrame(response.json())
        # max.rows рекомендуется указать не более 30. Без натройки None отображение будет в свернутом виде
        pd.set_option('display.max_rows', None)
        # запись логов удачного результат
        logger_bkkbanks_logs.debug('ALL INNER FAMILIES VALUES HAVE BEEN RECEIVED \n%s',
                                   bangkok_bank_inner_families_values)
        return bangkok_bank_inner_families_values

    def format_get_family_by_currency(self, currency: str) -> Optional[str]:
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
            logger_bkkbanks_logs.error('FAMILY FOR %s VALUE HAS NOT BEEN FOUND:', currency)
            return None
        # определяем требуемое значение из DataFrame объекта
        format_family_currency = currency_frame['Family'].loc[currency_frame.index[0]]
        # запись логов удачного результат
        logger_bkkbanks_logs.debug('FAMILY FOR %s VALUE HAS BEEN RECEIVED: %s', currency, format_family_currency)
        return format_family_currency

    def format_get_close_families_by_reg_name(self, reg_currency: str) -> Optional[DataFrame]:
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
        format_families_by_reg = data_frame[
            data_frame['Description'].str.match(f"((.*)({reg_currency.lower()}).*)")==True]
        # запись логов удачного результат
        logger_bkkbanks_logs.debug('ALL FAMILIES CLOSE TO CURRENSY \n%s', format_families_by_reg)
        return format_families_by_reg

    def format_get_x_rate(self, date_list: dict, family: str, rate_info: str = "TT") -> Optional[tuple]:
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
            return None, None
        response = self.get_x_rate(date_list, family)
        # проверка статуса результата запроса
        if len(response.json()) == 0:
            return None, None
        data_needed = response.json()[-1]
        date = data_needed.get('Ddate').split('/')
        tt_rate = float(data_needed.get(rate_info))
        date = f"{date[1]}/{date[0]}/{date[2]}"
        time = data_needed.get('DTime')
        # запись логов удачного результат
        logger_bkkbanks_logs.debug('T-T RATE LAST UPDATE %s', tt_rate)
        message_in = f"THB         : {tt_rate}\n" \
                     f"Update: {time} {date}\n" \
                     f"\n"
        return tt_rate, message_in
