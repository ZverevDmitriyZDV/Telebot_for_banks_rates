from typing import Optional, Tuple

from src.clients.tink_client import TinkoffBankClient
from src.controllers.tink_controller import CandlesDataFrame
from src.utils.bad_auth_exception import BadAuthException


class LastUSDToRUBRates:
    """
    класс для определения последнего обновления котировокл валюыт USD
    """

    def __init__(self):
        """
        метод инициализации клиента Тинькофф банка.
        """
        self.client = TinkoffBankClient()

    def get_usd_last_rate(self) -> Optional[Tuple[float, str]]:
        """
        метод формирования словаря, в котором будет определена информация по последнем курсу для USD
        :return: -> Dict() словарь с данными по котировкам
        """
        # поиск свечей для валюты USD
        try:
            usd_candles_data = self.client.get_usd_candles()
        except BadAuthException:
            return None
        # форматирование данных свечей
        usd_rates_data = CandlesDataFrame(usd_candles_data)
        # форматирование результата в вид словаря
        return usd_rates_data.get_xrate_dict_format()



