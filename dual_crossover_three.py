"""

When price is too far from moving average trade in opposite direction.
wait for confirmation in lower time frame?
Trend following?

"""
import json
from datetime import datetime
from yahoo_fin.stock_info import get_data, get_live_price
import mail


balance = 100
spread = 0.002


def store_data(ticker, data):
    with open("test/" + ticker + "-month.json", 'w') as file:
        for line in data:
            # print(line)
            file.write(json.dumps(line))
            if line != len(data) - 1:
                file.write("\n")
        file.close()


def load_data(ticker):
    data = []
    with open("test/" + ticker + "-month-February-Daily.json", 'r') as file:  # "test/" + ticker + "-month.json", 'r'
        for line in file:
            data.append(json.loads(line))
        file.close()
    return data


def get_minutes(ticker, start, end):
    x = get_data(ticker, start_date=start, end_date=end, interval="1m")
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


def get_timeframe(period, minutes):
    timeframe = []

    count = 1
    high = None
    low = None
    close = None
    open = None
    for i in range(len(minutes)):

        # this simple code will take the last minute and make it act as a full hour
        """
        if i == len(minutes):
            count = 60
        """

        open = minutes[i]["open"] if count == 1 else open
        close = minutes[i]["close"] if count == period else close
        if not high:
            high = minutes[i]["high"]
        else:
            high = minutes[i]["high"] if minutes[i]["high"] > high else high
        if not low:
            low = minutes[i]["low"]
        else:
            low = minutes[i]["low"] if minutes[i]["low"] < low else low

        if count == period:
            timeframe.append(
                {
                    "open": open,
                    "high": high,
                    "low": low,
                    "close": close
                }
            )
            high = None
            low = None
            close = None
            open = None
            count = 1
        else:
            count = count + 1
    return timeframe


def get_sma(minutes, period):
    index = len(minutes) - period
    if index < 0:
        return None
    sum = 0
    for i in range(period):
        close = minutes[index + i]["close"]
        sum = sum + close
    average = sum / period
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


def send_message(ticker, type, target, stop):
    address = ['stockalertsj@gmail.com']
    subject = ticker + " " + datetime.now().strftime("%H:%M") + " " + type + " TARGET " + str(round(target, 2)) \
              + " STOP " + str(round(stop, 2))  # :%S
    content = type
    print(subject)
    mail.send(address, subject, content)


def fuse_arrays(arrays):
    new_array = []
    for array in arrays:
        for item in array:
            new_array.append(item)
    return new_array


def get_up_take_profit(reward, open_price, candle):
    high = candle["high"]
    open = candle["open"]
    low = candle["low"]
    close = candle["close"]
    target = (1 + reward) * open_price
    if high >= target:
        return target
    return 0


def get_up_stop_loss(risk, open, candle):
    if candle["low"] <= (1 - risk) * open:
        return (1 - risk) * open
    return 0


def get_down_take_profit(reward, open_price, candle):
    low = candle["low"]
    target = (1 - reward) * open_price
    if low <= target:
        return target
    return 0


def get_down_stop_loss(risk, open, candle):
    if candle["high"] >= (1 + risk) * open:
        return (1 + risk) * open
    return 0


def get_crossover(i, timeframe, sma_fast, sma_slow):
    if i < sma_slow:
        return 0
    sma_slow_now = get_sma(timeframe[:i + 1], sma_slow)
    sma_slow_past = get_sma(timeframe[:i], sma_slow)
    sma_fast_now = get_sma(timeframe[:i + 1], sma_fast)
    sma_fast_past = get_sma(timeframe[:i], sma_fast)

    verdict_now = 1 if sma_fast_now > sma_slow_now else 0
    verdict_past = 1 if sma_fast_past > sma_slow_past else 0
    indication = verdict_now - verdict_past
    return indication


def get_confirmation(i, timeframe, sma_fast, sma_slow):
    if i < sma_slow:
        return 0
    fast = get_sma(timeframe[:i + 1], sma_fast)
    slow = get_sma(timeframe[:i + 1], sma_slow)
    if fast > slow:
        return 1
    if slow > fast:
        return -1
    return 0


def long_condition(i, timeframe, sma_fast, sma_slow):
    crossover = get_crossover(i, timeframe, sma_fast, sma_slow)
    if crossover == 1:
        # print("CROSS UP")
        return True
    return False


def long_condition_entry(i, timeframe, sma_fast, sma_slow, f, s):
    crossover = get_crossover(i, timeframe, sma_fast, sma_slow)
    confirmation = get_confirmation(i, timeframe, f, s)
    if crossover == 1 and confirmation == 1:
        # print("CROSS UP")
        return True
    return False


def short_condition(i, timeframe, sma_fast, sma_slow):
    crossover = get_crossover(i, timeframe, sma_fast, sma_slow)
    if crossover == -1:  #
        # print("CROSS DOWN")
        return True
    return False


def short_condition_entry(i, timeframe, sma_fast, sma_slow, f, s):
    crossover = get_crossover(i, timeframe, sma_fast, sma_slow)
    confirmation = get_confirmation(i, timeframe, f, s)
    if crossover == -1 and confirmation == -1:  #
        # print("CROSS DOWN")
        return True
    return False


