import datetime
from datetime import timedelta
from time import sleep

from bangkok_request import LastUSDToTHBRates
from tinkoff_request import LastUSDToRUBRates
from units import is_time_to_update


class ValueRate:
    '''
    класс для обработки соотношения валюты с учетом всех комиссий
    некоторые комиссии установлены по умолчанию
    '''

    def __init__(self, usd_thb, usd_rub, raif_ex=2.257, swift=3.0, thb_ex=0.21):
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
    def rub_thb(self):
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
    def rub_thb_zdv(self):
        return round(self.rub_thb * 1.02, 2)


class ValueData:
    def __init__(self):
        self.rate = 0
        self.message = ''
        self.time = datetime.datetime.now()

    @property
    def time_update(self):
        need_to_be_updated = is_time_to_update(self.time)
        print(need_to_be_updated)
        if need_to_be_updated:
            self.time = datetime.datetime.now()
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
        self.thb_rates.rate, self.thb_rates.message = self.get_usd_thb_data
        self.tink_rates.rate, self.tink_rates.message = self.get_usd_rub_data
        # self.time_update_usd = self.time_updated()
        # self.time_update_thb = datetime.datetime.now()
        # self.usd_rub, self.usd_rub_message = self.get_usd_rub_data
        # self.usd_thb, self.usd_thb_message = self.get_usd_thb_data
        self.money = ValueRate(usd_thb=self.thb_rates.rate, usd_rub=self.tink_rates.rate)
        self.rub_thb, self.rub_thb_zdv = self.get_thb_rub_rate

    # @property
    # def time_delta_usd(self):
    #     time = datetime.datetime.now()
    #     return is_time_to_update(self.time_update_usd)
    #     # delta = datetime.datetime.now() - self.time_update_usd
    #     # if delta < timedelta(seconds=1):
    #     #     return True
    #     # elif delta > timedelta(hours=1, minutes=1):
    #     #     self.time_update_usd = datetime.datetime.now()
    #     #     return True
    #     # return False
    #
    # @property
    # def time_delta_thb(self):
    #     return is_time_to_update(self.time_update_thb)
    #
    # #     delta = datetime.datetime.now() - self.time_update_thb
    # #     if delta < timedelta(seconds=1):
    # #         return True
    # #     # elif delta > timedelta(hours=1, minutes=1):
    # #     elif delta > timedelta(seconds=15):
    # #         return True
    # #     return False

    @property
    def get_usd_rub_data(self):
        """
        метод определения курса обмена покупка USD за RUB, через Тинькофф банк
        и получение текстового сообщения о дополнительных деталях
        :return: flaot(),str()
        """
        if self.tink_rates.time_update:
            return LastUSDToRUBRates().get_usd_last_rate()

    @property
    def get_usd_thb_data(self):
        """
        метод обмена валюты продажа USD за THB, через  Bangkok Bank
        И получение текстового сообщения о дополнительной информации
        :return: flaot(),str()
        """
        if self.thb_rates.time_update:
            return LastUSDToTHBRates().get_usd_to_thb_rates()

    @property
    def get_thb_rub_rate(self):
        """
        метод определения обмена валюты RUB в THB
        и перезаписи основных переменных
        :return: flaot(),str()
        """
        return self.money.rub_thb, self.money.rub_thb_zdv

    def get_exchange_message_rub_thb(self):
        """
        метод определяющий финальное сообщение значения обмена 1 THB к RUB
        :return: -> float() , str() значение курса, строку с дополнительной информацией
        """
        message_out = f"RUB / THB   : {self.rub_thb}\n" \
                      f"RUB / THB*  : {self.rub_thb_zdv}" \
                      f"\n"
        return self.rub_thb_zdv, message_out


if __name__ == '__main__':
    a1 = ExchangeConvertor()
    print(a1.tink_rates.rate)
    print(a1.tink_rates.message)
    print(a1.thb_rates.rate)
    print(a1.thb_rates.message)
    print(a1.rub_thb)
    print(a1.rub_thb_zdv)
    print(datetime.datetime.now())
    print(a1.thb_rates.time)
    print(a1.tink_rates.time)
    print(a1.get_exchange_message_rub_thb())
    print(a1.thb_rates.time)
    print(a1.tink_rates.time)
    sleep(30)
    print(a1.tink_rates.rate)
    print(a1.tink_rates.message)
    print(a1.thb_rates.rate)
    print(a1.thb_rates.message)
    print(a1.rub_thb)
    print(a1.rub_thb_zdv)
    print(datetime.datetime.now())
    print(a1.thb_rates.time)
    print(a1.tink_rates.time)
    print(a1.get_exchange_message_rub_thb())
    print(a1.thb_rates.time)
    print(a1.tink_rates.time)

