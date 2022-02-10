import time
import json
from datetime import date, datetime

from numpy import nan
from yahoo_fin.stock_info import get_data, get_live_price
import mail
import os

"""
Get all minutes for a stock for a year
Then set up account balance, spreads, and simulate opening buys and shorts, collecting data
"""

start = 100
balance = start
spread = 0.02  # 2%

total_buys = 0
total_buy_winners = 0
total_buy_losers = total_buys - total_buy_winners

total_sells = 0
total_sell_winners = 0
total_sell_losers = total_sells - total_sell_winners

total_trades = total_buys + total_sells
total_winners = total_buy_winners + total_sell_winners
total_losers = total_buy_losers + total_sell_losers


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


def store_data(data):
    with open("data/" + ticker + "-2021.json", 'w') as file:
        for line in range(len(data)):
            file.write(json.dumps(data[line]))
            if line != len(data)-1:
                file.write("\n")
        file.close()


def get_minutes(ticker, start, end):
    x = get_data(ticker, start_date=start, end_date=end, interval="1m")
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


def get_weeks():
    weeks = [{"start": "01/01/2021", "stop": "01/01/2021"}, {"start": "01/04/2021", "stop": "01/08/2021"},
             {"start": "01/11/2021", "stop": "01/15/2021"}, {"start": "01/18/2021", "stop": "01/22/2021"},
             {"start": "01/25/2021", "stop": "01/29/2021"}, {"start": "02/01/2021", "stop": "02/05/2021"},
             {"start": "02/08/2021", "stop": "02/12/2021"}, {"start": "02/15/2021", "stop": "02/19/2021"},
             {"start": "02/22/2021", "stop": "02/26/2021"}, {"start": "03/01/2021", "stop": "03/05/2021"},
             {"start": "03/08/2021", "stop": "03/12/2021"}, {"start": "03/25/2021", "stop": "03/19/2021"},
             {"start": "03/22/2021", "stop": "03/26/2021"}, {"start": "03/29/2021", "stop": "04/02/2021"},
             {"start": "04/05/2021", "stop": "04/09/2021"}, {"start": "04/12/2021", "stop": "04/16/2021"},
             {"start": "04/19/2021", "stop": "04/23/2021"}, {"start": "04/26/2021", "stop": "04/30/2021"},
             {"start": "05/03/2021", "stop": "05/07/2021"}, {"start": "05/10/2021", "stop": "05/14/2021"},
             {"start": "05/17/2021", "stop": "05/21/2021"}, {"start": "05/24/2021", "stop": "05/28/2021"},
             {"start": "05/31/2021", "stop": "06/04/2021"}, {"start": "06/07/2021", "stop": "06/11/2021"},
             {"start": "06/14/2021", "stop": "06/18/2021"}, {"start": "06/21/2021", "stop": "06/25/2021"},
             {"start": "06/28/2021", "stop": "07/02/2021"}, {"start": "07/05/2021", "stop": "07/09/2021"},
             {"start": "07/12/2021", "stop": "07/16/2021"}, {"start": "07/19/2021", "stop": "07/23/2021"},
             {"start": "07/26/2021", "stop": "07/30/2021"}, {"start": "08/02/2021", "stop": "08/06/2021"},
             {"start": "08/09/2021", "stop": "08/13/2021"}, {"start": "08/16/2021", "stop": "08/20/2021"},
             {"start": "08/23/2021", "stop": "08/27/2021"}, {"start": "08/30/2021", "stop": "09/03/2021"},
             {"start": "09/06/2021", "stop": "09/10/2021"}, {"start": "09/13/2021", "stop": "09/17/2021"},
             {"start": "09/20/2021", "stop": "09/24/2021"}, {"start": "09/27/2021", "stop": "10/01/2021"},
             {"start": "10/04/2021", "stop": "10/08/2021"}, {"start": "10/11/2021", "stop": "10/15/2021"},
             {"start": "10/18/2021", "stop": "10/22/2021"}, {"start": "10/25/2021", "stop": "10/29/2021"},
             {"start": "11/01/2021", "stop": "11/05/2021"}, {"start": "11/08/2021", "stop": "11/12/2021"},
             {"start": "11/15/2021", "stop": "11/19/2021"}, {"start": "11/22/2021", "stop": "11/26/2021"},
             {"start": "11/29/2021", "stop": "12/03/2021"}, {"start": "12/06/2021", "stop": "12/10/2021"},
             {"start": "12/13/2021", "stop": "12/17/2021"}, {"start": "12/20/2021", "stop": "12/24/2021"},
             {"start": "12/27/2021", "stop": "12/31/2021"}]
    return weeks


if __name__ == "__main__":
    ticker = "FB"
    weeks = get_weeks()
    minutes = []
    for week in weeks:
        print(week)
        new = get_minutes(ticker, week["start"], week["stop"])
        minutes = fuse_arrays(minutes, new)
    print(minutes)
