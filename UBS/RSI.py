import pandas as pd
import tushare as ts
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
import matplotlib
matplotlib.rcParams['axes.unicode_minus']=False

ts.set_token("97cb1de3f2e916ed4b7dd74d29b94997d6d7589f124a668ffcaadc21")
pro = ts.pro_api()


def RSI(price, period):
    clprcChange = price - price.shift(1)
    clprcChange = clprcChange.dropna()

    indexprc = clprcChange.index
    upPrc = pd.Series(0, index=indexprc)
    upPrc[clprcChange > 0] = clprcChange[clprcChange > 0]

    downPrc = pd.Series(0, index=indexprc)
    downPrc[clprcChange < 0] = -clprcChange[clprcChange < 0]
    risdata = pd.concat([price, clprcChange, upPrc, downPrc], axis=1)
    risdata.columns = ['price', 'PrcChange', 'upPrc', 'downPrc']
    risdata = risdata.dropna()

    SMUP = []
    SMDOWN = []
    for i in range(period, len(upPrc) + 1):
        SMUP.append(np.mean(upPrc.values[(i - period): i], dtype=np.float32))
        SMDOWN.append(np.mean(downPrc.values[(i - period): i], dtype=np.float32))
        rsi = [100 * SMUP[i] / (SMUP[i] + SMDOWN[i]) for i in range(0, len(SMUP))]

    indexRsi = indexprc[(period - 1):]
    rsi = pd.Series(rsi, index=indexRsi)
    rsi.dropna(inplace=True)
    return rsi


def RSI_Strategy(ticker, startdate, enddate, cost=0):
    df = pro.daily(ts_code=ticker,
                   start_date=startdate,
                   end_date=enddate)
    df_index = pd.to_datetime(df["trade_date"])
    df_index = df.sort_index()

    df["RSI_6"] = RSI(df["close"], 6)
    df["RSI_24"] = RSI(df["close"], 24)

    # 买卖信号
    # 6日的超买和超卖
    sig1 = []
    for i in df.RSI_6:
        if i > 80:
            sig1.append(1)
        elif i < 20:
            sig1.append(-1)
        else:
            sig1.append(0)
    df['sig1'] = sig1

    # 交易信号2：金叉与死叉
    sig2 = pd.Series(0, index=df.index)
    lagrsi6 = df.RSI_6.shift(1)
    lagrsi24 = df.RSI_24.shift(1)
    for i in range(0, len(lagrsi6)):
        if (df.RSI_6[i] > df.RSI_24[i]) & (lagrsi6[i] < lagrsi24[i]):
            sig2[i] = 1
        elif (df.RSI_6[i] < df.RSI_24[i]) & (lagrsi6[i] > lagrsi24[i]):
            sig2[i] = -1

    df['sig2'] = sig2

    signal = sig1 + sig2
    signal[signal >= 1] = 1
    signal[signal <= -1] = -1
    signal = signal.dropna()
    df['signal'] = signal
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


zgyh_RSI = RSI_Strategy("601988.SH", "20170101", "20211231")
plt.figure(figsize=(12, 6))
plt.plot(zgyh_RSI['position'])
plt.title('持仓', loc='center', fontsize=16)
plt.show()
