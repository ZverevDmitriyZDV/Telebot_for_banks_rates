import datetime
import re
from tinkoff.invest import HistoricCandle, Quotation

from src.controllers.tink_controller import TinkoffDataFrameFormat, CandlesDataFrame

TINK_FIGI_LIST = [
    {'ticker': 'CoV2', 'figi': 'FUTCO1022000', 'type': 'futures', 'name': 'Co-10.22 Медь'},
    {'ticker': 'GDZ3', 'figi': 'FUTGOLD12230', 'type': 'futures', 'name': 'GOLD-12.23 Золото'},
    {'ticker': 'CFM2', 'figi': 'FUTUCHF06220', 'type': 'futures',
     'name': 'UCHF-6.22 Курс доллар США - Швейцарский франк'},
    {'ticker': 'SGU2', 'figi': 'FUTSNGP09220', 'type': 'futures',
     'name': 'SNGP-9.22 Сургутнефтегаз (привилегированные)'},
    {'ticker': 'MAM2', 'figi': 'FUTMMI062200', 'type': 'futures', 'name': 'MMI-6.22 Индекс Металлов и добычи'},
    {'ticker': 'RMZ2', 'figi': 'FUTRTSM12220', 'type': 'futures', 'name': 'RTSM-12.22 Индекс РТС (мини)'},
    {'ticker': 'MMZ5', 'figi': 'FUTMXI122500', 'type': 'futures', 'name': 'MXI-12.25 Индекс МосБиржи (мини)'},
    {'ticker': 'RIH2', 'figi': 'FUTRTS032200', 'type': 'futures', 'name': 'RTS-3.22 Индекс РТС'},
    {'ticker': 'BRU2', 'figi': 'FUTBR0922000', 'type': 'futures', 'name': 'BR-9.22 Нефть Brent'},
    {'ticker': 'PIM2', 'figi': 'FUTPIKK06220', 'type': 'futures', 'name': 'PIKK-6.22 ПИК'},
    {'ticker': 'GZM2', 'figi': 'FUTGAZR06220', 'type': 'futures', 'name': 'GAZR-6.22 Газпром'},
    {'ticker': 'SAH2', 'figi': 'FUTSUGR03220', 'type': 'futures', 'name': 'SUGR-3.22 Сахар'},
    {'ticker': 'CRM2', 'figi': 'FUTCNY062200', 'type': 'futures', 'name': 'CNY-6.22 Курс Юань - Рубль'},
    {'ticker': 'SXZ2', 'figi': 'FUTSTOX12220', 'type': 'futures', 'name': 'STOX-12.22 EURO STOXX 50'},
    {'ticker': 'IRM3', 'figi': 'FUTIRAO06230', 'type': 'futures', 'name': 'IRAO-6.23 Интер РАО ЕЭС'},
    {'ticker': 'NGF2', 'figi': 'FUTNG0122000', 'type': 'futures', 'name': 'NG-1.22 Природный газ'},
    {'ticker': 'SFZ3', 'figi': 'FUTSPYF12230', 'type': 'futures', 'name': 'SPYF-12.23 S&P 500'},
    {'ticker': 'RLM2', 'figi': 'FUTRUAL06220', 'type': 'futures', 'name': 'RUAL-6.22 РУСАЛ'}
]

CANDLES_HISTORY = [
    HistoricCandle(open=Quotation(units=35548, nano=0), high=Quotation(units=35548, nano=0),
                   low=Quotation(units=35548, nano=0), close=Quotation(units=35548, nano=0), volume=1,
                   time=datetime.datetime(2023, 4, 3, 6, 0, tzinfo=datetime.timezone.utc), is_complete=True),
    HistoricCandle(open=Quotation(units=35547, nano=0), high=Quotation(units=35753, nano=0),
                   low=Quotation(units=35547, nano=0), close=Quotation(units=35682, nano=0), volume=18,
                   time=datetime.datetime(2023, 4, 3, 7, 0, tzinfo=datetime.timezone.utc), is_complete=True),
    HistoricCandle(open=Quotation(units=35693, nano=0), high=Quotation(units=35693, nano=0),
                   low=Quotation(units=35693, nano=0), close=Quotation(units=35693, nano=0), volume=1,
                   time=datetime.datetime(2023, 4, 3, 8, 0, tzinfo=datetime.timezone.utc), is_complete=True),
    HistoricCandle(open=Quotation(units=35690, nano=0), high=Quotation(units=35839, nano=0),
                   low=Quotation(units=35690, nano=0), close=Quotation(units=35839, nano=0), volume=8,
                   time=datetime.datetime(2023, 4, 3, 9, 0, tzinfo=datetime.timezone.utc), is_complete=True)]

tink_df_data = TinkoffDataFrameFormat(TINK_FIGI_LIST)
candles_df_data = CandlesDataFrame(CANDLES_HISTORY)


def test_get_ticker_by_rex():
    rex_name = '.*(Индекс).*'
    result_name_list_needed = ['MMI-6.22 Индекс Металлов и добычи',
                               'RTSM-12.22 Индекс РТС (мини)',
                               'MXI-12.25 Индекс МосБиржи (мини)',
                               'RTS-3.22 Индекс РТС']
    result_data = tink_df_data.get_ticker_by_rex(rex_name)
    result_name_list = result_data['name'].to_list()
    assert result_data.empty is False
    assert len(result_data) == 4
    assert result_name_list == result_name_list_needed


def test_get_ticker_by_incorrect_rex():
    rex_name = '.*INCORRECT_REX_NAME.*'
    result_data = tink_df_data.get_ticker_by_rex(rex_name)
    assert len(result_data) == 0


def test_figi_by_ticker():
    crm_figi = tink_df_data.get_figi_by_ticker('CRM2')
    assert crm_figi == 'FUTCNY062200'


def test_figi_by_ticker_incorrect():
    figi_incorrect = tink_df_data.get_figi_by_ticker('INCORRECT_TICKER')
    assert figi_incorrect is None


def test_create_candles_df():
    candles_df = candles_df_data.create_df()
    headers_list_needed = ['time', 'volume', 'open', 'close', 'high', 'low']
    candles_header_list = candles_df.columns.tolist()
    assert len(candles_df) == 4
    assert candles_header_list == headers_list_needed


def test_create_none_candles_df():
    none_candles = CandlesDataFrame(None)
    assert none_candles.create_df() is None


def test_xrate_ema_dataframe():
    new_candles_df = candles_df_data.get_xrates_ema_dataframe()
    headers_list_needed = ['time', 'open', 'close', 'high', 'low', 'ema']
    candles_header_list = new_candles_df.columns.tolist()
    assert len(headers_list_needed) == 6
    assert headers_list_needed[-1] == 'ema'
    assert headers_list_needed == candles_header_list


def test_xrate_ema_none_dataframe():
    none_candles = CandlesDataFrame(None)
    assert none_candles.get_xrates_ema_dataframe() is None


def test_get_xrate_dict_format_from_none_candles():
    none_candles = CandlesDataFrame(None)
    assert none_candles.get_xrate_dict_format() == (None, None)


def test_get_xrate_dict_format():
    max_rate, message = candles_df_data.get_xrate_dict_format()
    reg = r'(Update : )(\S*\s*\S*)'
    update_time = re.search(reg, message).group(0)
    time_correct_result = 'Update : 12:00  03/04/2023'
    assert type(message) == str
    assert message.count('\n') == 4
    assert update_time == time_correct_result
    assert max_rate == 35839.0

