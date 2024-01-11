import pandas as pd
import tushare as ts
import numpy as np

ts.set_token("97cb1de3f2e916ed4b7dd74d29b94997d6d7589f124a668ffcaadc21")
pro = ts.pro_api()


def KDJ(ticker, startdate, enddate):
    df = pro.daily(ts_code=ticker,
                   start_date=startdate,
                   end_date=enddate)
    df_index = pd.to_datetime(df["trade_date"])
    df_index = df.sort_index()
    low_list = df['low'].rolling(9, min_periods=9).min()
    low_list.fillna(value=df['low'].expanding().min(), inplace=True)
    high_list = df['high'].rolling(9, min_periods=9).max()
    high_list.fillna(value=df['high'].expanding().max(), inplace=True)
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    df['K'] = pd.DataFrame(rsv).ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    df.dropna(inplace=True)
    return df


def KDJ_Strategy(ticker, startdate, enddate, cost=0):
    df = KDJ(ticker, startdate, enddate)
    KSignal = df['K'].apply(lambda x: -1 if x > 85 else 1 if x < 20 else 0)
    DSignal = df['D'].apply(lambda x: -1 if x > 80 else 1 if x < 20 else 0)
    JSignal = df['J'].apply(lambda x: -1 if x > 100 else 1 if x < 0 else 0)
    df["KDJSignal"] = KSignal + DSignal + JSignal
    df.loc[(df.KDJSignal >= 2) & (
            df["open"] > df["close"].shift(1) * 0.903), "signal"] = 1
    df.loc[(df.KDJSignal <= -2) & (
            df["open"] < df["close"].shift(1) * 1.097), "signal"] = 0
    df.dropna(inplace=True)
    df["position"] = df["signal"].shift(1)  # 每日持仓数量
    df["position"].fillna(method="ffill", inplace=True)
    df["position"].fillna(df["position"].shift(1), inplace=True)
    df["market_dis"] = df["close"].pct_change(1)
    df.loc[df.index[0], 'capital_ret'] = 0
    # 今天开盘新买入的position在今天的涨幅(扣除手续费)
    df.loc[df['position'] > df['position'].shift(1), 'capital_ret'] = \
        (df['close'] / df['open'] - 1) * (1 - cost)
    # 卖出同理
    df.loc[df['position'] < df['position'].shift(1), 'capital_ret'] = \
        (df['open'] / df['close'].shift(1) - 1) * (1 - cost)
    # 当仓位不变时,当天的capital是当天的change * position
    df.loc[df['position'] == df['position'].shift(1), 'capital_ret'] = \
        df['market_dis'] * df['position']
    df['capital_line'] = (df.capital_ret + 1.0).cumprod()
    df['rolling_max'] = df['capital_line'].rolling(30, min_periods=1).max()
    df['daily_drawndown'] = df['capital_line'] / df['rolling_max'] - 1
    df['max_drawndown'] = df['daily_drawndown'].rolling(30, min_periods=1).min()
    return df


zgyh_KDJ = KDJ_Strategy("601988.SH", "20170101", "20211231")
print(sum(zgyh_KDJ['close'])/len(zgyh_KDJ['close']))
print(max(zgyh_KDJ['close']))
print(min(zgyh_KDJ['close']))
print(np.var(zgyh_KDJ['close']))
print(np.quantile(zgyh_KDJ['close'],.75))
print(np.quantile(zgyh_KDJ['close'],.25))