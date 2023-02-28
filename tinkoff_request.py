from datetime import datetime, timedelta
import pytz
from pandas import DataFrame
from tinkoff.invest.services import InstrumentsService, MarketDataService
from ta.trend import ema_indicator
from tinkoff.invest import Client, RequestError, CandleInterval, HistoricCandle
import pandas as pd
from tinkoff.invest.utils import now
import os
from dotenv import load_dotenv
import logging
from logger.logger import Zlogger
from bangkok_request import BankAPI

# константы для валюты обмена USD
TICKER_USD = 'USD000UTSTOM'
FIGI_USD = 'BBG0013HGFT4'

tnk_logger = Zlogger('tinkoff_logs')
tnk_logger.logger_config()
tnk_logger.logger_format()

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class TinkoffBank(BankAPI):
    """
    реализация класса подключения к клиенту брокера Тинькофф и осуществления запросов последних котировок японский
    свечей валют
    """

    def __init__(self, token_name):
        """
        Инициализация подключения к клиенту брокера
        :param token_name:  токен подключения к клиенту
        """
        self.token_name = token_name

    def get_token(self):
        """
        получение сохраненного токена из файл .env или окружения HEROKU / GIT в зависимости от ресурса на котором
        будет произведено развертывание проекта.
        :return: токен доступа для подключения к клиенту
        """
        load_dotenv(os.path.abspath('.env'))
        return os.environ.get(self.token_name)

    def get(self):
        """
        метод осуществления проверки корректного подключения к клиенту.
        проверяет правильность токена путем получения информации о пользователе.
        :return: True / False
        """
        try:
            with Client(self.get_token()) as cl:
                _ = cl.users.get_info()
                return True
        except RequestError as e:
            # в случае ошибки подключения осуществить запись логов в файл
            logging.error(e.metadata.message)
            return False

    def get_all_figi_list(self):
        """
        метод получения соотношения Тикетов валют, их названий и кода валюты FIGI для дальнейших корректных запросов
        :return: -> list() список данных по каждой валюте, по которой проходят торговые операции
        """
        # проверка подключению к клиенту
        if not self.get():
            return None
        # поиск всех валют по которым проходят торговые операции(method), все данные хранятся во внутреннем классе
        # InstrumentsService
        with Client(self.get_token()) as cl:
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
        logging.debug('''ALL FIGI'S LIST HAVE BEEN FOUND''')
        return list_of_all_ticker_figi

    def get_candles_by_figi(self, figi):
        """
        метод получения свечей по заданному коду FIGI
        период отслеживания данных в течении последних 3-х дней
        данные свечей - часовые свечи
        при изменении параметров могут возникнуть ошибки перегрузки запросов и блокировка со стороны Тинькофф клиента
        :param figi: -> Str строковое обозначение код-ключа FIGI
        :return: -> List список данных часовых свечей в течении 3-х дней
        """
        # проверка возможности подключения
        if not self.get():
            return None
        # поиск информации японских торговых свечей для определенной валюты. Код валюты передается через FIGI
        # для реализации используется внутренний класс MarketDataService
        with Client(self.get_token()) as client:
            market_data: MarketDataService = client.market_data
            response = client.market_data.get_candles(
                figi=figi,
                from_=now() - timedelta(days=3),
                to=now(),
                interval=CandleInterval.CANDLE_INTERVAL_HOUR
            )
            # проверка ответа на корректность исходного запроса
            if len(response.candles) == 0:
                logging.error('FIGI IS WRONG. NO CANDLES HAVE BEEN FOUNDED')
                return None
            logging.debug('CANDLES INFO FOR FIGI %s HAVE BEEN FOUND', figi)
            return response.candles

    def get_usd_candles(self):
        """
        метод получения свечей для валюты USD
        для осуществления необходимо знать точное значение FIGI_USD
        :return: -> List список данных часовых свечей для USD в течении 3-х дней
        """
        logging.debug('CANDLES INFO FOR USD HAVE BEEN FOUND')
        return self.get_candles_by_figi(FIGI_USD)


