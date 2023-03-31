import datetime
from datetime import timedelta
from time import sleep

from src.controllers.usd_contollers.bangkok_usd_thb_controller import LastUSDToTHBRates
from src.controllers.const import RAIF_EX, SWIFT_RAIF, SWIFT_BKKB
from src.controllers.usd_contollers.tinkoff_usd_rub_controller import LastUSDToRUBRates
from src.utils.calculation_utils import is_time_to_update


class ValueRate:
    '''
    класс для обработки соотношения валюты с учетом всех комиссий
    некоторые комиссии установлены по умолчанию
    '''

    def __init__(self, usd_thb: float = 0, usd_rub: float = 0, raif_ex: float = RAIF_EX, swift :float = SWIFT_RAIF, thb_ex: float = SWIFT_BKKB):
        '''
        :param usd_thb: курс доллара к thb
        :param usd_rub: курс рубля к usd
        :param raif_ex: комиссия райфайзен банка броккера
        :param swift: комиссия за swift перевод
        :param thb_ex: комиссия приемы валюты
        '''
        self.usd_thb = float(usd_thb)
        self.usd_rub = float(usd_rub)
        self.raif_ex = float(raif_ex)
        self.swift = float(swift)
        self.thb_ex = float(thb_ex)

    @property
    def rub_thb(self) -> float:
        if self.usd_thb == 0 or self.usd_rub == 0:
            return 0
        thb_rub = round(
            self.usd_thb / self.usd_rub *
            (1 - self.raif_ex / 100) *
            (1 - self.swift / 100) *
            (1 - self.thb_ex / 100),
            2)
        return round(1 / thb_rub, 2)

    @property
    def rub_thb_zdv(self) -> float:
        return round(self.rub_thb * 1.02, 2)


class ValueData:
    def __init__(self, rate: float = 0, message: str = ''):
        self.rate = rate
        self.message = message
        self._time = datetime.datetime.now() - timedelta(days=1)

    @property
    def time_update(self) -> bool:
        need_to_be_updated = is_time_to_update(self._time)
        if need_to_be_updated:
            self._time = datetime.datetime.now()
        return need_to_be_updated


class ExchangeConvertor:
    """
    класс для определения конверсии из RUB в THB с учетом и без учета комиссии
    """

    def __init__(self):
        """
        метод инициализации, в котором определяем текущие котировки валют
        """
        self.thb_rates = ValueData()
        self.tink_rates = ValueData()
        self.money = ValueRate()

    def get_usd_rub_data(self) -> ValueData:
        """
        метод определения курса обмена покупка USD за RUB, через Тинькофф банк
        и получение текстового сообщения о дополнительных деталях
        :return: flaot(),str()
        """

        if self.tink_rates.time_update:
            self.tink_rates.rate, self.tink_rates.message = LastUSDToRUBRates().get_usd_last_rate()
            return self.tink_rates

    def get_usd_thb_data(self) -> ValueData:
        """
        метод обмена валюты продажа USD за THB, через  Bangkok Bank
        И получение текстового сообщения о дополнительной информации
        :return: ValueData
        """
        if self.thb_rates.time_update:
            self.thb_rates.rate, self.thb_rates.message = LastUSDToTHBRates().get_usd_to_thb_rates()
        return self.thb_rates

    def get_thb_rub_rate(self) -> (float, str):
        """
        метод определения обмена валюты RUB в THB
        и перезаписи основных переменных
        :return: flaot(),str()
        """
        self.money.usd_thb = self.thb_rates.rate
        self.money.usd_rub = self.tink_rates.rate
        return self.money.rub_thb, self.money.rub_thb_zdv

    def get_exchange_message_rub_thb(self) -> (float, str):
        self.get_usd_thb_data()
        self.get_usd_rub_data()
        self.get_thb_rub_rate()
        """
        метод определяющий финальное сообщение значения обмена 1 THB к RUB
        :return: -> float() , str() значение курса, строку с дополнительной информацией
        """
        message_out = f"RUB / THB   : {self.money.rub_thb}\n" \
                      f"RUB / THB*  : {self.money.rub_thb_zdv}" \
                      f"\n"
        return self.money.rub_thb_zdv, message_out


# if __name__ == '__main__':
#     a1 = ExchangeConvertor()
#     print(a1.money.usd_thb)
#     print(a1.money.usd_rub)
#     print(a1.get_exchange_message_rub_thb())
#     print(a1.money.usd_thb)
#     print(a1.money.usd_rub)
#     print(a1.thb_rates._time)
#     sleep(30)
#     print(a1.money.usd_thb)
#     print(a1.money.usd_rub)
#     print(a1.get_exchange_message_rub_thb())
#     print(a1.money.usd_thb)
#     print(a1.money.usd_rub)
#     print(a1.thb_rates._time)