def test(timeframe, sma_fast, sma_slow, f, s, balance, spread):
    status = False
    type = None
    open_price = None
    wins = 0
    loses = 0

    candle_count = 0

    for i in range(len(timeframe)):
        if status and open_price is None:
            open_price = timeframe[i]["open"]

        if status:

            if type == "up":
                short = short_condition(i, timeframe, sma_fast, sma_slow)
                if short:
                    balance_before = balance
                    price = timeframe[i]["close"]
                    balance = balance * ((price / open_price) - spread)
                    # print(candle_count)
                    if balance >= balance_before:
                        wins = wins + 1
                    else:
                        loses = loses + 1
                    status = False
                    type = None
                    candle_count = 0
                    open_price = None

            if type == "down":
                long = long_condition(i, timeframe, sma_fast, sma_slow)

                if long:
                    balance_before = balance
                    price = timeframe[i]["close"]
                    # print(candle_count)
                    balance = balance * ((open_price / price) - spread)
                    if balance >= balance_before:
                        wins = wins + 1
                    else:
                        loses = loses + 1
                    status = False
                    type = None
                    candle_count = 0
                    open_price = None
            candle_count = candle_count + 1

        if status is False:
            long = long_condition_entry(i, timeframe, sma_fast, sma_slow, f, s)
            # long = None
            short = short_condition_entry(i, timeframe, sma_fast, sma_slow, f, s)
            # short = None
            if long:
                status = True
                type = "up"
                # print(get_prevailing_trend(i, minutes, 0))
            if short:
                status = True
                type = "down"
                # print(get_prevailing_trend(i, minutes, 0))
    return balance


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


def calculate_all_volatility(tickers):
    for ticker in tickers:
        print(ticker)
        minutes = load_data(ticker)
        vol = get_average_volatility_percentage(minutes)
        print(vol)
        print("------------------")


if __name__ == "__main__":
    balance = 100
    spread = 0.002  # 50/200/1  30/100/1  # 26/200/1 how to remove some bad trades?
    sma_fast = 50
    sma_slow = 100
    time = 1
    f = sma_fast
    s = sma_slow

    tickers = ["NIO", "VIR", "VRTX", "CRSP", "TSLA", "NVDA", "PYPL", "AAPL", "AMZN", "BABA", "GOOG", "MSFT", "NFLX"]
    # tickers = ["CRSP", "PYPL", "NFLX", "NIO", "GILD", "SPPI", "PROG", "CLVS", "MRSN",  # "FB",
               # "VNDA", "OPK"]
    tickers = ["TSLA"]
    # correlation with other metrics? average volume, vol at crosses, volatility, momentum
    #

    results = []
    for ticker in tickers:
        print(ticker)
        minutes = load_data(ticker)
        minutes = get_timeframe(time, minutes)
        result = test(minutes, sma_fast, sma_slow, f, s, balance, spread)
        results.append(result)
        print(result)

    total = 0
    count = 0
    for x in results:
        total = total + x
        count = count + 1

    average = total / count if count > 0 else 0
    print("----------------")
    print(average)
    print("----------------")
    # get info on total trades, percent profitable, average profitability etc.
    # 3 crosses strategy? try 3/12 confirmation on entries.


"""
if __name__ == "__main__":
    balance = 100
    spread = 0.002
    # sma_fast = 74
    # sma_slow = 200
    time = 1

    tickers = ["TSLA"]  # , "NVDA", "PYPL", "AAPL", "AMZN", "BABA", "FB", "GOOG", "MSFT", "NFLX"]

    # biggest_average = 0
    biggest_result = 0
    sma_slow_best = 0
    sma_fast_best = 0

    cycle = 0

    for sma_slow in range(1, 201):
        for sma_fast in range(1, sma_slow):

            results = []
            for ticker in tickers:
                # print(ticker)
                # print(cycle)
                minutes = load_data(ticker)
                minutes = get_timeframe(time, minutes)
                result = test(minutes, sma_fast, sma_slow, balance, spread)
                results.append(result)
                # print("Balance: " + str(result))
                # print("----------------------------------------------------")

            total = 0
            count = 0
            for x in results:
                number = x - 100
                total = total + number
                count = count + 1
            # average = total / count if count > 0 else 0

            if total > 0:
                print(total)
                print(sma_fast)
                print(sma_slow)
                print("------------------------")

            cycle = cycle + 1
            
            
3 day above 10 day go long only, 3 day below 10 day, go short only?
in any case, its obvious that going long in uptrends will work better. 
how to determine trend overall? recent rend sma to use for day timeframe. 

consider not shorting when price is under 50 ema on day time frame. 
maybe a better time would be better to judge when price has fallen too far, like 60. 
when it dips under 50 it usually goes up, so going long would make sense. 
only because of the fall in january does not going long because of the under 50 make sense. 
look at the recent trend before deciding to enter. market is falling like fuck so short only. 



"""
