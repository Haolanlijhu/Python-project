import pandas as pd
import tushare as ts
import numpy as np
from arch.unitroot import ADF
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
import matplotlib

matplotlib.rcParams['axes.unicode_minus'] = False

ts.set_token("97cb1de3f2e916ed4b7dd74d29b94997d6d7589f124a668ffcaadc21")
pro = ts.pro_api()

tickers = ['600919.SH', '601658.SH', '601328.SH', '600926.SH', '601009.SH', '601825.SH', '601166.SH', '601528.SH',
           '601398.SH', '601187.SH', '601939.SH', '601229.SH', '601963.SH', '601665.SH', '601169.SH', '601818.SH',
           '601077.SH', '600016.SH', '601288.SH', '601988.SH', '601998.SH', '601860.SH', '601916.SH', '600036.SH',
           '601128.SH', '600015.SH', '600928.SH', '000001.SZ', '601838.SH', '601577.SH', '603323.SH', '601997.SH',
           '600908.SH', '600000.SH', '002142.SZ', '002839.SZ', '002958.SZ', '002966.SZ', '002936.SZ', '002948.SZ',
           '002807.SZ']
data_list = []
for code in tickers:
    data = pro.daily(ts_code=code, start_date='20210101', end_date='20211231')[['trade_date', 'close']]
    data.sort_values('trade_date', inplace=True)
    data.rename(columns={'close': code}, inplace=True)
    data.set_index('trade_date', inplace=True)
    data_list.append(data)
data = pd.concat(data_list, axis=1)
data = data.astype(float)
data = data.drop(['601825.SH', '601528.SH', '601963.SH', '601665.SH', '002142.SZ'], axis=1)


# 选股
def checkADF(tickerA, tickerB):
    price_A = tickerA['close'].values
    price_B = tickerB['close'].values
    result_A = adfuller(price_A)
    result_B = adfuller(price_B)
    return result_A, result_B


def checkdiff(tickerA, tickerB):
    price_A = tickerA['close'].values
    price_B = tickerB['close'].values
    price_A = np.diff(price_A)
    price_B = np.diff(price_B)
    result_A = adfuller(price_A)
    result_B = adfuller(price_B)
    return result_A, result_B


def cointegration(tickerA, tickerB):
    log_priceX = np.log(tickerA)
    log_priceY = np.log(tickerB)
    results = sm.OLS(log_priceY, sm.add_constant(log_priceX)).fit()
    resid = results.resid
    adfSpread = ADF(resid)

    if adfSpread.pvalue >= 0.05:
        print(tickerA, tickerB, '''收盘价格不具有协整关系.
            P-value of ADF test: %f
            Coefficients of regression:
            Intercept: %f
            Beta: %f
             ''' % (adfSpread.pvalue, results.params[0], results.params[1]))
        return None
    else:
        print(tickerA, tickerB, '''收盘价格具有协整关系.
            P-value of ADF test: %f
            Coefficients of regression:
            Intercept: %f
            Beta: %f
             ''' % (adfSpread.pvalue, results.params[0], results.params[1]))
        return results.params[0], results.params[1]


lst = list(data.columns)
d = dict()
for i in range(len(lst)):
    for j in range(i + 1, len(lst)):
        x = data[lst[i]]
        y = data[lst[j]]
        coin = cointegration(x, y)

# 渝农商行 与 邮储银行
ynyh = pro.daily(ts_code='601077.SH', start_date="20200101", end_date="20211231")
ynyh_index = pd.to_datetime(ynyh["trade_date"])
ynyh_index = ynyh.sort_index()

ycyh = pro.daily(ts_code='601658.SH', start_date="20200101", end_date="20211231")
ycyh_index = pd.to_datetime(ycyh["trade_date"])
ycyh_index = ycyh.sort_index()

log_ynyh = np.log(ynyh.close)
log_ycyh = np.log(ycyh.close)
model = sm.OLS(log_ycyh, sm.add_constant(log_ynyh))
result = model.fit()
alpha = result.params[0]
beta = result.params[1]
spread_f = log_ycyh - beta * log_ynyh - alpha
adfSpread = ADF(spread_f)
mu = np.mean(spread_f)
sd = np.std(spread_f)

#  计算交易期协整方程的残差序列（价差序列）
CoSpreadTrade = np.log(ycyh['close']) - beta * np.log(ynyh['close']) - alpha