class TinkoffDataFrameFormat:
    """
    класс обработки данных запросов от клиента Тинькофф. Для удобства используется pandas
    """

    def __init__(self, list_of_all_ticker_figi):
        """
        метод инициализации класса
        :param list_of_all_ticker_figi: список дынных всех валют с информацие по названию / тикеру / figi-кода.
        """
        # преобразуем данные в DataFrame объет для удобства обращения
        self.list_of_all_ticker_figi = DataFrame(list_of_all_ticker_figi)

    def get_ticker_by_rex(self, rex_word):
        """
        метод позволяющий по ключевому выражению осуществить поиск близких совпадений для данных валюты.
        поиск осуществляется по ticker
        :param rex_word: -> Str регулярное выражение для валюты
        :return: -> DataFrame объект с названием / тикетом/ figi ключом интересующей валюты
        """
        return self.list_of_all_ticker_figi[self.list_of_all_ticker_figi['ticker'].str.match(rex_word) == True]

    def get_figi_by_ticker(self, ticker):
        """
        метод позволяющий по тикеру валюты найти интересующий figi-ключ
        :param ticker: -> Str тикер валюты, необходимо точное совпадение
        :return: -> Str фиги-ключ для валюты
        """
        data_frame_ticker_figi = self.list_of_all_ticker_figi[self.list_of_all_ticker_figi['ticker'] == ticker]
        # проверка данных на соответсвие
        if data_frame_ticker_figi.empty:
            logging.error('GETTING TICKER %s FAILED ', ticker)
            return
        figi_for_ticker = data_frame_ticker_figi['figi'].iloc[0]
        logging.debug('FIGI FOR TICKER %s IS %s', ticker, figi_for_ticker)
        return figi_for_ticker


class CandlesDataFrame:
    """
    класс для обработки данных свечей валют
    """

    def __init__(self, candles):
        """
        метод инициализации
        :param candles: -> List список данных запроса японских свечей определнной валюты
        """
        self.candles = candles

    def create_df(self):
        """
        метод преобразования списка в DataFrame объект с выделением конкретной информации и преобразованием валют
        :return: -> DataFrame объект данных свечей с форматированными данными по стоимости
        """
        # данные открытия / закрытия свечей имеют имеют дробные значение. банком данные цифры определены с точностью
        # до 9 знака. для получения корректных котировок необходимо преобрпзовать данные
        candles_df_data = DataFrame([{
            'time': candle.time,
            'volume': candle.volume,
            'open': cast_money(candle.open),
            'close': cast_money(candle.close),
            'high': cast_money(candle.high),
            'low': cast_money(candle.low),
        } for candle in self.candles])
        return candles_df_data

    def get_xrates_ema_dataframe(self):
        """
        Метод получения значения средней скользящей для котировок валюты. Значение EMA
        Подробнее и тех анализа трейдеров https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.ema_indicator
        :return: -> DataFrame объект данных  свечей с добавление пункта EMA к каждой записи
        """
        candles_df_data = self.create_df()
        candles_df_data['ema'] = ema_indicator(close=candles_df_data['close'], window=9)
        logging.debug('RATES HAVE BEEN RECEIVED : \n %s', candles_df_data)
        return candles_df_data[['time', 'open', 'close', 'high', 'low', 'ema']].tail(30)

    def get_xrate_dict_format(self):
        """
        Метод форматирования данных в формате словаря, с определением максимального текущего курса заданной валюты
        :return: -> Dict словарь с данными максимальных котировок валюты с учетом EMA значением
        """
        rates_data = self.get_xrates_ema_dataframe()
        # проверка данных на соответствие
        if rates_data is None:
            logging.error('GET RATE WAS CRUSHED')
            return None
        # смотрим последние данные для свечи заданной валюты.
        data = rates_data.iloc[-1]
        max_rate = max(data.open, data.close, data.high, data.low)
        max_rate_with_ema = round(max(max_rate, data.ema), 2)
        date = data.time
        dt_Moscow = date.astimezone(pytz.timezone('Europe/Moscow')).strftime('%H:%M  %d/%m/%Y')
        logging.debug('GET RATE WAS ACCOMPLISHED. MAX RATE: %d', max_rate_with_ema)
        message_in = f"USD   : {max_rate}\n" \
                     f"USD ema: {max_rate_with_ema}\n" \
                     f"Update : {dt_Moscow}\n" \
                     f"\n"

        return max_rate_with_ema, message_in


def cast_money(v):
    """
    функция формирвоания дробного значение котировки валюты
    :param v: объект с данными по значению котировки свечи
    :return: число с плавающей точкой
    """
    return v.units + v.nano / 1e9  # units - целое значение nano - дробное значение 9 нулей после точки


class LastUSDToRUBRates:
    """
    класс для определения последнего обновления котировокл валюыт USD
    """

    def __init__(self):
        """
        метод инициализации клиента Тинькофф банка.
        """
        self.client = TinkoffBank('TOKEN_TINK')

    def get_usd_last_rate(self):
        """
        метод формирования словаря, в котором будет определена информация по последнем курсу для USD
        :return: -> Dict() словарь с данными по котировкам
        """
        # поиск свечей для валюты USD
        usd_candles_data = self.client.get_usd_candles()
        # форматирование данных свечей
        usd_rates_data = CandlesDataFrame(usd_candles_data)
        # форматировоание результата в вид словаря
        return usd_rates_data.get_xrate_dict_format()



