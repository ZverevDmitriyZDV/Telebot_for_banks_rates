from datetime import timedelta
import pytz
from typing import Optional, Tuple

import pandas as pd
from pandas import DataFrame

from ta.trend import ema_indicator
from tinkoff.invest.services import InstrumentsService, MarketDataService
from tinkoff.invest import Client, RequestError, CandleInterval
from tinkoff.invest.utils import now

from bangkok_request import BankAPI
from units import cast_money
from constant_data import *
from logger.logger import Zlogger

tink_logger = Zlogger()
tink_logger.name = 'TINKLOGS'
tink_logger.log_file = 'tinkoff_logs'
logger_tink = tink_logger.setup_logger


class TinkoffBankClient(BankAPI):
    """
    реализация класса подключения к клиенту брокера Тинькофф и осуществления запросов последних котировок японский
    свечей валют
    """

    def __init__(self, token_name: str):
        """
        Инициализация подключения к клиенту брокера
        :param token_name:  токен подключения к клиенту
        """
        self.token_name = self.get_token(token_name=token_name)

    def get_data(self) -> Optional[bool]:
        """
        метод осуществления проверки корректного подключения к клиенту.
        проверяет правильность токена путем получения информации о пользователе.
        :return: True / False
        """
        try:
            with Client(self.token_name) as cl:
                _ = cl.users.get_info()
                return True
        except RequestError as e:
            # в случае ошибки подключения осуществить запись логов в файл
            logger_tink.error(e.metadata.message)
            return False

    def get_all_figi_list(self) -> Optional[list]:
        """
        метод получения соотношения Тикетов валют, их названий и кода валюты FIGI для дальнейших корректных запросов
        :return: -> list() список данных по каждой валюте, по которой проходят торговые операции
        """
        # проверка подключению к клиенту
        if not self.get_data():
            return None
        # поиск всех валют по которым проходят торговые операции(method), все данные хранятся во внутреннем классе
        with Client(self.token_name) as cl:
            instruments: InstrumentsService = cl.instruments
            list_of_all_ticker_figi = list()
            for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
                for item in getattr(instruments, method)().instruments:
                    list_of_all_ticker_figi.append({
                        'ticker': item.ticker,
                        'figi': item.figi,
                        'type': method,
                        'name': item.name,
                    })
        logger_tink.debug('''ALL FIGI'S LIST HAVE BEEN FOUND''')
        return list_of_all_ticker_figi

    def get_candles_by_figi(self, figi: str) -> Optional[list]:
        """
        метод получения свечей по заданному коду FIGI
        период отслеживания данных в течении последних 3-х дней
        данные свечей - часовые свечи
        при изменении параметров могут возникнуть ошибки перегрузки запросов и блокировка со стороны Тинькофф клиента
        :param figi: -> Str строковое обозначение код-ключа FIGI
        :return: -> List список данных часовых свечей в течении 3-х дней
        """
        # проверка возможности подключения
        if not self.get_data():
            return None
        # поиск информации японских торговых свечей для определенной валюты. Код валюты передается через FIGI
        # для реализации используется внутренний класс MarketDataService
        with Client(self.token_name) as client:
            market_data: MarketDataService = client.market_data
            response = client.market_data.get_candles(
                figi=figi,
                from_=now() - timedelta(days=3),
                to=now(),
                interval=CandleInterval.CANDLE_INTERVAL_HOUR
            )
            # проверка ответа на корректность исходного запроса
            if len(response.candles) == 0:
                logger_tink.error('FIGI IS WRONG. NO CANDLES HAVE BEEN FOUNDED')
                return None
            logger_tink.debug('CANDLES INFO FOR FIGI %s HAVE BEEN FOUND', figi)
            return response.candles

    def get_usd_candles(self) -> Optional[list]:
        """
        метод получения свечей для валюты USD
        для осуществления необходимо знать точное значение FIGI_USD
        :return: -> List список данных часовых свечей для USD в течении 3-х дней
        """
        logger_tink.debug('CANDLES INFO FOR USD HAVE BEEN FOUND')
        return self.get_candles_by_figi(FIGI_USD)


