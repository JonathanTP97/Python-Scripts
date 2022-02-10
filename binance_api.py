import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client

symbol = 'BTCUSDT'

# get btc 12 day sma. when price moves above it, place order, set the tp and step loss appropriately.
# also trade eth if no opportunities available.
# get results of trades in terms of profit or loss percentage etc.
# read current account balance.


def get_dataframe():    # valid intervals-1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

    starttime = '30 minutes ago UTC'  # 1 week ago UTC
    interval = '1m'

    bars = client.get_historical_klines(symbol, interval, starttime)

    for line in bars:
        del line[5:]
    # 2d tabular data
    df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
    return df


def sma_trade_logic():
    symbol_df = get_dataframe()
    symbol_df['12sma'] = symbol_df['close'].rolling(12).mean()
    symbol_df['26sma'] = symbol_df['close'].rolling(26).mean()
    symbol_df['signal'] = np.where(symbol_df['12sma'] > symbol_df['26sma'], 1, 0)

    symbol_df.set_index('date', inplace=True)
    symbol_df.index = pd.to_datetime(symbol_df.index, unit='ms')

    with open('output.txt', 'w') as f:
        f.write(symbol_df.to_string())

    symbol_df['position'] = symbol_df['signal'].diff()  # difference from previous row
    symbol_df['buy'] = np.where(symbol_df['position'] == 1, symbol_df['close'], np.NaN)
    symbol_df['sell'] = np.where(symbol_df['position'] == -1, symbol_df['close'], np.NaN)

    plot_graph(symbol_df)

    buy_sell_list = symbol_df['position'].tolist()
    # buy_or_sell(buy_sell_list, symbol_df)


def plot_graph(df):
    df = df.astype(float)
    df[['close', '12sma', '26sma']].plot()
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Close Price', fontsize=18)
    plt.scatter(df.index, df['buy'], color='green', label='Buy', marker='>', alpha=1)  # green = buy
    plt.scatter(df.index, df['sell'], color='red', label='Sell', marker='<', alpha=1)  # red = sell
    plt.show()


def buy_or_sell(buy_sell_list, df):
    for index, value in enumerate(buy_sell_list):
        current_price = client.get_symbol_ticker(symbol=symbol)
        print(current_price['price'])

        if value == 1.0:  # signal to buy
            print(df['buy'][index])
            if current_price['price'] < df['buy'][index]:
                print("buy buy buy...")
                buy_order = client.order_market_buy(symbol=symbol, quantity=2)
                print(buy_order)

        elif value == -1.0:  # signal to sell
            if current_price['price'] > df["sell"][index]:
                print("sell sell sell...")
                sell_order = client.order_market_sell(symbol=symbol, quantity=10)
                print(sell_order)
        else:
            print("nothing to do...")


def main():
    sma_trade_logic()


if __name__ == "__main__":
    api_key = os.environ.get('binance_api')
    api_secret = os.environ.get('binance_secret')
    client = Client(api_key, api_secret)
    btc_price_now = client.get_symbol_ticker(symbol="BTCUSDT")["price"]
    print(btc_price_now)
    main()

"""
# client.API_URL = 'https://testnet.binance.vision/api'

# get balances for all assets & some account information
print(client.get_account())

# get balance for a specific asset only (BTC)
print(client.get_asset_balance(asset='BTC'))

# get balances for futures account
print(client.futures_account_balance())

# get balances for margin account
print(client.get_margin_account())

# get latest price from Binance API
btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
# print full output (dictionary)
print(btc_price)

# {'symbol': 'BTCUSDT', 'price': '9678.08000000'}
print(btc_price["price"])





# init and start the WebSocket
bsm = ThreadedWebsocketManager()
bsm.start()

# subscribe to a stream
bsm.start_symbol_ticker_socket(callback=btc_trade_history, symbol='BTCUSDT')
bsm.start_symbol_ticker_socket(callback=btc_trade_history, symbol='ETHUSDT')

# stop websocket
bsm.stop()

# valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

# get timestamp of earliest date data is available
timestamp = client._get_earliest_valid_timestamp('BTCUSDT', '1d')
print(timestamp)

# request historical candle (or klines) data
bars = client.get_historical_klines('BTCUSDT', '1d', timestamp, limit=1000)

"""
