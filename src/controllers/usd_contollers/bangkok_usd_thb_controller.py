from typing import Optional

from src.controllers.const import BKK_USD_FAMILY
from src.controllers.bkkb_controller import BKKBDataFrameFormat
from src.utils.bad_auth_exception import BadAuthException


class LastUSDToTHBRates:
    def __init__(self):
        # объявление клиента
        self.client = BKKBDataFrameFormat()

    def get_usd_to_thb_rates(self) -> Optional[tuple]:
        # определяем дату последнего обновления котировок
        try:
            usd_last_update = self.client.format_update_data()
            # определяем курс обмена валюты USD в THB для внутреннго клиента банка
        except BadAuthException:
            return None
        return self.client.format_get_x_rate(usd_last_update, BKK_USD_FAMILY)


if __name__ == '__main__':
    # # # объявление киента
    # client = BKKBClient('TOKEN_BANGKOK')
    # # поиск возможных совпадений
    # client2 = BKKBDataFrameFormat('TOKEN_BANGKOK')
    # a2 = client2.format_all_values_family()
    # print(a2)
    # usd_family = client2.format_get_close_families_by_reg_name('Dollar')
    # # поиск семейства для USD
    # family = client2.format_get_family_by_currency('US Dollar 50-100')
    # print(type(family))
    # print(family)
    # # определяем дату последнего обновления котировок
    # time_update_date = client2.format_update_data()
    # print(usd_family)
    # print(time_update_date)
    # # определяем курс обмена валюты USD в THB для внутреннго клиента банка
    # b2 = client2.format_get_x_rate(time_update_date, family)
    # print(type(b2))
    # usd_thb, message = client2.format_get_x_rate(time_update_date, family)
    thb_rate = LastUSDToTHBRates()
    print(thb_rate.get_usd_to_thb_rates())