class TinkoffDataFrameFormat:
    """
    класс обработки данных запросов от клиента Тинькофф. Для удобства используется pandas
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    def __init__(self, list_of_all_ticker_figi: list) -> Optional[DataFrame]:
        """
        метод инициализации класса
        :param list_of_all_ticker_figi: список дынных всех валют с информацие по названию / тикеру / figi-кода.
        """
        # преобразуем данные в DataFrame объет для удобства обращения
        self.list_of_all_ticker_figi = DataFrame(list_of_all_ticker_figi)

    def get_ticker_by_rex(self, rex_word: str) -> Optional[DataFrame]:
        """
        метод позволяющий по ключевому выражению осуществить поиск близких совпадений для данных валюты.
        поиск осуществляется по ticker
        :param rex_word: -> Str регулярное выражение для валюты
        :return: -> DataFrame объект с названием / тикетом/ figi ключом интересующей валюты
        """
        return self.list_of_all_ticker_figi[self.list_of_all_ticker_figi['ticker'].str.match(rex_word) == True]

    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """
        метод позволяющий по тикеру валюты найти интересующий figi-ключ
        :param ticker: -> Str тикер валюты, необходимо точное совпадение
        :return: -> Str фиги-ключ для валюты
        """
        data_frame_ticker_figi = self.list_of_all_ticker_figi[self.list_of_all_ticker_figi['ticker'] == ticker]
        # проверка данных на соответсвие
        if data_frame_ticker_figi.empty:
            logger_tink.error('GETTING TICKER %s FAILED ', ticker)
            return
        figi_for_ticker = data_frame_ticker_figi['figi'].iloc[0]
        logger_tink.debug('FIGI FOR TICKER %s IS %s', ticker, figi_for_ticker)
        return figi_for_ticker


class CandlesDataFrame:
    """
    класс для обработки данных свечей валют
    """

    def __init__(self, candles: list):
        """
        метод инициализации
        :param candles: -> List список данных запроса японских свечей определнной валюты
        """
        self.candles = candles

    def create_df(self) -> DataFrame:
        """
        метод преобразования списка в DataFrame объект с выделением конкретной информации и преобразованием валют
        :return: -> DataFrame объект данных свечей с форматированными данными по стоимости
        """
        # данные открытия / закрытия свечей имеют имеют дробные значение. банком данные цифры определены с точностью
        # до 9 знака. для получения корректных котировок необходимо преобрпзовать данные
        if self.candles is None:
            return None
        candles_df_data = DataFrame([{
            'time': candle.time,
            'volume': candle.volume,
            'open': cast_money(candle.open),
            'close': cast_money(candle.close),
            'high': cast_money(candle.high),
            'low': cast_money(candle.low),
        } for candle in self.candles])
        return candles_df_data

    def get_xrates_ema_dataframe(self) -> DataFrame:
        """
        Метод получения значения средней скользящей для котировок валюты. Значение EMA
        Подробнее и тех анализа трейдеров https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.ema_indicator
        :return: -> DataFrame объект данных  свечей с добавление пункта EMA к каждой записи
        """
        if self.candles is None:
            return None
        candles_df_data = self.create_df()
        candles_df_data['ema'] = ema_indicator(close=candles_df_data['close'], window=9)
        logger_tink.debug('RATES HAVE BEEN RECEIVED')
        return candles_df_data[['time', 'open', 'close', 'high', 'low', 'ema']].tail(30)

    def get_xrate_dict_format(self) -> Optional[Tuple[float, str]]:
        """
        Метод форматирования данных в формате словаря, с определением максимального текущего курса заданной валюты
        :return: -> Dict словарь с данными максимальных котировок валюты с учетом EMA значением
        """
        if self.candles is None:
            return None, None
        rates_data = self.get_xrates_ema_dataframe()
        # проверка данных на соответствие
        if rates_data is None:
            logger_tink.error('GET RATE WAS CRUSHED')
            return None
        # смотрим последние данные для свечи заданной валюты.
        data = rates_data.iloc[-1]
        max_rate = max(data.open, data.close, data.high, data.low)
        max_rate_with_ema = round(max(max_rate, data.ema), 2)
        date = data.time
        dt_Moscow = date.astimezone(pytz.timezone('Europe/Moscow')).strftime('%H:%M  %d/%m/%Y')
        logger_tink.debug('GET RATE WAS ACCOMPLISHED. MAX RATE: %d', max_rate_with_ema)
        message_in = f"USD   : {max_rate}\n" \
                     f"USD ema: {max_rate_with_ema}\n" \
                     f"Update : {dt_Moscow}\n" \
                     f"\n"

        return max_rate_with_ema, message_in


class LastUSDToRUBRates:
    """
    класс для определения последнего обновления котировокл валюыт USD
    """

    def __init__(self):
        """
        метод инициализации клиента Тинькофф банка.
        """
        self.client = TinkoffBankClient('TOKEN_TINK')

    def get_usd_last_rate(self) -> Optional[Tuple[float, str]]:
        """
        метод формирования словаря, в котором будет определена информация по последнем курсу для USD
        :return: -> Dict() словарь с данными по котировкам
        """
        # поиск свечей для валюты USD
        usd_candles_data = self.client.get_usd_candles()
        # форматирование данных свечей
        usd_rates_data = CandlesDataFrame(usd_candles_data)
        # форматирование результата в вид словаря
        return usd_rates_data.get_xrate_dict_format()


if __name__ == '__main__':
    # # построчное исполненение
    tnk_client = TinkoffBankClient('TOKEN_TINK')
    t1 = tnk_client.get_usd_candles()
    print(type(t1))
    fig_list = tnk_client.get_all_figi_list()
    usd_rex = "(US).*"
    usd_candles_data = tnk_client.get_usd_candles()
    money = CandlesDataFrame(usd_candles_data)
    usd_last_rate, message = money.get_xrate_dict_format()
    # # реализация класса
    tink_usd = LastUSDToRUBRates()
    print(tink_usd.get_usd_last_rate())
