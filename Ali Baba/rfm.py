import numpy as np
import pandas as pd
import datetime

#导入数据
data = pd.read_csv("D:\RFMdata.csv")

#string 转 时间格式
data['date'] = pd.to_datetime(data['trans_date'], format='%Y/%m/%d %H:%M', errors='coerce')

#设置特定的时间
tmp1 = datetime.datetime(2019, 6 , 1)

#计算时间差
data['天数'] = (data['date'] - tmp1) / np.timedelta64(1,'D')

#刷选我们需要的数据
data1 = data[(data['天数'] <= 30) & (data['天数'] >= 0)]
print(data1)
#分组计算RFM
data2 = data1.groupby('id').agg(
    {
        '天数':lambda x :x.min(),
        'id':lambda x :len(x),
        'amount':lambda x :x.sum()
    }
)

#column的名称重命名
data2.rename(columns={
    '天数':'r',
    'id':'f',
    'amount':'m'
},inplace=True)

#把index变成column
data3 = data2.reset_index()
print(data3)
#分别计算R，F，M的平均值用于用户分层
r_avg=np.average(data3['r'])
f_avg=np.average(data3['f'])
m_avg=np.average(data3['m'])

#将用户分为8类
data3.loc[(data3['r']>=r_avg)&(data3['f']>=f_avg)&(data3['m']>=m_avg),'tag']='重要价值用户——↑↑↑'
data3.loc[(data3['r']>=r_avg)&(data3['f']<f_avg)&(data3['m']>=m_avg),'tag']='重要发展用户——↑↓↑'
data3.loc[(data3['r']<r_avg)&(data3['f']>=f_avg)&(data3['m']>=m_avg),'tag']='重要保持用户——↓↑↑'
data3.loc[(data3['r']<r_avg)&(data3['f']<f_avg)&(data3['m']>=m_avg),'tag']='重要挽留用户——↓↓↑'
data3.loc[(data3['r']>=r_avg)&(data3['f']>=f_avg)&(data3['m']<m_avg),'tag']='一般价值用户——↑↑↓'
data3.loc[(data3['r']>=r_avg)&(data3['f']<f_avg)&(data3['m']<m_avg),'tag']='一般发展用户——↑↓↓'
data3.loc[(data3['r']<r_avg)&(data3['f']>=f_avg)&(data3['m']<m_avg),'tag']='一般保持用户——↓↑↓'
data3.loc[(data3['r']<r_avg)&(data3['f']<f_avg)&(data3['m']<m_avg),'tag']='一般挽留用户——↓↓↓'

#print(data3)