import datetime
from requests import Response
from datetime import timedelta
from typing import Callable, Optional
from logger.logger import Zlogger

bkkb_logger = Zlogger()
bkkb_logger.name = 'BKKBLOGS'
bkkb_logger.log_file = 'bangkok_bank'
logger_bkkb = bkkb_logger.setup_logger


def buy_rub_knowing_rub(value, rate):
    return round(value / rate, 2)


def buy_rub_knowing_thb(value, rate):
    return round(value * rate, 2)


def cast_money(v):
    """
    функция формирвоания дробного значение котировки валюты
    :param v: объект с данными по значению котировки свечи
    :return: число с плавающей точкой
    """
    return v.units + v.nano / 1e9  # units - целое значение nano - дробное значение 9 нулей после точки


def is_time_to_update(time):
    delta = datetime.datetime.now() - time
    return delta > timedelta(hours=1, minutes=1)


def check_status(msg: str = "default") -> Optional[Response]:
    def decorator(f: Callable[..., Response]):
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)
            if resp.status_code == 401:
                logger_bkkb.error(f'{msg} %s', resp.reason)
                return False
            return resp

        return wrapper

    return decorator
