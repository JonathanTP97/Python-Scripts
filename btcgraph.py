import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import time
import datetime

symbol = 'BTCUSDT'
starttime = '100 minutes ago UTC'  # 1 week ago UTC
interval = '1m'


def plot_graph(df):
    df = df.astype(float)
    df[['close', '12sma']].plot()  # , '26sma'
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Close Price', fontsize=18)
    # plt.scatter(df.index, df['buy'], color='green', label='Buy', marker='>', alpha=1)  # green = buy
    # plt.scatter(df.index, df['sell'], color='red', label='Sell', marker='<', alpha=1)  # red = sell
    plt.show()


def get_data():
    bars = client.get_historical_klines(symbol, interval, starttime)

    for line in bars:
        del line[5:]

    # 2d tabular data
    symbol_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])

    symbol_df['12sma'] = symbol_df['close'].rolling(12).mean()
    # symbol_df['26sma'] = symbol_df['close'].rolling(26).mean()
    symbol_df['signal'] = np.where(float(client.get_symbol_ticker(symbol=symbol)['price']) > symbol_df['12sma'], 1, 0)
    symbol_df['position'] = symbol_df['signal'].diff()  # difference from previous row 1, 0 -1
    # symbol_df['buy'] = np.where(symbol_df['position'] == 1, symbol_df['close'], np.NaN)
    # symbol_df['sell'] = np.where(symbol_df['position'] == -1, symbol_df['close'], np.NaN)

    symbol_df.set_index('date', inplace=True)
    symbol_df.index = pd.to_datetime(symbol_df.index, unit='ms')
    return symbol_df


if __name__ == "__main__":
    api_key = os.environ.get('binance_api')
    api_secret = os.environ.get('binance_secret')
    client = Client(api_key, api_secret)

    while True:
        symbol_df = get_data()
        plot_graph(symbol_df)
