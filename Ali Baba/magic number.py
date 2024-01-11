import os
import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt
import matplotlib.pyplot as plt
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']


def read_tablemethod(filename):
    data = pd.read_table(filename, header=0, delim_whitespace=True)
    return data


#MCC值计算公式
def calculate_data(TP, FP, FN, TN):
    numerator = (TP * TN) - (FP * FN)
    denominator = sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))
    result = numerator/denominator
    return result


#导入数据
df = read_tablemethod('D:\data.txt')


#数据清洗及筛选
df['date'] = pd.to_datetime(df['time'], dayfirst=False, errors='coerce')

#设定特定的时间
tmp1 = datetime.datetime(2014, 12 , 15)

#计算时间差
df['difference'] = (df['date'] - tmp1) / np.timedelta64(1,'D')

#筛选需要的数据
data = df[(df['behavior_type'] == 1) | (df['behavior_type'] == 4)]
data1 = data[(data['difference'] <= 3.0) & (data['difference'] >= 0)]
data2 = data1[data1['behavior_type'] == 1]
data3 = data[(data['difference'] <= 0.0) & (data['difference'] >= -3.0)]
data4 = data3[data3['behavior_type'] == 4]

#建立新的数据集
data5 = data4.groupby('user_id').agg(
    {
        'behavior_type':lambda x : len(x)
    }
)
data5.rename(columns={
    'behavior_type':'buy_frequency',
},inplace=True)
MGB = data5.reset_index()

data6 = data2.groupby('user_id').agg(
    {
        'behavior_type':lambda x : len(x)
    }
)
data6.rename(columns={
    'behavior_type':'observe_frequency',
},inplace=True)
MGO = data6.reset_index()

MG = pd.merge(MGB,MGO,how='outer',on='user_id')
MG = MG.dropna(subset=["buy_frequency"],axis=0)
MG = MG.fillna(0)
MG = MG.astype(int)
# buy_frequency是购买次数，observe_frequency是留存周期的浏览次数（！=0即表明出现过浏览）

#计算MCC
for i in range(0, 10):
    # FN <i次，留存
    FN = len(MG[(MG['购买次数'] < i) & (MG['是否次日留存'] == 1)])

    # TP >=i次，留存
    TP = len(MG[(MG['购买次数'] >= i) & (MG['是否次日留存'] == 1)])

    # TN <i次，不留存
    TN = len(MG[(MG['购买次数'] < i) & (MG['是否次日留存'] == 0)])

    # FP >=i次，不留存
    FP = len(MG[(MG['购买次数'] >= i) & (MG['是否次日留存'] == 0)])

    try:
        MCC = (TP * TN  - FP * FN) / (ma.sqrt((TP+FP) * (TP+FN) * (TN+FP) * (TN+FN)))
        print('i: %s MCC: %s' % (i, MCC))
    except Exception as e:
        print (e)
        # 如果出现异常，多半就是除数为0了。
        continue

    # 保存当前最大值
    if MCC > max_MCC:
        max_MCC = MCC
        max_i = i

print('MCC 最大为 %s 对应的i为 %d' % (max_MCC, max_i))


















