
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import time.sleep

symbol = 'BTCUSDT'
starttime = '12 minutes ago UTC'  # 1 week ago UTC
interval = '1m'


def get_latest_position():
    bars = client.get_historical_klines(symbol, interval, starttime)

    for line in bars:
        del line[5:]

    # 2d tabular data
    symbol_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])

    symbol_df['12sma'] = symbol_df['close'].rolling(12).mean()
    symbol_df['signal'] = np.where(float(current_price) > symbol_df['12sma'], 1, 0)
    symbol_df['position'] = symbol_df['signal'].diff()  # difference from previous row 1, 0 -1
    number_of_bars = symbol_df.shape[0]
    return symbol_df['position'][number_of_bars - 1]  # i.e. 12th bar is index 11


def monitor_long():
    while client.get_open_orders(symbol=symbol)[0]['orderId'] > 0:
        orderId = client.get_open_orders(symbol=symbol)[0]['orderId']
        price_now = client.get_symbol_ticker(symbol=symbol)['price']
        # check price and quantity of original order
        # if price has moved up a certain amount then move the sl to a new place.
        if 5>3:  # if price has moved up, set a new stop loss
            client.cancel_order(symbol=symbol, orderId=orderId)
            client.create_oco_order()
    print("NO CURRENT ORDER")


def go_long():
    # return 1 success, return 0 sale, check for position to close,
    print("Going long")
    order_buy = client.create_oco_order(
        symbol=symbol,
        side="BUY",
        timeInForce=,
        quantity=1,
        price=0.0
    )
    order_buy_id = order_buy['orderId']
    # print("Order ID is " + str(order_buy_id))
    # orders = client.get_open_orders(symbol=symbol)
    # orderId = orders[0]['orderId']
    # if orderId > 0:
    client.cancel_order(symbol=symbol, orderId=order_buy_id)
    client.create_oco_order(

    )
    # cancel order if price has moved up and place a new one with better stop loss
    # place new order?

    pass


def go_short():
    print("Going short!")  # exact opposite of going long code.
    pass


def check_for_entries():
    try:
        while True:
            latest_position = get_latest_position()
            if latest_position == 1:
                print("buy buy buy!")
                go_long()
            elif latest_position == -1:
                print("sell sell sell!")
                go_short()
            else:
                print("nothing to do...")
            time.sleep(1)  # how often should i check for new info? too long and could miss kline action
    except BinanceAPIException as e:
        print(e)
    except BinanceOrderException as e:
        print(e)


if __name__ == "__main__":
    api_key = os.environ.get('binance_api')
    api_secret = os.environ.get('binance_secret')
    client = Client(api_key, api_secret)

    check_for_entries()



