import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
import matplotlib
matplotlib.rcParams['axes.unicode_minus']=False

ts.set_token("97cb1de3f2e916ed4b7dd74d29b94997d6d7589f124a668ffcaadc21")
pro = ts.pro_api()


def z_score(ticker, startdate, enddate):
    df = pro.daily(ts_code=ticker,
                   start_date=startdate,
                   end_date=enddate)
    df_index = pd.to_datetime(df["trade_date"])
    df_index = df.sort_index()
    df_close = df[["close"]]
    df["zscore"] = (df_close - df_close.rolling(14).mean()) / df_close.rolling(14).std()
    df.dropna(inplace=True)
    return df


def Zscore_Strategy(ticker, startdate, enddate, buy_threshold= -1.5, sell_threshold= 1.5, cost=0):
    df = z_score(ticker, startdate, enddate)
    df.loc[(df.zscore < buy_threshold) & (
            df["open"] < df["close"].shift(1) * 1.097), "signal"] = 1  # 当Zscore值小于-1.5且第二天开盘没有涨停发出买入信号设置为1
    df.loc[(df.zscore > sell_threshold) & (
            df["open"] > df["close"].shift(1) * 0.903), "signal"] = 0  # 当Zscore值大于1.5且第二天开盘没有跌停发出卖入信号设置为0
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


zgyh_ZS = Zscore_Strategy("601988.SH", "20170101", "20211231")
plt.figure(figsize=(12, 6))
plt.plot(zgyh_ZS['max_drawndown'])
plt.title('最大回撤率（30天）', loc='center', fontsize=16)
plt.show()
