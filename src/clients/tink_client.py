from datetime import timedelta
from typing import Optional

from tinkoff.invest import Client, RequestError, CandleInterval
from tinkoff.invest.services import InstrumentsService, MarketDataService
from tinkoff.invest.utils import now

from src.clients.base_api_class import BankAPI
from src.clients.const import FIGI_USD

from src.utils.http_tink_utils import logger_tinkoff_logs, check_status_client


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

    @check_status_client()
    def get_data(self) -> Optional:
        return Client(self.token_name)

    def get_all_figi_list(self) -> Optional[list]:
        """
        метод получения соотношения Тикетов валют, их названий и кода валюты FIGI для дальнейших корректных запросов
        :return: -> list() список данных по каждой валюте, по которой проходят торговые операции
        """
        # поиск всех валют по которым проходят торговые операции(method), все данные хранятся во внутреннем классе
        with self.get_data() as cl:
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
            logger_tinkoff_logs.debug('''ALL FIGI'S LIST HAVE BEEN FOUND''')
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

        # поиск информации японских торговых свечей для определенной валюты. Код валюты передается через FIGI
        # для реализации используется внутренний класс MarketDataService
        with self.get_data() as client:
            market_data: MarketDataService = client.market_data
            response = client.market_data.get_candles(
                figi=figi,
                from_=now() - timedelta(days=3),
                to=now(),
                interval=CandleInterval.CANDLE_INTERVAL_HOUR
            )
            # проверка ответа на корректность исходного запроса
            if len(response.candles) == 0:
                logger_tinkoff_logs.error('FIGI IS WRONG. NO CANDLES HAVE BEEN FOUNDED')
                return None
            logger_tinkoff_logs.debug('CANDLES INFO FOR FIGI %s HAVE BEEN FOUND', figi)
            return response.candles

    def get_usd_candles(self) -> Optional[list]:
        """
        метод получения свечей для валюты USD
        для осуществления необходимо знать точное значение FIGI_USD
        :return: -> List список данных часовых свечей для USD в течении 3-х дней
        """
        logger_tinkoff_logs.debug('CANDLES INFO FOR USD HAVE BEEN FOUND')
        return self.get_candles_by_figi(FIGI_USD)