# 绘制价格区间图（交易期）
plt.figure(figsize=(12, 6))
CoSpreadTrade.plot()
plt.title('价差序列(协整配对)', loc='center', fontsize=16)
plt.axhline(y=mu, color='black')
plt.axhline(y=mu + 0.2 * sd, color='blue', ls='-', lw=2)
plt.axhline(y=mu - 0.2 * sd, color='blue', ls='-', lw=2)
plt.axhline(y=mu + 1.5 * sd, color='green', ls='--', lw=2.5)
plt.axhline(y=mu - 1.5 * sd, color='green', ls='--', lw=2.5)
plt.axhline(y=mu + 2.5 * sd, color='red', ls='-.', lw=3)
plt.axhline(y=mu - 2.5 * sd, color='red', ls='-.', lw=3)
plt.show()

# 设置触发区间：t_0=0.2; t_1=1.5; t_2=2.5
level = (
    float('-inf'), mu - 2.5 * sd, mu - 1.5 * sd, mu - 0.2 * sd, mu + 0.2 * sd, mu + 1.5 * sd, mu + 2.5 * sd,
    float('inf'))

# 把交易期的价差序列按照触发区间标准分类【-3，+3】
prcLevel = pd.cut(CoSpreadTrade, level, labels=False) - 3


# 构造交易信号函数
def TradeSig(prcLevel):
    n = len(prcLevel)
    signal = np.zeros(n)

    for i in range(2, n):
        if prcLevel[i - 1] == 1 and prcLevel[i] == 2:  # 价差从1区上穿2区，反向建仓
            signal[i] = -2
        elif prcLevel[i - 1] == 1 and prcLevel[i] == 0:  # 价差从1区下穿0区，平仓
            signal[i] = 2
        elif prcLevel[i - 1] == 2 and prcLevel[i] == 3:  # 价差从2区上穿3区，即突破3区，平仓
            signal[i] = 3
        elif prcLevel[i - 1] == -1 and prcLevel[i] == -2:  # 价差从-1区下穿-2区，正向建仓
            signal[i] = 1
        elif prcLevel[i - 1] == -1 and prcLevel[i] == 0:  # 价差从-1区上穿0区，平仓
            signal[i] = -1
        elif prcLevel[i - 1] == -2 and prcLevel[i] == -3:  # 价差从-2区下穿-3区，即突破-3区，平仓
            signal[i] = -3
    return signal


signal = TradeSig(prcLevel)

# 设置买卖条件（信号）
position = [signal[0]]
ns = len(signal)

for i in range(1, ns):
    position.append(position[-1])
    if signal[i] == 1:
        position[i] = 1  # 价差从-1区下穿-2区，正向建仓: 买B卖A <------（价差为B-A）
    elif signal[i] == -2:
        position[i] = -1  # 价差从1区上穿2区，反向建仓：卖B买A <------（价差为B-A）
    elif signal[i] == -1 and position[i - 1] == 1:
        position[i] = 0  # 平仓
    elif signal[i] == 2 and position[i - 1] == -1:
        position[i] = 0  # 平仓
    elif signal[i] == 3:
        position[i] = 0  # 平仓
    elif signal[i] == -3:
        position[i] = 0  # 平仓

position = pd.Series(position, index=CoSpreadTrade.index)

ynyh['position'] = np.sign(position)
ycyh['position'] = -np.sign(position)
ynyh['returns'] = (np.log(ynyh['close'] / ynyh['close'].shift(1))).fillna(0)
ycyh['returns'] = (np.log(ycyh['close'] / ycyh['close'].shift(1))).fillna(0)

df = pd.DataFrame()
df["position_1"] = ynyh['position']
df['position_2'] = ynyh['position']
df['returns_1'] = ycyh['returns']
df['returns_2'] = ycyh['returns']
df['strategy_returns'] = 0.5 * (ynyh['position'].shift(1) * ynyh['returns']) + 0.5 * (
        ycyh['position'].shift(1) * ycyh['returns'])
df['cumret'] = df['strategy_returns'].dropna().cumsum().apply(np.exp)
df['rolling_max'] = df['cumret'].rolling(30, min_periods=1).max()
df['daily_drawndown'] = df['cumret'] / df['rolling_max'] - 1
df['max_drawndown'] = df['daily_drawndown'].rolling(30, min_periods=1).min()

plt.figure(figsize=(12, 6))
plt.plot(df['max_drawndown'])
plt.title('最大回撤率（30天）', loc='center', fontsize=16)
plt.show()
