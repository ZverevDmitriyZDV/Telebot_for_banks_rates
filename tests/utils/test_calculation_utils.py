import datetime

import pytest

from src.utils.calculation_utils import buy_rub_knowing_rub, \
                                        buy_rub_knowing_thb, cast_money, \
                                        is_time_to_update


def test_buy_rub_knowing_rub():
    with pytest.raises(ZeroDivisionError) as e_info:
        buy_rub_knowing_rub(10, 0)
    assert buy_rub_knowing_rub(10, 2) == 5.00
    assert buy_rub_knowing_rub(10, 20) == 0.50


def test_buy_rub_knowing_thb():
    assert buy_rub_knowing_thb(10, 2) == 20.00
    assert buy_rub_knowing_thb(0, 2) == 0.00
    assert buy_rub_knowing_thb(10, 0.25) == 2.50


def test_cast_money():
    class MoneyV:
        def __init__(self, units, nano):
            self.units: int = units
            self.nano: int = nano
    assert cast_money(MoneyV(250, 850000000)) == 250.85
    assert cast_money(MoneyV(0, 150)) == 0.00000015


def test_is_time_to_update():
    time = datetime.datetime(2019,12,4)
    assert is_time_to_update(time=time) == True
    assert is_time_to_update(datetime.datetime.now()) == False