from yahoo_fin.stock_info import get_data
from trade_stat_logger.logger import SimpleLogger

def compute_performance_MA(ticker, ndays_momentum, ndays_resistance, start_date, end_date, bandwidth=1.05, threshold_ratio=1.3):
    logger = SimpleLogger()
    if ndays_momentum > ndays_resistance:
        raise ValueError('momentum should be short term, thus fewer days')
    df = get_data(ticker=ticker, start_date=start_date, end_date=end_date)
    df = df['open']
    daily_df = df[ndays_resistance:]
    # removes NaNs and aligns the two moving averages and the daily
    moving_average_momentum = df.rolling(window=ndays_momentum).mean()
    moving_average_momentum = moving_average_momentum[ndays_resistance:]
    moving_average_resistance = df.rolling(window=ndays_resistance).mean()
    moving_average_resistance = moving_average_resistance[ndays_resistance:]

    prev_below_resistance = False
    for x in range(len(moving_average_momentum)):
        momentum = moving_average_momentum.iloc[x]
        resistance = moving_average_resistance.iloc[x]
        shares, _ = logger.get_position(ticker)
        # buy into momentum
        if (momentum * bandwidth > resistance) and prev_below_resistance and shares < 100:
            logger.log(security=ticker, shares=100, share_price=daily_df.iloc[x])
            prev_below_resistance = False
        # sell once momentum hits threshold
        elif momentum * threshold_ratio > resistance and shares > 0:
            logger.log(security=ticker, shares=-100, share_price=daily_df.iloc[x])
            prev_below_resistance = False
        # "stop loss", or sell if momentum goes against us
        elif momentum < resistance:
            logger.log(security=ticker, shares=-100, share_price=daily_df.iloc[x])
            prev_below_resistance = True
    return logger

logger_10_100 = compute_performance_MA(ticker='AAPL', ndays_momentum=10, ndays_resistance=100, start_date='01/01/2017', end_date='01/01/2019')
print(logger_10_100.get_summary_statistics())
logger_10_100.graph_statistics()
