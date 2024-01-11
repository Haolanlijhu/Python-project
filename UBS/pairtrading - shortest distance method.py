import pandas as pd
import tushare as ts
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
import matplotlib
matplotlib.rcParams['axes.unicode_minus']=False

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
def SSD(priceX, priceY):
    returnX = (priceX - priceX.shift(1)) / priceX.shift(1)[1:]
    returnY = (priceY - priceY.shift(1)) / priceY.shift(1)[1:]
    standardX = (returnX + 1).cumprod()
    standardY = (returnY + 1).cumprod()
    SSD = np.sum((standardX - standardY) ** 2)
    return SSD


lst = list(data.columns)
d = dict()
for i in range(len(lst)):
    for j in range(i + 1, len(lst)):
        x = data[lst[i]]
        y = data[lst[j]]
        dis = SSD(x, y)
        d[lst[i] + '-' + lst[j]] = dis

d_sort = sorted(d.items(), key=lambda x: x[1])
print(d_sort)


# 紫金银行 和 西安银行 配对交易股票回测

# 构建类
class PairTrading:

    def SSD(self, priceX, priceY):
        returnX = (priceX - priceX.shift(1)) / priceX.shift(1)[1:]
        returnY = (priceY - priceY.shift(1)) / priceY.shift(1)[1:]
        standardX = (returnX + 1).cumprod()
        standardY = (returnY + 1).cumprod()
        SSD = np.sum((standardY - standardX) ** 2)
        return SSD

    def SSD_Spread(self, priceX, priceY):
        priceX = np.log(priceX)
        priceY = np.log(priceY)
        retx = priceX.diff()[1:]
        rety = priceY.diff()[1:]
        standardX = (1 + retx).cumprod()
        standardY = (1 + rety).cumprod()
        spread = standardY - standardX
        return spread

    def SSD_Cal_Bound(self, priceX, priceY, width):
        spread = self.SSD_Spread(priceX, priceY)
        mu = np.mean(spread)
        sd = np.std(spread)
        UpperBound = mu + width * sd
        LowerBound = mu - width * sd
        return UpperBound, LowerBound


zjyh = pro.daily(ts_code='601860.SH', start_date="20200101", end_date="20211231")
zjyh_index = pd.to_datetime(zjyh["trade_date"])
zjyh_index = zjyh.sort_index()

xayh = pro.daily(ts_code='600928.SH', start_date="20200101", end_date="20211231")
xayh_index = pd.to_datetime(xayh["trade_date"])
xayh_index = xayh.sort_index()

pt = PairTrading()

SSD_spread_trade = pt.SSD_Spread(zjyh.close, xayh.close)
mu = np.mean(SSD_spread_trade)
sd = np.std(SSD_spread_trade)

plt.figure(figsize=(12, 8))
SSD_spread_trade.plot()
plt.title('价差序列', loc='center', fontsize=16)
plt.axhline(y=mu, color='black')
plt.axhline(y=mu + 0.2 * sd, color='blue', ls='-', lw=2)
plt.axhline(y=mu - 0.2 * sd, color='blue', ls='-', lw=2)
plt.axhline(y=mu + 2.0 * sd, color='green', ls='--', lw=2.5)
plt.axhline(y=mu - 2.0 * sd, color='green', ls='--', lw=2.5)
plt.axhline(y=mu + 3.5 * sd, color='red', ls='-.', lw=3)
plt.axhline(y=mu - 3.5 * sd, color='red', ls='-.', lw=3)
plt.show()

# 设置信号触发点
level = (
    float('-inf'), mu - 3.5 * sd, mu - 2.0 * sd, mu - 0.2 * sd, mu + 0.2 * sd, mu + 2.0 * sd, mu + 3.5 * sd,
    float('inf'))
prcLevel = pd.cut(SSD_spread_trade, level, labels=False) - 3  # 剪切函数pd.cut()


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

# 计算交易信号
position = pd.Series(position, index=SSD_spread_trade.index)

# 收益率计算
zjyh['position'] = np.sign(position)
xayh['position'] = -np.sign(position)
zjyh['returns'] = (np.log(zjyh['close'] / zjyh['close'].shift(1))).fillna(0)
xayh['returns'] = (np.log(xayh['close'] / xayh['close'].shift(1))).fillna(0)

df = pd.DataFrame()
df["position_1"] = zjyh['position']
df['position_2'] = xayh['position']
df['returns_1'] = zjyh['returns']
df['returns_2'] = xayh['returns']
df['strategy_returns'] = 0.5 * (zjyh['position'].shift(1) * zjyh['returns']) + 0.5 * (
            xayh['position'].shift(1) * xayh['returns'])
df['cumret'] = df['strategy_returns'].dropna().cumsum().apply(np.exp)
df['rolling_max'] = df['cumret'].rolling(30, min_periods=1).max()
df['daily_drawndown'] = df['cumret'] / df['rolling_max'] - 1
df['max_drawndown'] = df['daily_drawndown'].rolling(30, min_periods=1).min()


plt.figure(figsize=(12, 6))
plt.plot(position)
plt.title('持仓', loc='center', fontsize=16)
plt.show()