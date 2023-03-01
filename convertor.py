from bangkok_request import LastUSDToTHBRates
from tinkoff_request import LastUSDToRUBRates
import datetime
from datetime import timedelta


class ExchangeConvertor:
    """
    класс для определения конверсии из RUB в THB с учетом и без учета комиссии
    """

    def __init__(self):
        """
        метод инициализации, в котором определяем текущие котировки валют
        """
        self.usd_rub = 0
        self.usd_rub_message = ''
        self.usd_thb = 0
        self.usd_thb_message = ''
        self.time_update = datetime.datetime.now()
        self.rub_thb = 0

    def get_usd_rub_data(self):
        """
        метод определения курса обмена покупка USD за RUB, через Тинькофф банк
        и получение текстового сообщения о дополнительных деталях
        :return: True
        """
        if self.usd_rub != 0:
            return True
        self.usd_rub, self.usd_rub_message = LastUSDToRUBRates().get_usd_last_rate()
        return True

    def get_usd_thb_data(self):
        """
        метод обмена валюты продажа USD за THB, через  Bangkok Bank
        И получение текстового сообщения о дополнительной информации
        :return: True
        """
        if self.usd_thb != 0 and self.usd_thb_message != '':
            return True
        self.usd_thb, self.usd_thb_message = LastUSDToTHBRates().get_usd_to_thb_rates()
        return True

    def get_thb_rub_rate(self, swift=3.0, thb_exange=0.21, raif_exgande=2.257):
        """
        метод определения обмена валюты RUB в THB
        и перезаписи основных переменных
        :param swift: -> float() комиссия банка Райфайзен за Swift перевод
        :param thb_exange: -> float() комиссия банка BangkokBank за прием Swfit перевода и операции пополнения счета
        :param raif_exgande: -> float() комиссия броке Райфайзен банка за совершение брокерской операции
        :return: True
        """
        # проверка ненулевых значений котировок, для просчета курса обмена
        if self.rub_thb != 0:
            return True
        if self.usd_thb == 0:
            self.get_usd_thb_data()
        if self.usd_rub == 0:
            self.get_usd_rub_data()
        # формула расчета конверсии 1 RUB в THB
        thb_rub = float(self.usd_thb) / float(self.usd_rub) * (1 - raif_exgande / 100) * (1 - swift / 100) * (
                1 - thb_exange / 100)
        # формула обмена 1 THB к RUB
        self.rub_thb = round(1 / thb_rub, 2)
        return True

    def get_exchange_message_rub_thb(self):
        """
        метод определяющий финальное сообщение значения обмена 1 THB к RUB
        :return: -> float() , str() значение курса, строку с дополнительной информацией
        """
        self.get_thb_rub_rate()
        rub_thb_zdv = round(self.rub_thb * 1.02, 2)
        message_out = f"RUB / THB   : {self.rub_thb}\n" \
                      f"RUB / THB*  : {rub_thb_zdv}" \
                      f"\n"
        return rub_thb_zdv, message_out

    def reset_rate_data(self):
        """
        метод возвращающий значения в дефолтное состояние после проверки
        :return: True
        """
        delta = datetime.datetime.now() - self.time_update
        if delta > timedelta(hours=1, minutes=1):
            self.usd_rub = 0
            self.usd_rub_message = ''
            self.usd_thb = 0
            self.usd_thb_message = ''
            self.rub_thb = 0
        return True
