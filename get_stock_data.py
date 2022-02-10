# get all stocks
# get most volatile stocks
# long only strategy? always in strategy?
# diversification effects long term?
# set and forget

import time
import json
from datetime import date, datetime

from numpy import nan
from yahoo_fin.stock_info import get_data, get_live_price
import mail
import os


def get_minutes(ticker, start, end):
    x = get_data(ticker, start_date=start, end_date=end, interval="1d")
    print(x)
    minutes = []
    for i in range(x.shape[0]):
        data = \
            {
                "open": x.iloc[i][0],  # ohlcv
                "high": x.iloc[i][1],
                "low": x.iloc[i][2],
                "close": x.iloc[i][3],
                "volume": x.iloc[i][4]
            }
        minutes.append(data)
    minutes = minutes[:-2]
    minutes = remove_junk(minutes)
    return minutes


def remove_junk(minutes):
    new_minutes = []
    for i in range(len(minutes)):
        if is_unique_minute(minutes[i]) and is_valid_minute(minutes[i]):
            new_minutes.append(minutes[i])
    return new_minutes


def is_unique_minute(minute):
    if minute["open"] == minute["close"] and minute["open"] == minute["high"] and minute["open"] == minute["low"]:
        return False
    return True


def is_valid_minute(minute):
    if not float(minute["open"]) > 0:
        return False
    return True


def fuse_arrays(one, two):
    data = []
    for item in one:
        data.append(item)
    for item in two:
        data.append(item)
    return data


def store_data(ticker, data):
    with open("test/" + ticker + "-month-February-Daily.json", 'w') as file:
        for line in data:
            # print(line)
            file.write(json.dumps(line))
            if line != len(data) - 1:
                file.write("\n")
        file.close()


def load_data(ticker):
    data = []
    with open("test/" + ticker + "-month-January.json", 'r') as file:
        for line in file:
            data.append(json.loads(line))
        file.close()
    return data


def get_tickers():
    return ["VIR", "VRTX", "CRSP", "TSLA", "NVDA", "PYPL", "AAPL", "AMZN", "BABA", "FB", "GOOG", "MSFT", "NFLX",
            "NIO"]


def get_weeks():
    weeks = [{"start": "01/10/2022", "stop": "01/14/2022"}, {"start": "01/17/2022", "stop": "01/21/2022"},
             {"start": "01/24/2022", "stop": "01/28/2022"}, {"start": "31/1/2022", "stop": "02/4/2022"}]
    return weeks


def get_average_volatility_percentage(candles):
    sum = 0
    count = 0
    for i in range(len(candles)):
        open = candles[i]["open"]
        high = candles[i]["high"]
        low = candles[i]["low"]
        close = candles[i]["close"]

        if close > open:
            percentage = ((close / open) * 100) - 100
            sum = sum + percentage
            count = count + 1
        if open > close:
            percentage = ((open / close) * 100) - 100
            sum = sum + percentage
            count = count + 1

    average = sum / count
    return average


def calculate_all_volatility():
    tickers = get_tickers()
    for ticker in tickers:
        print(ticker)
        minutes = load_data(ticker)
        vol = get_average_volatility_percentage(minutes)
        print(vol)
        print("------------------")


if __name__ == "__main__":
    # calculate_all_volatility()
    # breakpoint()
    tickers = get_tickers()
    for ticker in tickers:
        weeks = get_weeks()
        minutes = get_minutes(ticker, "01/01/2020", "02/07/2022")
        """
        minutes = []
        for week in weeks:
            print(week)
            new = get_minutes(ticker, week["start"], week["stop"])
            minutes = fuse_arrays(minutes, new)
        """
        print(minutes)
        store_data(ticker, minutes)

# https://www.suredividend.com/technology-stocks-list/
# https://www.investopedia.com/articles/stocks/11/dividend-capture-strategy.asp
# https://markets.businessinsider.com/index/components/nasdaq_100?op=1


