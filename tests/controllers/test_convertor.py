import datetime

from src.controllers.convertor import ValueRate, ValueData, ExchangeConvertor


def test_rub_thb_with_zero():
    money = ValueRate()
    assert money.rub_thb == 0
    assert money.rub_thb_zdv == 0


def test_rub_thb_normal_data():
    money = ValueRate(usd_thb=30, usd_rub=30, raif_ex=0, swift=0, thb_ex=0)
    assert money.rub_thb == 1.00
    assert money.rub_thb_zdv == 1.02


def test_time_to_update_no_need():
    value_data = ValueData()
    value_data._time = datetime.datetime.now()
    assert value_data.time_update is False


def test_time_to_update_needed():
    value_data = ValueData()
    assert value_data.time_update is True


def test_get_usd_rub_data_no_need_to_update():
    convertor = ExchangeConvertor()
    convertor.tink_rates._time = datetime.datetime.now()
    convertor.get_usd_rub_data()
    assert convertor.tink_rates.rate == 0
    assert convertor.tink_rates.message == ''


def test_get_usd_rub_data():
    convertor = ExchangeConvertor()
    convertor.get_usd_rub_data()
    assert convertor.tink_rates.rate != 0
    assert convertor.tink_rates.message != ''


def test_get_usd_thb_data_no_need_to_update():
    convertor = ExchangeConvertor()
    convertor.thb_rates._time = datetime.datetime.now()
    convertor.get_usd_thb_data()
    assert convertor.thb_rates.rate == 0
    assert convertor.thb_rates.message == ''


def test_get_usd_thb_data():
    convertor = ExchangeConvertor()
    convertor.get_usd_thb_data()
    assert convertor.thb_rates.rate != 0
    assert convertor.thb_rates.message != ''


def test_get_thb_rub_rate():
    convertor = ExchangeConvertor()
    convertor.thb_rates.rate = 30
    convertor.tink_rates.rate = 30
    convertor.money = ValueRate(raif_ex=0, swift=0, thb_ex=0)
    assert convertor.get_thb_rub_rate() == (1.0, 1.02)


def test_get_exchange_message_no_need_to_update():
    convertor = ExchangeConvertor()
    convertor.thb_rates.rate = 30
    convertor.tink_rates.rate = 30
    convertor.money = ValueRate(raif_ex=0, swift=0, thb_ex=0)
    convertor.tink_rates._time = datetime.datetime.now()
    convertor.thb_rates._time = datetime.datetime.now()
    rate, message = convertor.get_exchange_message_rub_thb()
    assert rate == 1.02
    assert convertor.thb_rates.rate == 30
    assert convertor.tink_rates.rate == 30


def test_get_exchange_message_tink_no_need_to_update():
    convertor = ExchangeConvertor()
    convertor.tink_rates.rate = 1
    convertor.thb_rates.rate = 30
    convertor.money = ValueRate(raif_ex=0, swift=0, thb_ex=0)
    convertor.tink_rates._time = datetime.datetime.now()
    rate, message = convertor.get_exchange_message_rub_thb()
    assert rate != 1.02
    assert convertor.tink_rates.rate == 1
    assert convertor.thb_rates.rate != 30
    assert datetime.datetime.now() - convertor.thb_rates._time < datetime.timedelta(minutes=1)
    assert datetime.datetime.now() - convertor.tink_rates._time < datetime.timedelta(minutes=1)


def test_get_exchange_message_bkkb_no_need_to_update():
    convertor = ExchangeConvertor()
    convertor.tink_rates.rate = 1
    convertor.thb_rates.rate = 30
    convertor.money = ValueRate(raif_ex=0, swift=0, thb_ex=0)
    convertor.thb_rates._time = datetime.datetime.now()
    rate, message = convertor.get_exchange_message_rub_thb()
    assert rate != 1.02
    assert convertor.tink_rates.rate != 1
    assert convertor.thb_rates.rate == 30
    assert datetime.datetime.now() - convertor.thb_rates._time < datetime.timedelta(minutes=1)
    assert datetime.datetime.now() - convertor.tink_rates._time < datetime.timedelta(minutes=1)


def test_get_exchange_message_need_to_update():
    convertor = ExchangeConvertor()
    convertor.tink_rates.rate = 1
    convertor.thb_rates.rate = 1
    convertor.money = ValueRate(raif_ex=0, swift=0, thb_ex=0)
    rate, message = convertor.get_exchange_message_rub_thb()
    assert rate != 1.02
    assert convertor.tink_rates.rate != 1
    assert convertor.thb_rates.rate != 1
    assert datetime.datetime.now() - convertor.thb_rates._time < datetime.timedelta(minutes=1)
    assert datetime.datetime.now() - convertor.tink_rates._time < datetime.timedelta(minutes=1)

