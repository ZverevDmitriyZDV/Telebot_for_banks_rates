from datetime import datetime, timedelta
import pytz

from pandas import DataFrame
from tinkoff.invest.services import InstrumentsService, MarketDataService
from ta.trend import ema_indicator
from tinkoff.invest import Client, RequestError, CandleInterval, HistoricCandle

import pandas as pd
from tinkoff.invest.utils import now
import os
from dotenv import load_dotenv
import logging
from logger.logger import Zlogger

dotenv_path = os.path.abspath('.env')
load_dotenv(dotenv_path)

tnk_logger = Zlogger('tinkoff_logs')
tnk_logger.logger_config()
tnk_logger.logger_format()
TOKEN = os.environ.get('TOKEN_TINK')

TICKER = 'USD000UTSTOM'
FIG_USD = 'BBG0013HGFT4'

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def get_figi(figi=None, ticker=None):
    if figi is not None:
        logging.debug('FIGI WAS TRANSFERRED')
        return figi
    try:
        with Client(TOKEN) as cl:
            instruments: InstrumentsService = cl.instruments
            market_data: MarketDataService = cl.market_data

            list_of_all_ticker_figi = []
            for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
                for item in getattr(instruments, method)().instruments:
                    list_of_all_ticker_figi.append({
                        'ticker': item.ticker,
                        'figi': item.figi,
                        'type': method,
                        'name': item.name,
                    })

            data_frame_ticker_figi = DataFrame(list_of_all_ticker_figi)
            logging.debug('GETTING ALL TICKER FIGI DATA WAS SUCCESSFUL, %d ELEMENTS HAVE BEEN FOUND',
                          len(list_of_all_ticker_figi))
            if ticker is None:
                pd.set_option('display.max_rows', None)
                logging.debug('TICKER IS NONE, THE LIST OF TICKER TO FIGI \n %s',data_frame_ticker_figi[['ticker','figi','name']])
                pd.set_option('display.max_columns', 500)
                return data_frame_ticker_figi
            data_frame_ticker_figi = data_frame_ticker_figi[data_frame_ticker_figi['ticker'] == ticker]
            if data_frame_ticker_figi.empty:
                logging.error('GETTING TICKER %s FAILED ', ticker)
                return
            figi_for_ticker = data_frame_ticker_figi['figi'].iloc[0]
            logging.debug('FIGI FOR TICKER %s IS %s', ticker, figi_for_ticker)
        return figi_for_ticker
    except RequestError as e:
        logging.error(e.metadata.message)


def run():
    try:
        with Client(TOKEN) as client:
            print(client)
            instruments: InstrumentsService = client.instruments
            market_data: MarketDataService = client.market_data
            figi_usd = get_figi(FIG_USD)
            response = client.market_data.get_candles(
                figi=figi_usd,
                from_=now() - timedelta(days=3),
                to=now(),
                interval=CandleInterval.CANDLE_INTERVAL_HOUR
            )
            if len(response.candles) == 0:
                logging.error('FIGI IS WRONG. NO CANDLES HAVE BEEN FOUNDED')
                return None

            data_frame = create_df(response.candles)
            # https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.ema_indicator
            data_frame['ema'] = ema_indicator(close=data_frame['close'], window=9)
            logging.debug('RATES HAVE BEEN RECEIVED : \n %s', data_frame)
            return data_frame[['time', 'open', 'close', 'high', 'low', 'ema']].tail(30)
    except RequestError as e:
        logging.error(e.metadata.message)


def get_rate_usd():
    rates_data = run()
    if rates_data is None:
        logging.error('GET RATE WAS CRUSHED')
        return None
    data = rates_data.iloc[-1]
    max_rate = max(data.open, data.close, data.high, data.low)
    max_rate_with_ema = round(max(max_rate, data.ema), 2)
    date = data.time

    dt_Moscow = date.astimezone(pytz.timezone('Europe/Moscow')).strftime('%H:%M  %d/%m/%Y')
    logging.debug('GET RATE WAS ACCOMPLISHED. MAX RATE: %d',max_rate_with_ema)
    return dict(
        max_rate=max_rate,
        max_rate_with_ema=max_rate_with_ema,
        time=dt_Moscow
    )


def create_df(candles: [HistoricCandle]):
    df = DataFrame([{
        'time': c.time,
        'volume': c.volume,
        'open': cast_money(c.open),
        'close': cast_money(c.close),
        'high': cast_money(c.high),
        'low': cast_money(c.low),
    } for c in candles])

    return df


def cast_money(v):
    return v.units + v.nano / 1e9  # nano - 9 нулей


if __name__ == '__main__':
    gf = get_figi()
    usd_figi = gf[gf['ticker'].str.match("(US4).*")==True]
    print(usd_figi)