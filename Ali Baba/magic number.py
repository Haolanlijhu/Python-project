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
MCC_values = []
for i in range(1,11):
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for j in range(len(MG['buy_frequency'])):
        if MG.iloc[j, 1] < i & MG.iloc[j, 2] != 0:
            FN += 1
        elif MG.iloc[j, 1] >= i & MG.iloc[j, 2] != 0:
            TP += 1
        elif MG.iloc[j, 1] < i & MG.iloc[j, 2] == 0:
            TN += 1
        elif MG.iloc[j, 1] >= i & MG.iloc[j, 2] == 0:
            FP += 1
    MCC = calculate_data(TP, FP, FN, TN)
    MCC_values.append(MCC)
print(MCC_values)



















