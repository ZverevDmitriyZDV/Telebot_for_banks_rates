import datetime
from datetime import timedelta


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
    if delta < timedelta(seconds=1):
        return True
    # elif delta > timedelta(hours=1, minutes=1):
    elif delta > timedelta(seconds=10):
        return True
    return False


