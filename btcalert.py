import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import time
import datetime


symbol = 'BTCUSDT'
starttime = '12 minutes ago UTC'  # 1 week ago UTC
interval = '1m'
now = datetime.datetime.now()


def clear():
    os.system('cls')


def color(color):
    if color == "green":
        os.system('cmd /c "color 2f"')
    if color == "red":
        os.system('cmd /c "color 2f"')
    if color == "black":
        os.system('cmd /c "color 3f"')


def get_latest_position():
    bars = client.get_historical_klines(symbol, interval, starttime)

    for line in bars:
        del line[5:]

    # 2d tabular data
    symbol_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
    number_of_bars = symbol_df.shape[0]

    symbol_df['12sma'] = symbol_df['close'].rolling(12).mean()
    symbol_df['signal'] = np.where(float(symbol_df['close'][number_of_bars - 1]) > float(symbol_df['12sma'][number_of_bars - 1]), 1, 0)
    symbol_df['position'] = symbol_df['signal'].diff()  # difference from previous row 1, 0 -1

    return float(symbol_df['position'][number_of_bars - 1])  # i.e. 12th bar is index 11


def check_for_entries():
    try:
        while True:
            latest_position = get_latest_position()
            if latest_position == 1:
                clear()
                color("green")
                print("buy buy buy!")  # color 2f
                print(now.strftime('%H:%M'))
            elif latest_position == -1:
                clear()
                color("red")
                print("sell sell sell!")  # color 4f
                print(now.strftime('%H:%M'))
            else:
                clear()
                color("black")
                print("nothing to do...")  # color
                print(now.strftime('%H:%M'))
            time.sleep(3)
    except BinanceAPIException as e:
        print(e)
    except BinanceOrderException as e:
        print(e)


if __name__ == "__main__":
    api_key = os.environ.get('binance_api')
    api_secret = os.environ.get('binance_secret')
    client = Client(api_key, api_secret)

    check_for_entries()



