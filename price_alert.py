
import json
import time
from datetime import datetime
from yahoo_fin.stock_info import get_data
import mail


def store_data(ticker_, data):
    with open("test/" + ticker_ + "-month.json", 'w') as file:
        for line in data:
            # print(line)
            file.write(json.dumps(line))
            if line != len(data) - 1:
                file.write("\n")
        file.close()


def load_data(ticker_):
    data = []
    with open("test/" + ticker_ + "-month-January.json", 'r') as file:  # "test/" + ticker + "-month.json", 'r'
        for line in file:
            data.append(json.loads(line))
        file.close()
    return data


def get_minutes(ticker_, start_, end_):
    x = get_data(ticker_, start_date=start_, end_date=end_, interval="1m")
    m = []
    for i in range(x.shape[0]):
        data = \
            {
                "open": x.iloc[i][0],  # ohlcv
                "high": x.iloc[i][1],
                "low": x.iloc[i][2],
                "close": x.iloc[i][3],
                "volume": x.iloc[i][4]
            }
        m.append(data)
    m = m[:-2]
    m = remove_junk(m)
    return m


def remove_junk(data):
    new_data = []
    for i in range(len(data)):
        if is_unique_minute(data[i]) and is_valid_minute(data[i]):
            new_data.append(data[i])
    return new_data


def is_unique_minute(minute):
    if minute["open"] == minute["close"] and minute["open"] == minute["high"] and minute["open"] == minute["low"]:
        return False
    return True


def is_valid_minute(minute):
    if not float(minute["open"]) > 0:
        return False
    return True


def get_timeframe(period, data):
    timeframe = []

    count = 1
    high_ = None
    low_ = None
    close_ = None
    open_ = None
    for i in range(len(data)):

        # this simple code will take the last minute and make it act as a full hour
        """
        if i == len(minutes):
            count = 60
        """

        open_ = data[i]["open"] if count == 1 else open_
        close_ = data[i]["close"] if count == period else close_
        if not high_:
            high_ = data[i]["high"]
        else:
            high_ = data[i]["high"] if data[i]["high"] > high_ else high_
        if not low_:
            low_ = data[i]["low"]
        else:
            low_ = data[i]["low"] if data[i]["low"] < low_ else low_

        if count == period:
            timeframe.append(
                {
                    "open": open_,
                    "high": high_,
                    "low": low_,
                    "close": close_
                }
            )
            high_ = None
            low_ = None
            close_ = None
            open_ = None
            count = 1
        else:
            count = count + 1
    return timeframe


def get_sma(data, period):
    index = len(data) - period
    if index < 0:
        return None
    total = 0
    for i in range(period):
        close = data[index + i]["close"]
        total = total + close
    average = total / period
    return average


def get_ema(hours, period):
    index = len(hours) - period
    if index < 0:
        return None
    weight = float(2 / (period + 1))
    previous_ema = 0
    for i in range(period):
        close = hours[index + i]["close"]
        if i == 0:
            previous_ema = close
        else:
            previous_ema = (close * weight) + (previous_ema * (1 - weight))
    return previous_ema


def send_message(current_ticker, current_type, current_time):
    address = ['stockalertsj@gmail.com']
    subject = current_ticker + " " + current_time + " " + current_type
    content = current_ticker + " " + current_type
    mail.send(address, subject, content)
    print("MESSAGE SENT")


def fuse_arrays(arrays):
    new_array = []
    for array in arrays:
        for item in array:
            new_array.append(item)
    return new_array


# TREND
def is_up_trend(trend):
    if trend > 0:
        return True
    return False


def is_down_trend(trend):
    if trend < 0:
        return True
    return False


def get_prevailing_trend(i, timeframe, candles):
    period = 5

    on_balance_price = 0
    count = 0
    for candle in timeframe[i - (period + (candles - 1)): i - (candles - 1)]:
        if candle["open"] > candle["close"]:
            on_balance_price = on_balance_price - (candle["open"] - candle["close"])
        if candle["close"] > candle["open"]:
            on_balance_price = on_balance_price + (candle["close"] - candle["open"])
        count = count + 1
    if on_balance_price == 0:
        return 0
    obp = on_balance_price / count
    return obp


def get_crossover(timeframe, sma_fast_, sma_slow_):
    if len(timeframe) < sma_slow_:
        return 0
    sma_slow_now = get_sma(timeframe, sma_slow_)
    sma_slow_past = get_sma(timeframe[:-1], sma_slow_)
    sma_fast_now = get_sma(timeframe, sma_fast_)
    sma_fast_past = get_sma(timeframe[:-1], sma_fast_)
    verdict_now = 1 if sma_fast_now > sma_slow_now else 0
    verdict_past = 1 if sma_fast_past > sma_slow_past else 0
    indication = verdict_now - verdict_past
    return indication


def check(timeframe, sma_fast_, sma_slow_):
    crossover = get_crossover(timeframe, sma_fast_, sma_slow_)
    if crossover != 0:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if crossover == 1:
            print(ticker + " CROSS UP " + current_time)
            send_message(ticker, "CROSS UP", current_time)
        if crossover == -1:
            print(ticker + " CROSS DOWN " + current_time)
            send_message(ticker, "CROSS DOWN", current_time)


def get_average_sma_deviation(timeframe, period):
    maximum = 0
    all_ratios = 0
    count = 0
    for i in range(len(timeframe)):
        if i < period - 1:
            continue
        price = timeframe[i]["close"]
        sma = get_sma(timeframe[:i + 1], period)
        diff = price - sma
        ratio = price / sma if diff >= 0 else sma / price
        all_ratios = all_ratios + ratio
        count = count + 1
        maximum = ratio if ratio > maximum else maximum
    average = all_ratios / count
    data = {
        "average": average,
        "maximum": maximum
    }
    return data


def get_average_volatility_percentage(candles):
    total = 0
    count = 0
    for i in range(len(candles)):
        open_ = candles[i]["open"]
        close_ = candles[i]["close"]

        if close_ > open_:
            percentage = ((close_ / open_) * 100) - 100
            total = total + percentage
            count = count + 1
        if open_ > close_:
            percentage = ((open_ / close_) * 100) - 100
            total = total + percentage
            count = count + 1

    average = total / count
    return average


def calculate_all_volatility(my_tickers):
    for my_ticker in my_tickers:
        print(my_ticker)
        data = load_data(my_ticker)
        vol = get_average_volatility_percentage(data)
        print(vol)
        print("------------------")


if __name__ == "__main__":
    sma_fast = 50
    sma_slow = 200
    start = "01/27/2022"
    end = "02/02/2022"

    mail = mail.Mail()
    tickers = ["TSLA", "NVDA", "PYPL", "AAPL", "AMZN", "BABA", "FB", "GOOG", "MSFT", "NFLX", "CRSP"]

    while True:
        for ticker in tickers:
            print(ticker)
            minutes = get_minutes(ticker, start, end)
            check(minutes, sma_fast, sma_slow)
        time.sleep(30)

"""
More volatile stocks = more profit? What are most volatile stocks
Strategies. 
Different time frame exit, different time frame entry?
prevailing trend effect on success of long or short. 
ranging mix long and short?
rising use long only
falling use short only?
longer timeframe trend recent. recent days trend. 

"""