from datetime import datetime, timedelta
import pytz

from pandas import DataFrame
from tinkoff.invest.services import InstrumentsService, MarketDataService
from ta.trend import ema_indicator
from tinkoff.invest import Client, RequestError, CandleInterval, HistoricCandle

import pandas as pd
from tinkoff.invest.utils import now
import os

TOKEN = os.environ.get('TOKEN_TINK')

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

TICKER = 'USD000UTSTOM'
FIG_USD = 'BBG0013HGFT4'


def get_figi(figi=None):
    if figi is not None:
        return figi
    with Client(TOKEN) as cl:
        instruments: InstrumentsService = cl.instruments
        market_data: MarketDataService = cl.market_data

        l = []
        for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
            for item in getattr(instruments, method)().instruments:
                l.append({
                    'ticker': item.ticker,
                    'figi': item.figi,
                    'type': method,
                    'name': item.name,
                })

        df = DataFrame(l)
        df = df[df['ticker'] == TICKER]
        if df.empty:
            print(f"Нет тикера {TICKER}")
            return
    return df['figi'].iloc[0]


def run():
    try:
        with Client(TOKEN) as client:
            instruments: InstrumentsService = client.instruments
            market_data: MarketDataService = client.market_data
            figi_usd = get_figi(FIG_USD)
            response = client.market_data.get_candles(
                figi=figi_usd,
                from_=now() - timedelta(days=3),
                to=now(),
                interval=CandleInterval.CANDLE_INTERVAL_HOUR
            )
            data_frame = create_df(response.candles)
            # https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.ema_indicator
            data_frame['ema'] = ema_indicator(close=data_frame['close'], window=9)

            return data_frame[['time', 'open', 'close', 'high', 'low', 'ema']].tail(30)
    except RequestError as e:
        print(str(e))


def get_rate_usd():
    data = run().iloc[-1]
    max_rate = max(data.open, data.close, data.high, data.low)
    max_rate_with_ema = round(max(max_rate, data.ema), 2)
    date = data.time

    dt_Moscow = date.astimezone(pytz.timezone('Europe/Moscow')).strftime('%H:%M  %d/%m/%Y')
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
    print(get_rate_usd())
