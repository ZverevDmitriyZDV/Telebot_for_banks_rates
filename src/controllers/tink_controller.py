from typing import Optional, Tuple

import pandas as pd
import pytz
from pandas import DataFrame
from ta.trend import ema_indicator

from src.utils.calculation_utils import cast_money
from src.clients.tink_client import logger_tinkoff_logs

class TinkoffDataFrameFormat:
    """
    класс обработки данных запросов от клиента Тинькофф. Для удобства используется pandas
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    def __init__(self, list_of_all_ticker_figi: list):
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
        return self.list_of_all_ticker_figi[self.list_of_all_ticker_figi['name'].str.match(rex_word) == True]

    def get_figi_by_ticker(self, ticker: str) -> Optional[str]:
        """
        метод позволяющий по тикеру валюты найти интересующий figi-ключ
        :param ticker: -> Str тикер валюты, необходимо точное совпадение
        :return: -> Str фиги-ключ для валюты
        """
        data_frame_ticker_figi = self.list_of_all_ticker_figi[self.list_of_all_ticker_figi['ticker'] == ticker]
        # проверка данных на соответсвие
        if data_frame_ticker_figi.empty:
            logger_tinkoff_logs.error('GETTING TICKER %s FAILED ', ticker)
            return None
        figi_for_ticker = data_frame_ticker_figi['figi'].iloc[0]
        logger_tinkoff_logs.debug('FIGI FOR TICKER %s IS %s', ticker, figi_for_ticker)
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

    def create_df(self) -> Optional[DataFrame]:
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

    def get_xrates_ema_dataframe(self) -> Optional[DataFrame]:
        """
        Метод получения значения средней скользящей для котировок валюты. Значение EMA
        Подробнее и тех анализа трейдеров https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.ema_indicator
        :return: -> DataFrame объект данных  свечей с добавление пункта EMA к каждой записи
        """
        if self.candles is None:
            return None
        candles_df_data = self.create_df()
        candles_df_data['ema'] = ema_indicator(close=candles_df_data['close'], window=9)
        logger_tinkoff_logs.debug('RATES HAVE BEEN RECEIVED')
        return candles_df_data[['time', 'open', 'close', 'high', 'low', 'ema']].tail(30)

    def get_xrate_dict_format(self) -> Tuple[Optional[float], Optional[str]]:
        """
        Метод форматирования данных в формате словаря, с определением максимального текущего курса заданной валюты
        :return: -> Dict словарь с данными максимальных котировок валюты с учетом EMA значением
        """
        if self.candles is None:
            return None, None
        rates_data = self.get_xrates_ema_dataframe()
        # проверка данных на соответствие
        if rates_data is None:
            logger_tinkoff_logs.error('GET RATE WAS CRUSHED')
            return None, None
        # смотрим последние данные для свечи заданной валюты.
        data = rates_data.iloc[-1]
        max_rate = max(data.open, data.close, data.high, data.low)
        max_rate_with_ema = round(max(max_rate, data.ema), 2)
        date = data.time
        dt_Moscow = date.astimezone(pytz.timezone('Europe/Moscow')).strftime('%H:%M  %d/%m/%Y')
        logger_tinkoff_logs.debug('GET RATE WAS ACCOMPLISHED. MAX RATE: %d', max_rate_with_ema)
        message_in = f"USD   : {max_rate}\n" \
                     f"USD ema: {max_rate_with_ema}\n" \
                     f"Update : {dt_Moscow}\n" \
                     f"\n"

        return max_rate_with_ema, message_in
