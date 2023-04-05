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