if __name__ == '__main__':
    ## построчное исполненение
    # tnk_client = TinkoffBank('TOKEN_TINK')
    # fig_list = tnk_client.get_all_figi_list()
    # ticker_list = TickerFigiObject(fig_list)
    # usd_rex = "(US).*"
    # print(ticker_list.get_figi_by_ticker(TICKER))
    # usd_candles_data = tnk_client.get_usd_candles()
    # print(figi_data)
    # money = CandlesDataFrame(usd_candles_data)
    # usd_last_rate, message = money.get_xrate_dict_format()
    # print(usd_last_rate, message)
    # реализация класса
    tink_usd = LastUSDToRUBRates()
    print(tink_usd.get_usd_last_rate())

# def get_figi(figi=None, ticker=None):
#     if figi is not None:
#         logging.debug('FIGI WAS TRANSFERRED')
#         return figi
#     try:
#         with Client(TOKEN) as cl:
#             instruments: InstrumentsService = cl.instruments
#             market_data: MarketDataService = cl.market_data
#
#             list_of_all_ticker_figi = []
#             for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
#                 for item in getattr(instruments, method)().instruments:
#                     list_of_all_ticker_figi.append({
#                         'ticker': item.ticker,
#                         'figi': item.figi,
#                         'type': method,
#                         'name': item.name,
#                     })
#
#             data_frame_ticker_figi = DataFrame(list_of_all_ticker_figi)
#             logging.debug('GETTING ALL TICKER FIGI DATA WAS SUCCESSFUL, %d ELEMENTS HAVE BEEN FOUND',
#                           len(list_of_all_ticker_figi))
#             if ticker is None:
#                 pd.set_option('display.max_rows', None)
#                 logging.debug('TICKER IS NONE, THE LIST OF TICKER TO FIGI \n %s',data_frame_ticker_figi[['ticker','figi','name']])
#                 pd.set_option('display.max_columns', 500)
#                 return data_frame_ticker_figi
#             data_frame_ticker_figi = data_frame_ticker_figi[data_frame_ticker_figi['ticker'] == ticker]
#             if data_frame_ticker_figi.empty:
#                 logging.error('GETTING TICKER %s FAILED ', ticker)
#                 return
#             figi_for_ticker = data_frame_ticker_figi['figi'].iloc[0]
#             logging.debug('FIGI FOR TICKER %s IS %s', ticker, figi_for_ticker)
#         return figi_for_ticker
#     except RequestError as e:
#         logging.error(e.metadata.message)
#
#
# def run():
#     try:
#         with Client(TOKEN) as client:
#             print(client)
#             instruments: InstrumentsService = client.instruments
#             market_data: MarketDataService = client.market_data
#             figi_usd = get_figi(FIG_USD)
#             response = client.market_data.get_candles(
#                 figi=figi_usd,
#                 from_=now() - timedelta(days=3),
#                 to=now(),
#                 interval=CandleInterval.CANDLE_INTERVAL_HOUR
#             )
#             if len(response.candles) == 0:
#                 logging.error('FIGI IS WRONG. NO CANDLES HAVE BEEN FOUNDED')
#                 return None
#
#             data_frame = create_df(response.candles)
#             # https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.ema_indicator
#             data_frame['ema'] = ema_indicator(close=data_frame['close'], window=9)
#             logging.debug('RATES HAVE BEEN RECEIVED : \n %s', data_frame)
#             return data_frame[['time', 'open', 'close', 'high', 'low', 'ema']].tail(30)
#     except RequestError as e:
#         logging.error(e.metadata.message)
#
#
# def get_rate_usd():
#     rates_data = run()
#     if rates_data is None:
#         logging.error('GET RATE WAS CRUSHED')
#         return None
#     data = rates_data.iloc[-1]
#     max_rate = max(data.open, data.close, data.high, data.low)
#     max_rate_with_ema = round(max(max_rate, data.ema), 2)
#     date = data.time
#
#     dt_Moscow = date.astimezone(pytz.timezone('Europe/Moscow')).strftime('%H:%M  %d/%m/%Y')
#     logging.debug('GET RATE WAS ACCOMPLISHED. MAX RATE: %d',max_rate_with_ema)
#     return dict(
#         max_rate=max_rate,
#         max_rate_with_ema=max_rate_with_ema,
#         time=dt_Moscow
#     )
#
# if __name__ == '__main__':
#     gf = get_figi()
#     usd_figi = gf[gf['ticker'].str.match("(US4).*")==True]
#     print(usd_figi)
