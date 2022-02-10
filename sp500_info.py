import csv

from yahoo_fin.stock_info import get_live_price, get_next_earnings_date, \
    get_data, get_quote_data, get_stats, \
    get_day_gainers, get_day_losers, get_day_most_active, \
    get_market_status, get_premarket_price, get_postmarket_price, \
    tickers_sp500, tickers_nasdaq

if __name__ == "__main__":
    with open('sp500.csv', 'w', encoding="UTF8") as file:
        writer = csv.writer(file)
    # print(len(tickers_nasdaq()))
    # print(len(tickers_sp500()))
        for ticker in tickers_sp500():
            print(ticker)
            date = "null"
            try:
                date = str(get_next_earnings_date(ticker))
            except:
                print("NO DATE FOUND")
            writer.writerow(ticker + "" + date)
    # print(get_day_gainers())
    #print(get_next_earnings_date("TSLA"))
    # print(get_live_price("MSFT"))
    # print(get_data("MSFT")) # year-month-day open high low adjclose volume ticker
    # print(get_quote_data("MSFT"))  # longName, shortName, fiftyTwoWeekLow, fiftyTwoWeekHigh, fiftyDayAverage, \
    # fiftyDayAverageChange, twoHundredDayAverage, displayName, symbol, regularMarketVolume, \
    # regularMarketPreviousClose, bid, ask,
    # print(get_stats("MSFT"))  # 50-Day Moving Average, 200-Day Moving Average